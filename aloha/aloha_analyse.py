# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/5
"""
import json
import pymongo
import time


client = pymongo.MongoClient("localhost")
db = client["uncleblue"]
FOLLOW_COLLECTION = db["aloha_follow"]
FRIENDS_LIST = db["aloha_friends"]
ANALYSE = db["aloha_analyse"]

friends = list(FRIENDS_LIST.find({}))

follows = list(FOLLOW_COLLECTION.find({}))

dic = {}

for user in follows:
    date = user["record_date"]
    data_dic = dic[date] if dic.get(date) else {"followed":0,"fans":0}
    if data_dic["followed"] == 0:
        total = FOLLOW_COLLECTION.count_documents({"record_date": date})
        data_dic["followed"] = total
    if FRIENDS_LIST.find_one({"id":user["id"]}):
        data_dic["fans"] = data_dic["fans"] + 1
        print("%s 已关注" % (user["name"]))
    dic[date] = data_dic

print(dic)

