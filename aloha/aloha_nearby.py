# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/6/1
"""

from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import pymongo

import logging
import re

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)

connect_device(
    "android://127.0.0.1:5037/4f74b1cc?cap_method=MINICAP_STREAM&&ori_method=MINICAPORI&&touch_method=MINITOUCH")
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
screenWidth, screenHeight = poco.get_screen_size()

client = pymongo.MongoClient("localhost")
db = client["uncleblue"]
collection = db["aloha_follow"]

date = time.strftime("%Y年%m月%d日", time.localtime())
total = collection.count_documents({"record_date":date})

def start():
    global total
    start_app("com.cupidapp.live")
    watcher()
    print("开始---")
    nearby = poco(text="附近")
    if nearby.exists():
        nearby.click()
        while True:
            total = collection.count_documents({"record_date": date})
            if total > 800:
                print("今天的关注先到这里吧，再见")
                break
            sleep(1)
            frozen = poco.freeze()
            # 当前列表附近的人
            items = frozen("com.cupidapp.live:id/userAvatarView")
            if items.exists():
                for user in items:
                    watcher()
                    print("选择附近列表")
                    user.click()
                    sleep(1)
                    # 年龄是否大于30岁
                    ageItem = poco("com.cupidapp.live:id/userAgeAndInfoTextView")
                    if ageItem.exists():
                        age = ageItem.get_text()
                        match = re.match("^(\d.)", age)
                        match_age = None
                        if match:
                            match_age = match.group(0)
                        if int(match_age) > 30:
                            print("%s 年龄不符合，再见👋"%age)
                            watcher()
                            print("年龄不符合返回")
                            keyevent('BACK')
                        else:
                            startChat = poco("com.cupidapp.live:id/startChatButton")
                            cancleBtn = poco("com.cupidapp.live:id/cancelFollowButton")
                            if startChat.exists() or cancleBtn.exists():
                                print("----------已经关注过了，下一个----------")
                                watcher()
                                print("已经关注返回")
                                keyevent('BACK')
                            else:
                                user_detail()

            swipe((screenWidth * 0.5, screenHeight*0.9), vector=[0, -1.3])
    else:
        start()

def user_detail():
    # 右上角更多
    info_btn = poco("com.cupidapp.live:id/arrowImageView")
    if info_btn.exists():
        watcher()
        print("查看个人详情")
        info_btn.click()
        sleep(1)
        swipe((screenWidth * 0.5, screenHeight * 0.7), vector=[0, -0.5], duration=1)
        count = poco("com.cupidapp.live:id/postCountTitleTextView")
        post_count = ""
        if count.exists():
            post_count = count.get_text()

        dest = poco("com.cupidapp.live:id/profileDescriptionTextView")
        post_dest = ""
        if dest.exists():
            post_dest = dest.get_text()

        print("pos_count:%s,pos_des is :%s" % (post_count, post_dest))
        desc_list = poco("com.cupidapp.live:id/specContentTextView")
        if len(desc_list) > 0:
            for item in desc_list:
                print(item.get_text())

        if post_count != "暂无动态":
            like_post()
        # 点击喜欢
        like_people()
        watcher()
        print("下一个人")
        keyevent('BACK')


def like_post():
    post_list = poco("com.cupidapp.live:id/profilePostCoverImageView")
    if len(post_list) > 0:
        watcher()
        print("进入动态")

        if post_list[0].exists():
            post_list[0].click()
        sleep(1)
        like = poco("com.cupidapp.live:id/feedPraiseButton")
        if like.exists():
            watcher()
            print("发现动态，准备点赞")

            if len(like) > 0:
                like[0].click()
                print("点赞一条动态")
            else:
                print(like.nodes)
        else:
            print("没找到")
        watcher()
        print("点赞结束，准备返回")

        back = poco("com.cupidapp.live:id/leftImageView")
        if back.exists():
            watcher()
            print("点赞返回")

            back.click()


def like_people():
    global total
    poco_like = poco("com.cupidapp.live:id/followImageView")
    if poco_like.exists():
        watcher()
        poco_like.click()
        total += 1
        print("喜欢了 %s 人" % total)
    back = poco("com.cupidapp.live:id/leftImageView")
    if back.exists():
        watcher()
        back.click()


def watcher():
    print("-----------------------弹窗检测启动")
    find_element = poco("com.cupidapp.live:id/closeImageView")
    if find_element.exists():
        find_element.click()
        print("发现元素")
    else:
        print("-----------------------等待0.5秒，当前时间：", time.strftime("%H:%M:%S", time.localtime()))

    time.sleep(2)

if __name__ == '__main__':
    start()