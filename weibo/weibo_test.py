# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/8
"""
import requests
import re
import pymongo
import time
from weibo import Client
import json

from bs4 import BeautifulSoup

client = pymongo.MongoClient('localhost')
db = client['uncleblue']
collection = db['weibo_daily']

all = list(collection.find({}))

replace_arr = []

for item in all:
    item.pop("_id")
    if item.get("follow_analyse"):
        analyse = item["follow_analyse"]
        replace_str = "["
        for key, value in analyse.items():
            name = f"{{\"\"sourceId\"\":\"\"{key}\"\","
            a_name = ""
            for a_key, a_value in value.items():
                a_name = a_name + f"\"\"{a_key}\"\":" + f"\"\"{a_value}\"\","
            a_name = a_name[:-1]
            name = name + a_name + "},"
            replace_str = replace_str + name
        item["follow_analyse"] = replace_str[:-1] + "]"
    replace_arr.append(item)

with open("./test_app.json", "w") as file:
    json.dump(replace_arr, file)

print(replace_arr)