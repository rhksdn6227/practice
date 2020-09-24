import sys, itertools
from collections import deque
import heapq
import requests
# 문제: 0,1,2번 엘리베이터: 최대 4대
url = 'http://localhost:8000'
user_key='tester'

global from_to=[[1,7],[7,13],[13,19],[19,25]]
global up=[1,1,1,1]

def start(problem_id,num_of_elevators):
    uri=url+'/start/tester/'+str(problem_id)+'/'+str(num_of_elevators)
    res=requests.post(uri)
    return res.json()

def on_calls(token):
    uri=url+'/oncalls'
    res=requests.get(uri,headers={'X-Auth-Token':token})
    return res.json()

def action(token,commands):
    uri=url+'/action'
    res=requests.post(uri,headers={'X-Auth-Token':token},json={'commands':commands})
    return res.json()

def elevator_move(enum,ride_list,elevator): #각 엘리베이터당 command 만드는 함수
    global up,from_to
    next_command={}
    next_command['elevator_id']=enum
    EXIT = False
    cnt = len(elevator['passengers'])
    for p in elevator['passengers']:
        if p['end'] == elevator['floor']: EXIT = True
        elif elevator['floor']==up[enum][1] and p['end']>up[enum][1]: EXIT=True
        elif elevator['floor']==up[enum][0] and p['end']<up[enum][0]: EXIT=True

    if elevator['status']=='OPENED': #엘리베이터 열려있음
        if EXIT: #내릴 사람이 있다
            next_command['call_ids']=[]
            for p in elevator['passengers']:
                if p['end']==elevator['floor']: next_command['call_ids'].append(p['id'])
            next_command['command']='EXIT'
        elif len(ride_list[elevator['floor']-1])!=0 and cnt<8: #태울 사람있고 가능
            next_command['call_ids']=[]
            for i in range(min(len(ride_list[elevator['floor']-1]),8-cnt)):
                next_command['call_ids'].append(ride_list[elevator['floor']-1][i]['id'])
            del ride_list[elevator['floor']-1][0:min(len(ride_list[elevator['floor']-1]),8-cnt)]
            next_command['command']='ENTER'
        else : next_command['command']='CLOSE'

    elif elevator['status'] == 'STOPPED': #엘리베이터 멈춰있음
        if len(ride_list[elevator['floor'] - 1]) != 0 and cnt < 8:  # 태울 사람있고 가능
            next_command['command']='OPEN'
        elif EXIT: next_command['command']='OPEN'
        else:
            if up[enum]==1:
                if elevator['floor']==5:
                    up[enum]=0
                    next_command['command']='DOWN'
                else : next_command['command']='UP'
            else :
                if elevator['floor']==1:
                    up[enum]=1
                    next_command['command']='UP'
                else : next_command['command']='DOWN'

    elif elevator['status']=='UPWARD':
        if len(ride_list[elevator['floor'] - 1]) != 0 and cnt < 8:  # 태울 사람있고 가능
            next_command['command']='STOP'
        elif EXIT: next_command['command']='STOP'
        else:
            if elevator['floor']==5:
                next_command['command']='STOP'
                up[enum]=0
            else :
                next_command['command']='UP'

    elif elevator['status'] == 'DOWNWARD':
        if len(ride_list[elevator['floor'] - 1]) != 0 and cnt < 8:  # 태울 사람있고 가능
            next_command['command']='STOP'
        elif EXIT:next_command['command']='STOP'
        else :
            if elevator['floor']==1:
                next_command['command']='STOP'
                up[enum]=1
            else :
                next_command['command']='DOWN'
    return next_command

    
ret = start( 1 , 4)
mytoken=ret['token']
print('my token is %s' % (mytoken))

time=0
wait_list = []
for _ in range(25):
    wait_list.append([])
while True:
    c=on_calls(mytoken)
    if c['is_end']:
        break
    elevators=c['elevators']
    calls=c['calls']

    timestamp=c['timestamp']
    for _ in range(25):
        wait_list[_].clear()
    for call in calls:
        if len(wait_list[call['start']-1])!=0 and wait_list[call['start']-1][-1]['id']==call['id']: continue
        wait_list[call['start']-1].append(call)

    
    z=[]
    for e in range(4):
        ride_list=[]
        for w in wait_list:
            if w['start']==elevators[e]['floor']:
                if w['start']==from_to[e][0]: 
                    if w['end']>from_to[e][0]:
                        ride_list.append(w)
                elif w['start']==from_to[e][1]:
                    if w['end']<from_to[e][1]:
                        ride_list.append(w)
                else: ride_list.append(w)
        z.append(elevator_move(e,ride_list,elevators[e]))

    res=action(mytoken,z)
    if res['is_end']: break
    time+=1
