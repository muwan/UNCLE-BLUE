# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/2
"""
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from multiprocessing import Process
import pymongo

import logging

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)


# poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
# screenWidth, screenHeight = poco.get_screen_size()


# count = 0
# for _ in range(0, 500):
#     poco("com.cupidapp.live:id/followButton").click()
#     count += 1
#     print("已经关注：%s 人" % count)
#     sleep(1)


class Aloha(object):
    def __init__(self):
        connect_device(
            "android://127.0.0.1:5037/4f74b1cc?cap_method=MINICAP_STREAM&&ori_method=MINICAPORI&&touch_method=MINITOUCH")
        self.poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        self.screenWidth, self.screenHeight = self.poco.get_screen_size()
        self.total = 0
        self.loop_users()

    def like_people(self):
        poco_like = self.poco("com.cupidapp.live:id/followImageView")
        if poco_like.exists():
            self.watcher()
            poco_like.click()
            self.total += 1
            print("喜欢了 %s 人" % self.total)
        back = self.poco("com.cupidapp.live:id/leftImageView")
        if back.exists():
            self.watcher()
            back.click()

    def like_post(self):
        post_list = self.poco("com.cupidapp.live:id/profilePostCoverImageView")
        if post_list.exists():
            self.watcher()
            post_list[0].click()
            sleep(1)
            # swipe((self.screenWidth * 0.5, self.screenHeight * 0.5), vector=[0, -0.5], duration=1)
            detail_list = self.poco("com.cupidapp.live:id/feedRecyclerView").children()
            if detail_list.__len__() > 0:
                detail_item = detail_list[0]
                like = detail_item.offspring("com.cupidapp.live:id/feedPraiseButton")
                if like.exists():
                    self.watcher()
                    like.click()
                    print("点赞一条动态")
                back = self.poco("com.cupidapp.live:id/leftImageView")
                if back.exists():
                    self.watcher()
                    back.click()

    def loop_users(self):
        start_app("com.cupidapp.live")
        self.watcher()
        while True:
            # self.some_one_like_you()
            if exists(Template(r"tpl1617539799242.png", record_pos=(0.388, -0.533), resolution=(1080, 2340))):
                self.watcher()
                touch(Template(r"tpl1617539799242.png", record_pos=(0.388, -0.533), resolution=(1080, 2340)))
                self.watcher()
                swipe((self.screenWidth * 0.5, self.screenHeight * 0.7), vector=[0, -0.5], duration=1)
                count = self.poco("com.cupidapp.live:id/postCountTitleTextView")
                post_count = ""
                if count.exists():
                    post_count = count.get_text()

                dest = self.poco("com.cupidapp.live:id/profileDescriptionTextView")
                post_dest = ""
                if dest.exists():
                    post_dest = dest.get_text()

                print("pos_count:%s,pos_des is :%s" % (post_count, post_dest))
                desc_list = self.poco("com.cupidapp.live:id/specContentTextView")
                if desc_list.exists():
                    for item in desc_list:
                        print(item.get_text())

                if post_count != "暂无动态":
                    self.like_post()
                # 点击喜欢
                self.like_people()
            else:
                self.watcher()

            back = self.poco("com.cupidapp.live:id/leftImageView")
            if back.exists():
                self.watcher()
                back.click()
            if self.total > 499:
                break


    def watcher(self):
        print("-----------------------弹窗检测启动")
        # 目标元素 com.cupidapp.live:id/messageSend
        find_element = self.poco("com.cupidapp.live:id/closeImageView")
        if find_element.exists():
            find_element.click()
            print("发现元素")
        else:
            print("-----------------------等待0.5秒，当前时间：",time.strftime("%H:%M:%S", time.localtime()))
            time.sleep(0.5)

        # 定义子线程: 循环查找目标元素
        # p = Process(target=self.loop_watcher, args=(find_element,))
        # p.start()

    def skip_old(self):
        pass

def change_date():

    client = pymongo.MongoClient("localhost")
    db = client["uncleblue"]
    collection = db["aloha_follow"]

    datas = collection.find({"record_date":None})
    for data in datas:
        date = time.strftime("%Y年%m月%d日", time.localtime())
        data["record_date"] = date
        collection.update_one({"_id":data["_id"]}, {"$set": data})
    # pass

if __name__ == '__main__':
    # change_date()
    aloha = Aloha()

