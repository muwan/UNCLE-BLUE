# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/5/19
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
screenWidth, screenHeight = poco.get_screen_size()


def start():
    start_app("com.cupidapp.live")

    while True:
        sleep(1)
        frozen = poco.freeze()
        items = frozen("com.cupidapp.live:id/userListLinearLayout")

        for user in items:
            sleep(1)
            match_tag = user.offspring("com.cupidapp.live:id/userMatchedTextView")
            if not match_tag.exists():
                user.click()
                print("进详情")
                sleep(1)
                watcher()
                swipe((screenWidth * 0.5, screenHeight * 0.7), vector=[0, -0.5], duration=1)
                follow_btn = poco("com.cupidapp.live:id/followImageView")
                if follow_btn.exists():
                    post_count = poco("com.cupidapp.live:id/postCountTitleTextView")
                    if post_count.exists():
                        count_text = post_count.get_text()
                        if count_text != "暂无动态":
                            sleep(1)
                            like_posts()
                    watcher()
                    # 先取关
                    follow_btn.click()
                    sleep(1)
                    # 再关注
                    follow_btn.click()
                    back = poco("com.cupidapp.live:id/leftImageView")
                    if back.exists():
                        watcher()
                        back.click()

        swipe((screenWidth * 0.5, screenHeight * 0.9), vector=[0, 1], duration=1)




def like_posts():
    post_list = poco("com.cupidapp.live:id/profilePostCoverImageView")
    if len(post_list) > 0:
        print("进动态点赞")
        if post_list[0].exists():
            post_list[0].click()
            sleep(1)
            swipe((screenWidth * 0.5, screenHeight * 0.5), vector=[0, -0.5], duration=1)
            detail_list = poco("com.cupidapp.live:id/feedRecyclerView").children()
            if detail_list.exists():
                detail_item = detail_list[0]
                if detail_item.exists():
                    like = detail_item.offspring("com.cupidapp.live:id/feedPraiseButton")
                    if like.exists():
                        like.click()
                        print("点了个赞")
                back = poco("com.cupidapp.live:id/leftImageView")
                if back.exists():
                    watcher()
                    back.click()


def watcher():
    print("-----------------------弹窗检测启动")
    # 目标元素 com.cupidapp.live:id/messageSend
    find_element = poco("com.cupidapp.live:id/closeImageView")
    if find_element.exists():
        find_element.click()
        print("发现元素")
    else:
        print("-----------------------等待0.5秒，当前时间：", time.strftime("%H:%M:%S", time.localtime()))
        time.sleep(0.5)

if __name__ == '__main__':
    start()