import sys, itertools
from collections import deque
import heapq
import requests
# 문제: 0,1,2번 엘리베이터: 최대 4대
url = 'http://localhost:8000'
user_key='tester'

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
    ret=requests.post(uri,headers={'X-Auth-Token':token},json={'commands':commands})
    return ret.json()

ret = start( 0 , 1)
mytoken=ret['token']
print('my token is %s' % (mytoken))

time=0
wait_list = []
up=1
for _ in range(5):
    wait_list.append([])
while True:
    c=on_calls(mytoken)
    if c['is_end']:
        break
    next_command={}
    next_command['elevator_id']=0
    elevators=c['elevators']
    elevator=elevators[0]
    calls=c['calls']

    timestamp=c['timestamp']
    for _ in range(5):
        wait_list[_].clear()
    for call in calls:
        if len(wait_list[call['start']-1])!=0 and wait_list[call['start']-1][-1]['id']==call['id']: continue
        wait_list[call['start']-1].append(call)

    EXIT = False
    cnt = len(elevator['passengers'])
    for p in elevator['passengers']:
        if p['end'] == elevator['floor']: EXIT = True

    if elevator['status']=='OPENED': #엘리베이터 열려있음
        if EXIT: #내릴 사람이 있다
            next_command['call_ids']=[]
            for p in elevator['passengers']:
                if p['end']==elevator['floor']: next_command['call_ids'].append(p['id'])
            next_command['command']='EXIT'
        elif len(wait_list[elevator['floor']-1])!=0 and cnt<8: #태울 사람있고 가능
            next_command['call_ids']=[]
            for i in range(min(len(wait_list[elevator['floor']-1]),8-cnt)):
                next_command['call_ids'].append(wait_list[elevator['floor']-1][i]['id'])
            del wait_list[elevator['floor']-1][0:min(len(wait_list[elevator['floor']-1]),8-cnt)]
            next_command['command']='ENTER'
        else : next_command['command']='CLOSE'

    elif elevator['status'] == 'STOPPED': #엘리베이터 멈춰있음
        if len(wait_list[elevator['floor'] - 1]) != 0 and cnt < 8:  # 태울 사람있고 가능
            next_command['command']='OPEN'
        elif EXIT: next_command['command']='OPEN'
        else:
            if up==1:
                if elevator['floor']==5:
                    up=0
                    next_command['command']='DOWN'
                else : next_command['command']='UP'
            else :
                if elevator['floor']==1:
                    up=1
                    next_command['command']='UP'
                else : next_command['command']='DOWN'

    elif elevator['status']=='UPWARD':
        if len(wait_list[elevator['floor'] - 1]) != 0 and cnt < 8:  # 태울 사람있고 가능
            next_command['command']='STOP'
        elif EXIT: next_command['command']='STOP'
        else:
            if elevator['floor']==5:
                next_command['command']='STOP'
                up=0
            else :
                next_command['command']='UP'

    elif elevator['status'] == 'DOWNWARD':
        if len(wait_list[elevator['floor'] - 1]) != 0 and cnt < 8:  # 태울 사람있고 가능
            next_command['command']='STOP'
        elif EXIT:next_command['command']='STOP'
        else :
            if elevator['floor']==1:
                next_command['command']='STOP'
                up=1
            else :
                next_command['command']='DOWN'
    z=[]
    z.append(next_command)
    #print(z)
    #print(elevator['floor'],elevator['status'])

    res=action(mytoken,z)
    if res['is_end']: break
    time+=1
