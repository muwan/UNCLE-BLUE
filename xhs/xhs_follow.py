# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/10
"""
from airtest.core.api import *
from airtest.aircv import *
from pathlib import Path
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


import logging
import re
import pymongo

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)

client = pymongo.MongoClient("localhost")
db = client["uncleblue"]
collection = db["xhs_user"]


class XHSFollow(object):
    def __init__(self):
        connect_device(
            "android://127.0.0.1:5037/DRGGAM0850527807?cap_method=MINICAP_STREAM&&ori_method=MINICAPORI&&touch_method=MINITOUCH")
        self.poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        self.screenWidth, self.screenHeight = self.poco.get_screen_size()
        self.follow()

    def follow(self):
        start_app("com.xingin.xhs")
        temp_name_list = []
        while True:
            sleep(1)
            state = self.poco.freeze()
            fans_list = state(type="androidx.recyclerview.widget.RecyclerView")
            sleep(1)
            user_name_list = []
            for item in fans_list.children():
                sleep(1)
                item.click()
                sleep(1)

                post_frame = self.poco(type="androidx.recyclerview.widget.RecyclerView")
                sleep(1)
                if post_frame.exists():
                    if post_frame[-1].children().exists():
                        post = post_frame[-1].children()[0]
                        if post.exists():
                            post_name = post.get_name()
                            if re.match(r"^com.xingin.xhs:id.*", post_name):
                                sleep(1)
                                like = post.offspring("com.xingin.xhs:id/afi")
                                if like.exists():
                                    like.click()
                                print("已经点赞")
                            else:
                                print("用户没有发过帖子")

                message_btn = self.poco("com.xingin.xhs:id/cav")
                username = ""
                user_name_btn = self.poco("com.xingin.xhs:id/bhz")
                if user_name_btn.exists():
                    username = user_name_btn.get_text()
                    user_name_list.append(username)

                if message_btn.exists():
                    if message_btn.get_text()=="关注":
                        message_btn.click()
                        print("已经关注 ", username)
                    else:
                        print("已经关注过 %s 了，跳过" % username)

                sleep(1)
                if self.poco("com.xingin.xhs:id/bha").exists():
                    self.poco("com.xingin.xhs:id/bha").click()
                print("下一个")

            date = time.strftime("%Y%m%d", time.localtime())
            total = collection.count_documents({"record_date":date})
            if user_name_list == temp_name_list:
                print("-----------------\n到头了\n-----------------")
                break
            elif total > 500:
                print("今天任务完成了")
                break
            else:
                temp_name_list = user_name_list
                swipe((self.screenWidth * 0.5, self.screenHeight * 0.8), vector=[0, -1], duration=1)
                sleep(3)


if __name__ == '__main__':
    XHSFollow()