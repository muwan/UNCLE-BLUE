# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/2
"""
import json
import pymongo

from mitmproxy import flowfilter, http, ctx

client = pymongo.MongoClient("localhost")
db = client["uncleblue"]
collection = db["aloha_follow"]


class Aloha:
    def __init__(self):
        flowfilter.parse('~u https://api.finka.cn/user/profile/view/')
        self.count = 0
        self.group_id = ""
        self.group_name = ""

    def request(self, flow: http.HTTPFlow):
        if flow.request.url.startswith("https://api.finka.cn/user/profile/view/v3"):
            ctx.log.warn("change flow query %s" % flow.request.query)
        # else:
        #     ctx.log.warn("url is %s" % flow.request.url)

    def response(self, flow: http.HTTPFlow):
        if flow.request.url.startswith("https://api.finka.cn/user/profile/view/v3"):
            text = flow.response.text
            data = json.loads(text)
            user_f = data.get("data")
            user = user_f.get("user")
            if not collection.find_one({"id": user['id']}):
                collection.insert(user)
                des_list = user['profileSpecList']
                string = f"{user['name']}/".join([item['displayName']+"/" for item in des_list])
                ctx.log.warn("已关注用户 %s" % string)

addons = [Aloha()]
