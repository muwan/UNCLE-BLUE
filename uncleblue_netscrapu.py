# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/13
"""

from wei_bo import weibo_net

from aloha import aloha_scrapy
# from xhs import xhs_scrapy

addons = [
    aloha_scrapy.Aloha(),
    # xhs_scrapy.XHS(),ç
    weibo_net.WeiboNet()
]