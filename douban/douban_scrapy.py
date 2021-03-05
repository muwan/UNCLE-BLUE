# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/2
"""
from airtest.core.api import *
auto_setup(__file__)
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
s_width,s_height = poco.get_screen_size()

poco("豆瓣").click()
sleep(5)
freeze_po = poco.freeze()
group_list = freeze_po("com.douban.frodo:id/list_view").children()

for item in group_list:
    group_name = item.child("com.douban.frodo:id/tvTitle").get_text()
    if group_name == "本少要给自己找BF❤Gay":
        continue
    if group_name == "我们是Gay,但我们很Man!":
        continue
    if group_name == "彩虹城市-Gay":
        continue

    item.click()
    sleep(2)
    poco("com.douban.frodo:id/count").click()
    pre_name_list = []
    while True:
        sleep(5)
        freeze_user = poco.freeze()
        user_list = freeze_user("com.douban.frodo:id/name")
        user_name_list = []
        for user in user_list:
            user_name = user.get_text()
            user_name_list.append(user_name)
        print("user name list: ", user_name_list)
        if user_name_list == pre_name_list:
            print("-----------------\n-----------------\n到头了,去下一个小组\n-----------------\n-----------------\n")
            poco("android.widget.ImageButton").click()
            sleep(1)
            poco("Navigate up").click()
            sleep(0.5)
            break
        else:
            pre_name_list = user_name_list
            swipe((s_width * 0.5, s_height * 0.8), vector=[0, -1], duration=1)
            sleep(3)
        
#     print(item.type())
# print(group_list)poco("com.douban.frodo:id/list_view")
# poco("android.widget.ImageButton").click()
# poco("android.widget.LinearLayout").offspring("android:id/content").offspring("com.douban.frodo:id/content_container").offspring("com.douban.frodo:id/view_pager").child("android.widget.FrameLayout").offspring("com.douban.frodo:id/list_view").child("android.view.ViewGroup")[0].click()
# poco("com.douban.frodo:id/count").click()
# poco(zOrders="{'global': 0, 'local': 6}").swipe([-0.0159, -0.4152])
# poco(zOrders="{'global': 0, 'local': 8}").swipe([0.0573, -0.4047])
poco