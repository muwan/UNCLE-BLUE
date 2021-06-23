# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/6/19
"""
__author__ = "henly"

from airtest.core.api import *

auto_setup(__file__)

from poco.drivers.ios import iosPoco

poco = iosPoco()

source_cells = poco("Window").child("Other").child("Other").offspring("Table").children()

for cell in source_cells:
    cell.click()
    sleep(3)
    poco("9万 粉丝").click()
    fans_btn = poco("Window").child("Other").child("Other").offspring("Table").child("Other").child("Other")[4].child(
        type="Button")[1]
    fans_btn.click()
    sleep(3)


