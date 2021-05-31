# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/2
"""
import json
import pymongo
import time

from mitmproxy import flowfilter, http, ctx

client = pymongo.MongoClient("localhost")
db = client["uncleblue"]
collection = db["aloha_follow"]
FRIENDS_LIST = db["aloha_friends"]


class Aloha:
    def __init__(self):
        flowfilter.parse('~u https://api.finka.cn/user/profile/view/')

    def request(self, flow: http.HTTPFlow):
        if flow.request.url.startswith("https://api.finka.cn/user/profile/view/v3"):
            ctx.log.warn("change flow query %s" % flow.request.query)

        elif flow.request.url.startswith("https://api.finka.cn/user/match/newest/"):
            ctx.log.info("配对参数 %s" % flow.request.query)
        # else:
        #     ctx.log.warn("url is %s" % flow.request.url)

    def response(self, flow: http.HTTPFlow):
        if flow.request.url.startswith("https://api.finka.cn/user/profile/view/v3"):
            querys = flow.request.query
            text = flow.response.text
            data = json.loads(text)
            user_f = data.get("data")
            user = user_f.get("user")
            date = time.strftime("%Y年%m月%d日", time.localtime())
            user["record_date"] = date

            if not collection.find_one({"id": user['id']}):
                collection.insert(user)
                des_list = user['profileSpecList']
                string = f"{user['name']}/".join([item['displayName']+"/" for item in des_list])
                ctx.log.warn("已关注用户 %s" % string)
        elif flow.request.url.startswith("https://api.finka.cn/user/recommend?"):
            ctx.log.warn("推荐筛选")
            # ctx.log.warn("original response is %s" % flow.response.text)

            text = flow.response.text
            recommand = json.loads(text)
            data = recommand.get("data")
            list = data.get("list")
            filter = []
            for user in list:
                user_s = user.get("user")
                age = user_s.get("age")
                if int(age) < 30 :
                    filter.append(user)
                    # ctx.log.info("当前节点 %s" % user)
                    # ctx.log.warn("filier is %s" % filter)

                else:
                    ctx.log.error("过滤30以上")
            data["list"] = filter
            recommand["data"] = data
            changed_data = json.dumps(recommand)
            flow.response.set_text(changed_data)
            # ctx.log.warn("new response is %s" % flow.response.text)

        elif flow.request.url.startswith("https://api.finka.cn/user/match/newest/v3"):
            # 抓取好友
            text = flow.response.text
            friends = json.loads(text)
            data = friends.get("data")
            list = data.get("list")
            for user in list:
                date = time.strftime("%Y年%m月%d日", time.localtime())
                if not collection.find_one({"id":user["id"]}):
                    rec = {}
                    rec["id"] = user["id"]
                    rec["name"] = user["name"]
                    rec["record_date"] = date
                    collection.insert(rec)
                    ctx.log.info("补录 %s " % (user["name"]))

                user["record_date"] = date
                if not FRIENDS_LIST.find_one({"id": user['id']}):
                    FRIENDS_LIST.insert(user)
                    ctx.log.warn("已关注用户 %s" % user["name"])

        elif flow.request.url.startswith("https://api.finka.cn/user/match/liked/v3/newest/v3"):
            text = flow.response.text
            friends = json.loads(text)
            data = friends.get("data")
            list = data.get("list")
            for user in list:
                date = time.strftime("%Y年%m月%d日", time.localtime())
                if not collection.find_one({"id":user["id"]}):
                    rec = {}
                    rec["id"] = user["id"]
                    rec["name"] = user["name"]
                    rec["record_date"] = date
                    collection.insert(rec)
                    ctx.log.info("我喜欢的 %s " % (user["name"]))


        # elif flow.request.url.startswith("https://api.finka.cn/push/log/arrive"):
        #     print(flow.response.text)
        # elif flow.request.url.startswith("https://api.finka.cn/user/match/newest/"):
        #     ctx.log.info("请求地址是：%s \n内容是：%s" % (flow.request.url, flow.response.text))


addons = [Aloha()]
