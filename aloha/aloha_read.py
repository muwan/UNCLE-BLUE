# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/13
"""
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from multiprocessing import Process
import pymongo

import logging

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)

connect_device(
    "android://127.0.0.1:5037/4f74b1cc?cap_method=MINICAP_STREAM&&ori_method=MINICAPORI&&touch_method=MINITOUCH")
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
s_width,s_height = poco.get_screen_size()


def start():
    start_app("com.cupidapp.live")

    while True:
        sleep(2)
        froz_poco = poco.freeze()
        chat_list = poco("com.cupidapp.live:id/sessionUserAvatarImageView")
        sleep(1)
        if chat_list.exists():
            for chat in chat_list:
                if chat.exists():
                    watcher()
                    chat.click()
                    sleep(1)
                    back = poco("com.cupidapp.live:id/back_view")
                    if back.exists():
                        watcher()
                        back.click()
                        sleep(1)

        swipe((s_width * 0.5, s_height * 0.9), vector=[0, -1])




def watcher():
    print("-----------------------弹窗检测启动")
    # 目标元素 com.cupidapp.live:id/messageSend

    find_element = poco("com.cupidapp.live:id/closeImageView")
    if find_element.exists():
        find_element.click()
        print("发现元素")
    else:
        print("-----------------------等待0.5秒")
        sleep(0.5)


if __name__ == '__main__':
    start()