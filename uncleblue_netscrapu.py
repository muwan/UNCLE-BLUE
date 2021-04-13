# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/13
"""
from aloha import aloha_scrapy
from xhs import xhs_scrapy

addons = [
    aloha_scrapy.Aloha(),
    xhs_scrapy.XHS(),
]