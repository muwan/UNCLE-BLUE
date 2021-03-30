# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/2
"""

from airtest.core.api import *
from airtest.aircv import *
from pathlib import Path
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

import json
import pymongo
import logging

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)


client = pymongo.MongoClient("localhost")
db = client["uncleblue"]
#可以爬取的用户
source = db["weibo_sources"]


class Follow(object):

    def __init__(self):
        connect_device("android://127.0.0.1:5037/4f74b1cc?cap_method=MINICAP_STREAM&&ori_method=MINICAPORI&&touch_method=MINITOUCH")
        self.poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        self.s_width, self.s_height = self.poco.get_screen_size()

    def judge_lite(self):
        sleep(3)
        if exists(Template(r"tpl1616916148778.png", threshold=0.9000000000000001, rgb=True, record_pos=(-0.193, -0.033), resolution=(1080, 2340))):
            touch(Template(r"tpl1616916171046.png", threshold=0.9000000000000001, rgb=True, record_pos=(0.153, 0.212), resolution=(1080, 2340)))
        sleep(1)

    def fetch_fans(self):
        frzz = self.poco.freeze()
        frzz("android.widget.LinearLayout").offspring("com.android.chrome:id/compositor_view_holder").offspring(
            "app")[0].child("android.view.View")[0].child("android.view.View")[7].click()
        self.only_scrol()

    def fetch_follows(self):
        frzz = self.poco.freeze()
        frzz("android.widget.LinearLayout").offspring("com.android.chrome:id/compositor_view_holder").offspring(
            "app")[0].child("android.view.View")[0].child("android.view.View")[6].click()
        self.only_scrol()
        keyevent("BACK")
        sleep(3)
        self.fetch_fans()

    def only_scrol(self):
        path = Path("./end_user.png")
        if path.exists():
            path.unlink()
        while True:
            scr = self.scrol_crop()
            is_same = self.compaire_image(scr)
            if is_same:
                # 二次滚动防止提前退出
                second_pic = self.scrol_crop()
                second = self.compaire_image(second_pic)
                if second:
                    print("确实已经到达底部，下一轮开始了")
                    break
                else:
                    self.save_caputure(second_pic)
            else:
                self.save_caputure(scr)

    def save_caputure(self, pic):
        end_user = cv2_2_pil(pic)
        end_user.save(r"./end_user.png")
        print("继续往下滑")

    def scrol_crop(self):
        self.judge_lite()
        swipe((self.s_width * 0.5, self.s_height * 0.9), vector=[0, -1])
        sleep(1)

        scr = crop_image(G.DEVICE.snapshot(), (0, self.s_height / 2, 250, self.s_height / 2 + 250))
        return scr

    def compaire_image(self, scr):
        path = Path("./end_user.png")
        if path.exists():
            tempalte = Template(r"./end_user.png")
            pos = tempalte.match_in(scr)
            if pos:
                print("貌似到达底部了", pos)
                return True
            else:
                return False
        else:
            return False

    def start(self):
        start_app("com.android.chrome")
        owner = list(source.find({},{"user.id": 1, "screen_name": 1}))
        user_list = [item["user"] for item in owner]
        user_list.insert(0, {"id":"7270944832","screen_name":"我阅帅哥无数"})
        for user in user_list:
            userid = user["id"]
            username = user["screen_name"]
            url = "https://m.weibo.cn/profile/"+userid
            print("当前是 %s 的粉丝，id是 %s \n" %(username,userid))
            swipe((self.s_width * 0.5, self.s_height * 0.5), vector=[0, 1])
            sleep(1)
            self.poco("com.android.chrome:id/url_bar").click()
            self.poco("com.android.chrome:id/url_bar").set_text("")
            sleep(1)
            text(url, search=True)
            sleep(5)
            self.judge_lite()
            self.fetch_fans()


if __name__ == '__main__':
    follow = Follow()
    follow.start()
