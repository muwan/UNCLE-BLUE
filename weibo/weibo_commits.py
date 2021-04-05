# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/3
"""

import requests
from weibo import Client


access_token =  ''

url = "https://api.weibo.com/2/statuses/share.json"
#构建POST参数
params = {
"access_token": access_token,
"status": "百度一下！http://lhl.ybo.me"
}
#POST请求，发表文字微博
res = requests.post(url,data = params)
print(res.text)