# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/23
"""

import requests
import json
from urllib.parse import quote
import re
from bs4 import BeautifulSoup
from bmob import *
from time import sleep
import random
import webbrowser
import pymongo


bmob_client = Bmob("ce6a4c194e9d9f83eb884b3b161ad38e", "47129c006b23e15fcd189fec80b11915")

search_key = quote("=1&q=男生穿搭", 'utf-8')
search_url = f"https://m.weibo.cn/api/container/getIndex?containerid=100103type{search_key}&page_type=searchall"

head_string = '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="ie=edge"><title>小电影专用</title><link rel="stylesheet" href="./day10.css">
<style>
a:link {color: gray;}
a:visited {color: LightSteelBlue;}
</style>
<meta name="viewport" content="width=device-width, initial-scale=1" />
</head><body>
'''
link_string = '''<div style="width: 500pt;margin:25px 20px 20px;background-color:#c0c0c00f"><a target="_blank" style="font-size: small;" href="'''

img_src = '''"><div style="display: grid; grid-template-columns: 80pt 300pt;"><img style="grid-column: 1;width: 60pt;height: 60pt;border-radius:50%;align-self: center;justify-self: center;"src="'''
# img

username_string = '''"><div style="grid-column: 2;align-self: center"><p>'''
# {name}
fans_string = '''</p><p>粉丝：'''

# {fans}
time_string = '''</p><p>时间：'''
# {post_time}

post_string = '''</p></div></a><div style="grid-column-start: 1;grid-column-end: 3;padding-left: 10px;">'''

# {content}

comment_string = '''</div></div><div style="padding:10pt 10pt 10pt;color: slategray;font-size: small;">'''

div_end_string = '''</div></div>'''

end_string = '''</body></html>'''

source_end_string = '''</div></div></div>'''

user_data = []


def analyse_weibo_source():
    client = pymongo.MongoClient("localhost")
    db = client["uncleblue"]
    # 可以爬取的用户
    source = db["weibo_new_sources"]
    users = list(source.find({}))
    body_string = ""
    for user in users:
        user_name = user["user"]["screen_name"]
        user_id = user["user"]["id"]
        user_url = f"https://weibo.com/u/{user_id}"
        user_fans = user["user"]["followers_count"]
        user_des = user["user"]["description"]
        user_avatar = user["user"]["profile_image_url"]
        body_string = body_string + \
                      link_string + user_url + \
                      img_src + user_avatar + \
                      username_string + user_name + \
                      fans_string + str(user_fans) + \
                      post_string + "个人描述：" + user_des + "用户id:"+ str(user_id) +\
                      source_end_string

    final_html_string = head_string + body_string + end_string

    GEN_HTML = "weibo_new_source.html"
    f = open(GEN_HTML,'w')
    f.write(final_html_string)
    f.close()
    webbrowser.open(GEN_HTML, new=1)



def prepare():
    headers = {
        "accept": "application/json, text/plain, */*",
        "mweibo-pwa": "1",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; PBCM10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.96 Mobile Safari/537.36",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "referer": f"https://m.weibo.cn/search?containerid=100103type{search_key}",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    }
    cookies = requests.utils.cookiejar_from_dict({
        "SUB": "_2A25NYH8uDeRhGeNP61QX8SjIyjiIHXVuqwFmrDV6PUJbkdAKLRLgkW1NTqF6tEFqfk2_Z2fQo2a-PGC4ZirXYzf1",
        "_T_WM": "53821671377",
        "WEIBOCN_FROM": "1110005030"
    })

    s = requests.Session()
    s.cookies = cookies
    s.headers = headers
    return s


# res = requests.get(search_url, headers=headers)


def mblog_get_info(mblog):
    global body_string
    global user_data

    bid = mblog.get("bid")
    user = mblog.get("user")
    userid = None
    # 转发
    reposts_count = mblog.get('reposts_count')
    # 评论
    comments_count = mblog.get('comments_count')
    # 点赞
    attitudes_count = mblog.get('attitudes_count')
    username = None
    followers_count = None
    text = mblog.get("text")
    full_text = BeautifulSoup(text, 'html.parser').text
    avatar = None
    post_time = mblog.get('created_at')
    time_struct = time.strptime(post_time, "%a %b %d %H:%M:%S %z %Y")
    post_time = time.strftime("%Y-%m-%d %H:%M:%S %A", time_struct)

    if user:
        gender = user.get('gender')
        if gender == "f":
            return
        userid = user.get("id")
        followers_count = user.get('followers_count')
        username = user.get('screen_name')
        avatar = user.get('profile_image_url')

    final_url = f"https://weibo.com/{userid}/{bid}"



    data = {
        "user_id": userid,
        "bid": bid,
        "user_name": username,
        "followers_count": followers_count,
        "full_text": full_text,
        "comments_count": comments_count,
        "reposts_count": reposts_count,
        "attitudes_count": attitudes_count,
        "avatar": avatar,
        "post_time": post_time,
        "final_url":final_url
    }

    user_data.append(data)

    res = bmob_client.insert("Weibo_Commit", data)
    print(res.status)
    print("用户名: %s ,粉丝数 %s 有一条微博\n%s\n有 %s 个评论， %s 个转发， %s 个点赞\n发博时间：%s\n" % (
        username, followers_count, final_url, comments_count, reposts_count, attitudes_count, post_time))


def launch_request(session: requests.Session):
    global user_data
    # temp_cookies = {"MLOGIN": "1",
    #                 "XSRF-TOKEN": "1d48a6",
    #                 "M_WEIBOCN_PARAMS": "fid%3D100103type{search_key}%26oid%3D4629043193053673%26uicode%3D10000011"}

    res = session.get("https://m.weibo.cn")
    res_cookies = res.cookies
    print("当前cookies是", res_cookies)
    token = None
    for index in range(1, 30):
        sleep(random.randint(3, 10))
        for key, value in res_cookies.items():
            if key == "XSRF-TOKEN":
                token = value
        session.headers.update({"x-xsrf-token": token})
        page = f"&page={index}"
        url = search_url if index == 1 else search_url + page
        r1 = session.get(url)
        res_cookies = r1.cookies
        print("现在cookies 是", res_cookies)
        prase_response(r1)


    user_data.sort(key=lambda x:x["post_time"],reverse=True)
    body_string = ""
    for item in user_data:
        body_string = body_string + \
                      link_string + item["final_url"] + \
                      img_src + item["avatar"] + \
                      username_string + item["user_name"] + \
                      fans_string + str(item["followers_count"]) + \
                      time_string + item["post_time"] + \
                      post_string + item["full_text"] + \
                      comment_string + f"评论：{str(item['comments_count'])} 点赞：{str(item['attitudes_count'])} 转发：{str(item['reposts_count'])}" + \
                      div_end_string

    final_html_string = head_string + body_string + end_string

    GEN_HTML = "weibo.html"
    f = open(GEN_HTML,'w')
    f.write(final_html_string)
    f.close()
    webbrowser.open(GEN_HTML, new=1)


def prase_response(response: requests.Response):
    json_text = response.text
    json_dic = json.loads(json_text)

    data = json_dic.get("data")
    cards = data.get("cards")

    if isinstance(cards, list):
        for item in cards:
            card_type = item.get("card_type")
            if card_type == 9:
                mblog = item.get("mblog")
                mblog_get_info(mblog)
            elif card_type == 11:
                card_group = item.get("card_group")
                if isinstance(card_group, list):
                    for card_group_item in card_group:
                        group_mblog = card_group_item.get("mblog")
                        if group_mblog:
                            mblog_get_info(group_mblog)


if __name__ == '__main__':
    # launch_request(prepare())
    analyse_weibo_source()