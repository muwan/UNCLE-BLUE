# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/28
记录微博爬取得数据
"""
import json
import pymongo
import re

from mitmproxy import flowfilter, http, ctx

follow_url = "https://m\.weibo\.cn/api/container/getIndex\?containerid.+followers.+"
fans_url = "https://m\.weibo\.cn/api/container/getIndex\?containerid.+fans.+"

client = pymongo.MongoClient("localhost")
db = client["uncleblue"]
# 需要关注的用户
collection = db["weibo_users"]
# 可以爬取的用户
source = db["weibo_sources"]


class WeiboNet(object):
    # def analysis_json(self, json):
    #     if isinstance(json, list) and isinstance(json[0], dict):
    #         return self.analysis_json({x: list(map(lambda k: k[x], json)) for x in json[0]})
    #     elif isinstance(json, dict):
    #         return {x: self.analysis_json(json[x]) for x in json}
    #     else:
    #         return json

    def response(self, flow: http.HTTPFlow):
        if re.match(follow_url, flow.request.url):
            ctx.log.error("folloe url is %s" % flow.request.url)
            text = flow.response.text
            data_j = json.loads(text)
            data = data_j.get("data")
            cards = data.get("cards")

            for card_item in cards:
                match = True
                if len(cards) > 1:
                    title = card_item.get("title")
                    result = re.match(".*全部关注",title if title is not None else "")
                    match = True if result is not None else False
                    ctx.log.warn("match result is %s , title is %s, result is %s" % (match, title , result))

                if match:
                    itemid = card_item.get("itemid")
                    from_who = itemid.split("_")[-1]
                    card_group = card_item.get("card_group")
                    for follow in card_group:
                        if follow:
                            nickname:str = follow["user"]["screen_name"]
                            gender = follow["user"]["gender"]
                            if not (nickname.startswith("微博") or gender == "f" or ("范冰冰" in nickname) or ("刘昊然" in nickname) or ("网易" in nickname)):
                                ctx.log.warn("follow is %s" % follow["scheme"])
                                follow["from_who"] = from_who
                                if not source.find_one({"from_who": from_who, "user.id": follow["user"]["id"]}):
                                    source.insert(follow)
                                    ctx.log.info("关注保存成功")

        elif re.match(fans_url, flow.request.url):
            ctx.log.error("fans url is %s" % flow.request.url)
            text = flow.response.text
            data_j = json.loads(text)
            data = data_j.get("data")
            cards = data.get("cards")

            for card_item in cards:
                match = True
                if len(cards) > 1:
                    title = card_item.get("title")
                    result = re.match(".*全部粉丝", title if title is not None else "")
                    match = True if result is not None else False

                if match:
                    itemid = card_item.get("itemid")
                    from_who = itemid.split("_")[-1]
                    ctx.log.info("匹配到粉丝")
                    card_group = card_item["card_group"]
                    for fans in card_group:
                        if fans:
                            fans["from_who"] = from_who
                            # 如果粉丝数大于1000 就标记一下
                            # 略过已经存在的和女生
                            if not (collection.find_one({"from_who": from_who, "user.id": fans["user"]["id"]}) or fans["user"]["gender"]=="f"):
                                collection.insert(fans)
                                ctx.log.info("粉丝保存成功")
                                fans_count = fans["user"]["followers_count"]
                                ctx.log.info("名字：%s , 粉丝数: %s" % (fans["user"]["screen_name"], fans_count))
                                become_follow = True if fans_count > 1000 else False
                                not_exists = True if not source.find_one({"from_who": from_who, "user.id": fans["user"]["id"]}) else False
                                if not_exists and become_follow :
                                    source.insert(fans)
                                    ctx.log.error("关注列表新增一个，粉丝：%s ，名称： %s" % (fans_count, fans["user"]["screen_name"]))
        else:
            ctx.log.warn("not match url is %s" % flow.request.url)


addons = [WeiboNet()]
