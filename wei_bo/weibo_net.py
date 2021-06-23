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

my_follow_url = "https://m\.weibo\.cn/api/container/getIndex\?containerid.+selfgroupfollow.+"

follow_url = "https://m\.weibo\.cn/api/container/getIndex\?containerid.+followers.+"
fans_url = "https://m\.weibo\.cn/api/container/getIndex\?containerid.+fans.+"

app_follow_url = "https://m\.weibo\.cn/api/friendships/sortedList\?uid=.+"
app_fans_url = "https://m\.weibo\.cn/c/fans/followers\?uid=.+"

client = pymongo.MongoClient("localhost")
db = client["uncleblue"]
# 需要关注的用户
collection = db["weibo_new_users"]
app_collection = db["weibo_app_users"]
# 可以爬取的用户
source = db["weibo_new_sources"]
app_source = db["weibo_app_source"]

my_follow = db["weibo_my_follow"]

class WeiboNet(object):
    def response(self, flow: http.HTTPFlow):
        # h5 关注页面
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
                    result = re.match(
                        ".*全部关注", title if title is not None else "")
                    match = True if result is not None else False
                    ctx.log.warn("match result is %s , title is %s, result is %s" % (
                        match, title, result))

                if match:
                    itemid = card_item.get("itemid")
                    from_who = itemid.split("_")[-1]
                    card_group = card_item.get("card_group")
                    for follow in card_group:
                        if follow:
                            nickname: str = follow["user"]["screen_name"]
                            gender = follow["user"]["gender"]
                            if not (nickname.startswith("微博") or gender == "f" or ("范冰冰" in nickname) or ("刘昊然" in nickname) or ("网易" in nickname)):
                                ctx.log.warn("follow is %s" % follow["scheme"])
                                follow["from_who"] = from_who
                                if not source.find_one({"from_who": from_who, "user.id": follow["user"]["id"]}):
                                    source.insert(follow)
                                    ctx.log.info("关注保存成功")
        # H5 粉丝页面
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
                    result = re.match(
                        ".*全部粉丝", title if title is not None else "")
                    match = True if result is not None else False

                if match:
                    itemid = card_item.get("itemid")
                    from_who = itemid.split("_")[-1]
                    ctx.log.info("匹配到粉丝")
                    card_group = card_item["card_group"]
                    for fans in card_group:
                        if fans:
                            fans["from_who"] = from_who
                            nickname = fans["user"]["screen_name"]
                            fans_count = fans["user"]["followers_count"]
                            # 如果粉丝数大于1000 就标记一下
                            # 略过已经存在的和女生
                            if not (collection.find_one({"user.id": fans["user"]["id"]}) or fans["user"]["gender"] == "f" or "微博" in nickname or nickname.startswith("用户") or fans_count < 10):
                                collection.insert(fans)
                                ctx.log.info("粉丝保存成功")
                                ctx.log.info("名字：%s , 粉丝数: %s" % (
                                    fans["user"]["screen_name"], fans_count))
                                become_follow = True if fans_count > 1000 else False
                                not_exists = True if not source.find_one(
                                    {"from_who": from_who, "user.id": fans["user"]["id"]}) else False
                                if not_exists and become_follow:
                                    source.insert(fans)
                                    ctx.log.error("关注列表新增一个，粉丝：%s ，名称： %s" % (
                                        fans_count, fans["user"]["screen_name"]))
        # H5 我的关注
        elif re.match(my_follow_url,flow.request.url):
            ctx.log.error("我的穿搭 url is %s" % flow.request.url)
            text = flow.response.text
            data_j = json.loads(text)
            data = data_j.get("data")
            cards = data.get("cards")

            for card_item in cards:
                serach_btn = True
                if len(cards) > 1:
                    title = card_item.get("desc")
                    result = re.match("搜全部关注", title if title is not None else "")
                    serach_btn = True if result else False
                
                # 不是搜索按钮
                if not serach_btn:
                    card_group = card_item.get("card_group")
                    for follower in card_group:
                        user = follower.get("user")
                        if not (my_follow.find_one({"id": user["id"]}) or user["gender"] == "f"):
                            my_follow.insert_one(user)
                            ctx.log.info("记录一个大V")

        # app 关注页面
        elif re.match(app_follow_url, flow.request.url):
            ctx.log.error("folloe url is %s" % flow.request.url)
            text = flow.response.text
            data_j = json.loads(text)
            data = data_j.get("data")
            # 谁的关注
            from_who = str(data.get("uid"))
            users = data.get("users")
            for follow_item in users:
                follow_user = follow_item.get("user")
                if follow_user:
                    nickname: str = follow_user["screen_name"]
                    gender = follow_user["gender"]
                    ctx.log.warn("follow is %s" % nickname)
                    follow_user["from_who"] = from_who
                    if not app_source.find_one({"from_who": from_who, "user.id": follow_user["id"]}):
                        app_source.insert(follow_user)
                        ctx.log.info("关注保存成功")
        # app 粉丝页面
        elif re.match(app_fans_url, flow.request.url):
            ctx.log.error("fans url is %s" % flow.request.url)
            text = flow.response.text
            data_j = json.loads(text)
            fans_data = data_j.get("data")
            from_who = re.search("(\d+)",flow.request.url).group()
            fans_list = fans_data.get("list")
            all_fans = fans_list.get("users")
            for fans_user in all_fans:
                nickname = fans_user["screen_name"]
                fans_user["from_who"] = from_who
                fans_count = fans_user["followers_count"]
                # 过滤女粉和已经存在的
                if fans_count > 10000:
                    ctx.log.info("%s 太大牌了，关注不起" % nickname)
                if not (app_collection.find_one({"from_who": from_who, "id": fans_user["id"]}) or fans_user["gender"] == "f" or nickname.startswith("用户") or "微博" in nickname or fans_count < 10 or fans_count > 10000):
                    app_collection.insert(fans_user)
                    ctx.log.info("粉丝保存成功")
                    ctx.log.info("名字：%s , 粉丝数: %s" % (nickname, fans_count))
                    become_follow = True if fans_count > 1000 else False
                    not_exists = True if not app_source.find_one({"id": fans_user["id"]}) else False
                    if not_exists and become_follow:
                        app_source.insert(fans_user)
                        ctx.log.error("关注列表新增一个，粉丝：%s ，名称： %s" % (fans_count, nickname))



addons = [WeiboNet()]
