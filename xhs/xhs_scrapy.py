# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/10
"""
import json
import pymongo
import time

from mitmproxy import flowfilter, http, ctx

client = pymongo.MongoClient("localhost")
db = client["uncleblue"]
collection = db["xhs_user"]


class XHS:
    def request(self, flow: http.HTTPFlow):
        if flow.request.url.startswith("https://edith.xiaohongshu.com/api/sns/v1/user/followers?user_id"):
            ctx.log.warn("小红书查询用户数 %s" % flow.request.query)

        elif flow.request.url.startswith("https://api.finka.cn/user/match/newest/"):
            ctx.log.info("配对参数 %s" % flow.request.query)
        # else:
        #     ctx.log.warn("url is %s" % flow.request.url)

    def response(self, flow: http.HTTPFlow):
        if flow.request.url.startswith("https://edith.xiaohongshu.com/api/sns/v1/user/followers?user_id"):
            text = flow.response.text
            data = json.loads(text)
            user_f = data.get("data")
            users = user_f.get("users")
            for user in users:
                date = time.strftime("%Y%m%d", time.localtime())
                user["record_date"] = date

                if not collection.find_one({"userid": user['userid']}):
                    collection.insert(user)
                    des_list = user['desc']
                    string = f"{user['nickname']}/{des_list}"
                    ctx.log.warn("已关注用户 %s" % string)


addons = [XHS()]
