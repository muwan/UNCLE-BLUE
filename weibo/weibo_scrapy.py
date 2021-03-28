# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/2
"""
base_url = "https://m.weibo.cn"
from airtest.core.api import *
from airtest.aircv import *
from pathlib import Path


auto_setup(__file__)


from poco.drivers.android.uiautomation import AndroidUiautomationPoco
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
s_width,s_height = poco.get_screen_size()


"https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_1453649594"

import json
import pymongo

# from mitmproxy import flowfilter, http, ctx

# client = pymongo.MongoClient("localhost")
# db = client["uncleblue"]
# # 需要关注的用户
# collection = db["weibo_users"]
# #可以爬取的用户
# source = da["weibo_sources"]

poco("Chrome").click()
# poco("com.android.chrome:id/url_bar").click()
# sleep(1)
# text("https://m.weibo.cn/profile/1453649594", search=True)
# sleep(3)

# # 关注
# poco("android.widget.LinearLayout").offspring("com.android.chrome:id/compositor_view_holder").offspring("app")[0].child("android.view.View")[0].child("android.view.View")[6].click()


while True:
    poco("android.webkit.WebView").swipe([-0.0144, -0.555])
    sleep(1)
    
    scr = crop_image(G.DEVICE.snapshot(),(0,s_height-400,s_width,s_height))
    path = Path("./end_user.png")
    if path.exists():
        tempalte = Template(path.resolve())
        pos = tempalte.match_in(scr)
        print("已经到底了，开始下一个",pos)
    else:
        end_user = cv2_2_pil(scr)
        end_user.save(r"./end_user.png")
        print("继续往下滑")
 

# swipe((s_width * 0.5, s_height * 0.8), vector=[0, -1], duration=1)

# 粉丝、
# poco("android.widget.LinearLayout").offspring("com.android.chrome:id/compositor_view_holder").offspring("app")[1].child("android.view.View")[0].child("android.view.View")[7].click()


def judge_lite():
    if exists(Template(r"tpl1616916148778.png", record_pos=(-0.193, -0.033), resolution=(1080, 2340))):
        touch(Template(r"tpl1616916171046.png", record_pos=(0.153, 0.212), resolution=(1080, 2340)))




# class Follow(object):
#     def weibo_url(self):
#         headers = {
#             "accept": "application/json,text/plain, */*",
#             "dnt": 1,
#             "x-xsrf-token": 104048,
#             "x-requested-with": "XMLHttpRequest",
#             "mweibo-pwa": 1,
#             "user-agent": "Mozilla / 5.0(Macintosh;Intel Mac OS X 11_2_2) AppleWebKit/537.36(KHTML,likeGecko) Chrome/87.0.4280.88 Safari/537.36",
#             "sec-fetch-site": "same-origin",
#             "sec-fetch-mode": "cors",
#             "sec-fetch-dest": "empty",
#             "referer": "https://m.weibo.cn/p/index?containerid = 231051_-_fans_-_5686465105",
#             "accept-encoding": "gzip, deflate, br",
#             "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,zh-HK;q=0.6",
#             "cookie": "SCF=AgXNIOFwpgywws6C1B97zJzYk8cR5I0xIdrH91TNSs8p7ai7tfEvZvKaNmJnnCQpXzRlkImtVKzfuY8U17SREeA.;SUB=_2A25NWRJmDeRhGeNP61QX8SjIyjiIHXVupb4urDV6PUJbktAKLRL8kW1NTqF6tHxUY53Las-_H83xchhjY4kGBBSK;SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhCBm1PpalYuqA0lHUFum8R5NHD95QfeK5cSo2cSh2XWs4DqcjGBgxaUgiL9Btt;MLOGIN=1;_T_WM=92726686995;XSRF-TOKEN=104048;WEIBOCN_FROM=1110006030;M_WEIBOCN_PARAMS=uicode%3D20000174",
#         }
#         pass

