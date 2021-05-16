# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/28
"""
import requests
import pymongo
import random
import datetime
import time
import pandas as pd
import asyncio
import shutil

from pyppeteer.page import Page
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.errors import TimeoutError
from pathlib import Path
from bson.objectid import ObjectId


WINDOW_WIDTH, WINDOW_HEIGHT = 1366, 768
client = pymongo.MongoClient('localhost')
db = client['xiaohongshu']
collection = db['discover225']

proxypool = []  # 'http://127.0.0.1:5555/random'


def get_proxy_list():
    global proxypool
    request_url = "http://d.jghttp.alicloudecs.com/getip?num=100&type=2&pro=&city=0&yys=0&port=1&time=1&ts=1&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions="
    response = requests.get(request_url)
    result = response.json()
    if result.get("data"):
        proxypool = result.get("data")


def get_random_proxy():
    global proxypool

    def get_random_item():
        global proxypool
        total = len(proxypool)
        random_res = proxypool[random.randint(0, total - 1)]
        return random_res

    radom_item = get_random_item()
    now = datetime.datetime.now()
    expire_time = datetime.datetime.strptime(radom_item["expire_time"], "%Y-%m-%d %H:%M:%S")
    random_url = str(radom_item["ip"]) + ":" + str(radom_item["port"])
    if (expire_time - now).seconds > 10:
        print("current url %s 过期时间 %s "%(random_url,expire_time))
        return random_url,expire_time
    else:
        proxypool.remove(radom_item)
        get_random_item()


async def get_brownser():
    p = Path("./xhs_userData").resolve()
    proxy_url,expire_time = get_random_proxy()
    brownser = await launch({"headless": False,
                             "userDataDir": p,
                             "autoClose":False,
                             "args": [
                                 '--disable-infobars',
                                 f'--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}',
                                 '--no-sandbox',
                                 # '--proxy-server='+'60.166.183.147:4531'
                             ]})
    context = await brownser.createIncognitoBrowserContext()
    page = await context.newPage()
    user_list = list(collection.find({"_id":{"$gt": ObjectId("603785e1058469c7d07685a0")}}))
    for user in user_list:
        url = user["url"]
        await page.setViewport({'width': WINDOW_WIDTH, 'height': WINDOW_HEIGHT})
        await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
        await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
        try:
            await page.goto(url,options={"timeout": 1000 * 5})
            await asyncio.sleep(5)
            await prase_web(page, user)
        except TimeoutError:
            print(TimeoutError)
            await prase_web(page, user)


async def prase_web(page:Page,user):
    location = await page.querySelector("span.location-text")
    if location:
        location_text = await page.evaluate("element => element.innerText",location)
        collection.update_one({"_id":user["_id"]},{"$set":{"location":location_text}})
        print("%s 的所在地是：%s, _id 是 %s" % (user["name"],location_text,user["_id"]))





def main():
    """
    main method, entry point
    :return: none
    """
    path = Path("./xhs_userData")
    if path.exists():
        shutil.rmtree(path.resolve())

    get_proxy_list()
    asyncio.get_event_loop().run_until_complete(get_brownser())


def select_changsha():
    users = list(collection.find({}))[:2000]
    for user in users:
        if user.get("location"):
            location = str(user["location"])
            # print(location)
            if "changsha" in location.lower() or "长沙" in location:
                print("找到长沙用户 %s %s" % (user["name"],user["url"]))

if __name__ == '__main__':
    # main()
    select_changsha()
