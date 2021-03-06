# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/3
"""

import requests
import re
import pymongo
import time
from weibo import Client
from bmob import *
from bs4 import BeautifulSoup

client = pymongo.MongoClient('localhost')
db = client['uncleblue']
collection = db['weibo_daily']

b = Bmob("ce6a4c194e9d9f83eb884b3b161ad38e", "47129c006b23e15fcd189fec80b11915")

# souece = db["weibo_sources"]
# datas = list(souece.find({"user.followers_count":{"$gte":10000}},{"user.id":1,"user.screen_name":1,"_id":0}))
#
# links = [(f"https://weibo.com/u/{user['user']['id']}?is_all=1",user["user"]["screen_name"]) for user in datas]
# print(links)


headers = {
    "Cookie": "_T_WM=1e0eb414a5ffae154ce6143d1bd12a5c; SUB=_2A25NhizQDeRhGedJ7VYR8SbKzzuIHXVuiLSYrDV6PUJbktAfLXfMkW1NUcNerGiSSYHjSjoFX98s_6tt-Kc4hssW; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWuOP1L8pkhD2LfgsKMDFKr5NHD95QpS0qXeh2RSoBNWs4Dqcj_i--ciK.RiKLsi--ciKy8i-2Ei--RiK.0iKL2i--fiKysiK.Xi--fiKysiK.X; SSOLoginState=1619156096",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "dnt": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://passport.weibo.cn/",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,zh-HK;q=0.6",
}

url = "https://weibo.cn/"

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.content, 'html.parser')
datas = soup.find("div", class_="tip2")
a_links = datas.find_all("a")
followers = datas.find(href="/1764018647/follow").getText()
follower_num = re.search(r"(\d+)", followers).group()

fans = datas.find(href="/1764018647/fans").getText()
fans_num = re.search(r"(\d+)", fans).group()

date = time.strftime("%Y%m%d", time.localtime())
data = {
    "date": date,
    "followers": follower_num,
    "fans": fans_num
}
b.insert("weibo_analyse", data)

if not collection.find_one({"date": date}):
    collection.insert_one(data)
    # insert_data = {
    #     "date": date,
    #     "followers": follower_num,
    #     "fans": fans_num
    # }
    b.insert("weibo_analyse", data)

print("%s ??????????????????%s ??????????????????%s ???" % (time.strftime("%Y???%m???%d???", time.localtime()), fans_num, follower_num))
