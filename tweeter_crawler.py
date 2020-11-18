# -*- coding: utf-8 -*-
import tweepy
import csv
import os

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

location = "%s,%s,%s" % ("35.95", "128.25", "1000km")

keyword = "유출확인 OR 유출조회 OR 회생작업 OR 여권위조 OR 운전면허증위조"

#저장할 csv 파일 오픈
f = open('other_spam.csv', 'wt', encoding='utf-8')
writer = csv.writer(f)

# twitter 검색 cursor 선언

cursor = tweepy.Cursor(api.search,
                       q=keyword,
                       since='2015-01-01',
                       count=100,  # 페이지당 반환할 트위터 수 최대 100
                       geocode=location,
                       include_entities=True)
for i, tweet in enumerate(cursor.items()):
    print("{}: {}".format(i, tweet.text))
    writer.writerow([i,tweet.text,0])
    if i==1000: break
f.close()
