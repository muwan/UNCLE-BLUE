# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/23
"""
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


import logging
import re
import random

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)


class XHSUnfollow(object):
    def __init__(self):
        connect_device(
            "android://127.0.0.1:5037/DRGGAM0850527807?cap_method=MINICAP_STREAM&&ori_method=MINICAPORI&&touch_method=MINITOUCH")
        self.poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        self.screenWidth, self.screenHeight = self.poco.get_screen_size()
        self.follow()

    def sleep_radom(self):
        sleep(random.randint(1,3))

    def follow(self):
        start_app("com.xingin.xhs")
        total = 500
        while total > 1:
            self.sleep_radom()
            state = self.poco.freeze()
            fans_list = state("com.xingin.xhs:id/cx1")
            self.sleep_radom()
            for item in fans_list.children():
                self.sleep_radom()
                follow_state = item.offspring("com.xingin.xhs:id/ex1")
                if follow_state.exists():
                    state_str = follow_state.get_text()
                    if state_str == "互相关注":
                        continue
                    
                item.click()
                self.sleep_radom()

                post_frame = self.poco(type="androidx.recyclerview.widget.RecyclerView")
                self.sleep_radom()
                if post_frame.exists():
                    if post_frame[-1].children().exists():
                        post = post_frame[-1].children()[-1]
                        if post.exists():
                            post_name = post.get_name()
                            if not re.match(r"^com.xingin.xhs:id.*", post_name):
                                message_btn = self.poco("com.xingin.xhs:id/f21")
                                username = ""
                                user_name_btn = self.poco("com.xingin.xhs:id/de8")
                                if user_name_btn.exists():
                                    username = user_name_btn.get_text()

                                if message_btn.exists():
                                    if message_btn.get_text() == "发消息":
                                        unfollow_btn = self.poco("com.xingin.xhs:id/f22")
                                        if unfollow_btn.exists():
                                            self.sleep_radom()
                                            unfollow_btn.click()
                                            self.sleep_radom()
                                            self.poco("android:id/button1").click()
                                            self.sleep_radom()
                                            print("已经取关 ", username)
                                            total = total - 1
                                    else:
                                        print("没有操作 %s 了，跳过" % username)
                            else:
                                print("用户发过帖子")

                if self.poco("com.xingin.xhs:id/ddi").exists():
                    self.poco("com.xingin.xhs:id/ddi").click()
                print("下一个")


            swipe((self.screenWidth * 0.5, self.screenHeight * 0.2), vector=[0, 1], duration=random.randint(1,3))
            self.sleep_radom()




if __name__ == '__main__':
    XHSUnfollow()