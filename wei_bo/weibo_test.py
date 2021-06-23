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
from time import sleep
import random

from bs4 import BeautifulSoup

CLIENT = pymongo.MongoClient('localhost')
DB = CLIENT['uncleblue']
SOURCE_COLLECTION = DB["weibo_my_follow"]
USER_COLLECTION = DB['weibo_new_users']

SOURCE_NEW_COLLECTION = DB["weibo_new_sources"]

source_id = 0

source_url = f"https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_"

def prepare(userid):
    headers = {
        "accept": "application/json, text/plain, */*",
        "mweibo-pwa": "1",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile":"?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; PBCM10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.96 Mobile Safari/537.36",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": f"https://m.weibo.cn/p/index?containerid=231051_-_fans_-_{userid}",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    }


    cookies = requests.utils.cookiejar_from_dict({
        "SUB": "_2A25NYH8uDeRhGeNP61QX8SjIyjiIHXVuqwFmrDV6PUJbkdAKLRLgkW1NTqF6tEFqfk2_Z2fQo2a-PGC4ZirXYzf1",
        "_T_WM": "37911814169",
        "WEIBOCN_FROM": "1110005030",
        "MLOGIN":"1",
        "M_WEIBOCN_PARAMS":f"luicode%3D10000011%26lfid%3D231051_-_fans_-_{userid}%26fid%3D231051_-_fans_-_{userid}%26uicode%3D10000011",
    })

    s = requests.Session()
    s.cookies = cookies
    s.headers = headers
    return s

def get_source_user():
    global source_id
    # 3980477211
    users = list(SOURCE_COLLECTION.find({}))

    one = SOURCE_COLLECTION.find_one({"id":6037660116})
    index = users.index(one)
    for item in users[index:index+5]:
        source_id = item["id"]
        userid = str(source_id)
        session = prepare(userid)
        # 初始请求，如果有分页，就进行下一个请求
        url = source_url+userid
        launch_request(session,url,userid)



def launch_request(session: requests.Session, url, userid):
    response_data = session.get(url)
    res_cookies = response_data.cookies
    print("微博请求链接 ", url)
    token = None
    sleep(random.randint(3, 10))
    for key, value in res_cookies.items():
        if key == "XSRF-TOKEN":
            token = value
    session.headers.update({"x-xsrf-token": token})
    sinceid = prase_response(response_data)
    if sinceid:
        page_url = source_url + userid + f"&since_id={sinceid}"
        launch_request(session, page_url,userid)


def prase_response(response_data):
    json_text = response_data.text
    json_dic = json.loads(json_text)

    data = json_dic.get("data")
    cards = data.get("cards")
    if isinstance(cards, list):
        for item in cards:
            match = True
            if len(cards) > 1:
                title = item.get("title")
                result = re.match(
                    ".*全部粉丝", title if title is not None else "")
                match = True if result is not None else False

            if match:
                card_group = item.get("card_group")
                if isinstance(card_group, list):
                    for card_group_item in card_group:
                        card_group_item["from_who"] = str(source_id)
                        user = card_group_item.get("user")
                        userid = user.get("id")
                        nickname = user.get('screen_name')
                        fans_count = user.get('followers_count')
                        if not (USER_COLLECTION.find_one({"user.id":userid}) or user["gender"] == "f" or "微博" in nickname or nickname.startswith("用户") or fans_count < 10):
                            USER_COLLECTION.insert_one(card_group_item)
                            print("已保存 %s 粉丝数 %s ..." % (nickname,fans_count))
                            not_exists = True if not SOURCE_NEW_COLLECTION.find_one(
                                {"user.id": userid}) else False
                            if not_exists and fans_count > 1000 and fans_count < 100000:
                                SOURCE_NEW_COLLECTION.insert_one(card_group_item)
                                print("资源池中加入新血液...")
                        else:
                            print("过滤 %s 粉丝数 %s ..." % (nickname,fans_count))

    cardlistInfo = data.get("cardlistInfo")
    if cardlistInfo:
        since_id = cardlistInfo.get('since_id')

        return since_id
    else:
        return None

if __name__ == '__main__':
    get_source_user()