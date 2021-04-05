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
        self.fans_json = ""
        self.validate_config()

    def judge_lite(self):
        sleep(3)
        return
        # sleep(3)
        # if exists(Template(r"tpl1616916148778.png", threshold=0.9000000000000001, rgb=True, record_pos=(-0.193, -0.033), resolution=(1080, 2340))):
        #     touch(Template(r"tpl1616916171046.png", threshold=0.9000000000000001, rgb=True, record_pos=(0.153, 0.212), resolution=(1080, 2340)))
        # sleep(1)

    def fetch_fans(self):
        frzz = self.poco.freeze()
        frzz("android.widget.LinearLayout").offspring("com.android.chrome:id/compositor_view_holder").offspring(
            "app")[0].child("android.view.View")[0].child("android.view.View")[7].click()
        self.only_scrol()
        keyevent("BACK")
        sleep(3)

    def fetch_follows(self):
        frzz = self.poco.freeze()
        button = frzz("android.widget.LinearLayout").offspring("com.android.chrome:id/compositor_view_holder").offspring(
            "app")[0].child("android.view.View")[0].child("android.view.View")[6]
        if button:
            button.click()
        else:
            swipe((self.s_width * 0.5, self.s_height * 0.5), vector=[0, -0.4])
            sleep(5)
            frzz = self.poco.freeze()
            button = frzz("android.widget.LinearLayout").offspring("com.android.chrome:id/compositor_view_holder").offspring(
                "app")[0].child("android.view.View")[0].child("android.view.View")[6]

        self.only_scrol()
        keyevent("BACK")
        sleep(3)
        self.fetch_fans()

    def only_scrol(self):
        path = Path("./end_user.png")
        if path.exists():
            path.unlink()
        while True:
            sleep(2)
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
        # self.judge_lite()
        swipe((self.s_width * 0.5, self.s_height * 0.9), vector=[0, -1])
        sleep(5)

        scr = crop_image(G.DEVICE.snapshot(), (0, self.s_height / 2, 450, self.s_height / 2 + 250))
        sleep(1)
        return scr

    def compaire_image(self, scr):
        path = Path("./end_user.png")
        if path.exists():
            tempalte = Template(r"./end_user.png",threshold=0.90)
            pos = tempalte.match_in(scr)
            if pos:
                print("貌似到达底部了", pos)
                return True
            else:
                return False
        else:
            return False

    def start(self):
        owner = list(source.find({},{"user.id": 1, "user.screen_name": 1}))
        current = [item for item in owner if item["user"]["id"] == self.fans_json["userid"]]
        index = owner.index(current[0])
        user_list = [item["user"] for item in owner][index:]
        for user in user_list:
            start_app("com.android.chrome")
            sleep(5)

            swipe((self.s_width * 0.5, self.s_height * 0.5), vector=[0, -0.2])
            userid = user["id"]
            username = user["screen_name"]
            url = "https://m.weibo.cn/profile/"+str(userid)
            
            swipe((self.s_width * 0.5, self.s_height * 0.5), vector=[0, 0.2])
            sleep(5)
            self.poco("com.android.chrome:id/url_bar").click()
            self.poco("com.android.chrome:id/url_bar").set_text("")
            sleep(1)
            text(url, search=True)
            sleep(5)
            # self.judge_lite()
            print("当前是 %s 的粉丝，id是 %s \n" %(username,userid))
            self.write_data(userid)
            self.fetch_fans()
            stop_app("com.android.chrome")

    def validate_config(self):
        path = Path("fans.json")
        if not path.is_file():
            sys.exit(u'当前路径：%s 不存在fans.json' % path.resolve())

        with open("fans.json") as file:
            try:
                self.fans_json = json.loads(file.read())
                print(self.fans_json)
            except ValueError:
                sys.exit(u'fans.json 格式不正确')

    def write_data(self, id):
        self.fans_json["userid"] = id
        with open("fans.json", "w") as f:
            json.dump(self.fans_json, f)
            


def change_date():
    users = db["weibo_users"]
    datas = list(users.find({}))
    for data in datas:
        userid = data["user"]["id"]
        fromwho = data["from_who"]
        dump = list(users.find({"user.id":userid, "from_who":fromwho}))
        print("%s 有%s 个重复"%(userid,len(dump)))

        if len(dump) > 1:
            for i in range(0, len(dump)-1):
                print("删除第 %s 个重复项"% str(i+1))
                users.delete_one({"user.id":userid, "from_who":fromwho})

if __name__ == '__main__':
    # change_date()
    follow = Follow()
    follow.start()
