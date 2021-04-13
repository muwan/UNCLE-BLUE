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

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)

class XHSFollow(object):
    def __init__(self):
        connect_device(
            "android://127.0.0.1:5037/DRGGAM0850527807?cap_method=MINICAP_STREAM&&ori_method=MINICAPORI&&touch_method=MINITOUCH")
        self.poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

    def follow(self):
        start_app("com.xingin.xhs")

        while True:
            sleep(1)
            state = self.poco.freeze()
            fans_list = state(type="androidx.recyclerview.widget.RecyclerView")
            sleep(1)
            for item in fans_list.children():
                sleep(1)
                item.click()
                sleep(1)

                post_frame = self.poco(type="androidx.recyclerview.widget.RecyclerView")
                post = post_frame[1].children()[0]
                if post.exists():
                    post_name = post.get_name()
                    if re.match(r"^com.xingin.xhs:id.*", post_name):
                        sleep(1)
                        post.child("com.xingin.xhs:id/bak").click()
                        print("已经点赞")
                    else:
                        print("没用发过帖子")

                message_btn = self.poco(textMatches="^消息$")
                if message_btn.exists():
                    message_btn.click()

                    user_name_btn = self.poco("com.xingin.xhs:id/cpm")
                    username = ""
                    if user_name_btn.exists():
                        username = user_name_btn.get_text()
                    print("已经关注 ", username)

                sleep(1)
                print(item.get_name())

                keyevent("BACK")


if __name__ == '__main__':
    XHSFollow()