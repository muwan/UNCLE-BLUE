# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/7
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

def start():
    


    start_app("com.cupidapp.live")

    count = 100
    while True:
        first_item = poco("android.widget.LinearLayout").offspring("com.cupidapp.live:id/feedRecyclerView").child(
            "android.widget.RelativeLayout")[0].offspring("com.cupidapp.live:id/feedShareButton")

        if first_item:

            first_item.click()
        else:
            watcher()
            poco("android.widget.LinearLayout").offspring("com.cupidapp.live:id/feedRecyclerView").child(
                "android.widget.RelativeLayout")[1].offspring("com.cupidapp.live:id/feedShareButton").click()

        sleep(0.5)
        watcher()
        poco(text="删除内容").click()
        sleep(0.5)
        watcher()
        poco("android:id/button1").click()
        sleep(2)
        count -= 1
        if count == 0:
            break


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