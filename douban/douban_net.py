# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/2
"""
import os
import sys
import json
import pymongo

from mitmproxy import flowfilter, http, ctx

client = pymongo.MongoClient("localhost")
db = client["uncleblue"]
collection = db["douban"]


class Douban:
    def __init__(self):
        flowfilter.parse('~u https://frodo.douban.com/api/v2/group/')
        self.count = 0
        self.group_id = ""
        self.group_name = ""

    def request(self, flow: http.HTTPFlow):
        if flow.request.url.startswith("https://frodo.douban.com/api/v2/group/"):
            if flow.request.url.__contains__("/members?"):
                url_list = flow.request.url.split("/")
                group_id = url_list[-2]
                if self.group_id != group_id:
                    self.group_id = group_id
                    self.count = 0
                # flow.request.query.set_all("count", ["30"])
                # flow.request.query.set_all("start", [self.count])

                ctx.log.warn("change flow query %s" % flow.request.query)

    def response(self, flow: http.HTTPFlow):
        if flow.request.url.startswith("https://frodo.douban.com/api/v2/group/"):
            if flow.request.url.__contains__("/members?"):
                text = flow.response.text
                data = json.loads(text)
                user_list = data.get("members")
                count = data.get("count")
                self.count = self.count + count
                for user in user_list:
                    user["scrapy_from_group"] = self.group_id
                    user["group_name"] = self.group_name
                    if not collection.find_one({"id": user['id'], "scrapy_from_group": self.group_id}):
                        collection.insert(user)
            elif flow.request.url.__contains__("?access="):
                group = db["groups"]
                group_info = flow.response.text
                group_data = json.loads(group_info)
                self.group_name = group_data.get("name")
                if not group.find_one({"id": group_data['id']}):
                    group.insert(group_data)
                ctx.log.info("小组信息：%s" % self.group_name)

            # ctx.log.warn("response %s" % text)


addons = [Douban()]
