# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/2
"""

from pyppeteer.page import Page
from pyppeteer import launch
from pyppeteer.browser import Browser
from bson.objectid import ObjectId
from pathlib import Path
from enum import Enum

import random
import sys
import asyncio
import pymongo
import time
import chaojiying
import json

WINDOW_WIDTH, WINDOW_HEIGHT = 1366, 768
client = pymongo.MongoClient('localhost')
db = client['uncleblue']
collection = db['weibo_users']

FOLLOW_COLLECTION = db["weibo_follow"]

Status = Enum("Status", ("Fail", "Success", "Skip", "Sleep"))


class Follow(object):
    def __init__(self):
        self.cjy = chaojiying.Chaojiying_Client("sunbofu", "awgmRFEHbKSe.u7", "909639")
        self.last_status = False
        self.real_count = 0
        self.follow_json = {}
        self.last_follow = None
        self.validate_config()

    async def launch_brownser(self) -> Browser:
        p = Path("./userData").resolve()

        brownser = await launch({"headless": True,
                                 "userDataDir": p,
                                 "args": [
                                     '--disable-infobars',
                                     f'--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}',
                                     '--no-sandbox'
                                 ]})
        return brownser

    async def query_page(self, userid, selecter, page: Page) -> Page:
        try:
            await page.setViewport({'width': WINDOW_WIDTH, 'height': WINDOW_HEIGHT})
            await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
            await page.goto(userid, options={"timeout": 1000 * 60, "waitUntil": "networkidle0"})
            await page.waitForSelector(selecter)
            # await asyncio.wait(
            #     [
            #         asyncio.sleep(3),
            #         page.waitForSelector(selecter, options={"timeout": 1000 * 60})
            #     ]
            # )
            return page
        except TimeoutError:
            print('timeout error')

    async def prase_page(self, page: Page):
        sexElement = await page.querySelector("i.icon_pf_male")
        if sexElement:
            element = await page.querySelector("div[node-type='focusLink'] > a")
            if not await page.evaluate('element => element.getAttribute("action-type")', element) == "unFollow":
                await element.click()
                await asyncio.sleep(2)
                await element.focus()
                await asyncio.sleep(3)

                group = await page.querySelector(".list_ul > li[action-type='setGroup']")
                if group:
                    await group.click()
                    await asyncio.sleep(random.randint(3,5))
                labels = await page.querySelectorAll("[node-type='normal'] > li")
                for lanel in labels:
                    if await page.evaluate("element => element.innerText", lanel) == "待观察":
                        await lanel.click()
                        await asyncio.sleep(random.randint(1, 3))
                        submit = await page.querySelector("[node-type='submit']")
                        await submit.click() if submit else None

                await asyncio.sleep(random.randint(1, 3))

                yzm_frame = await page.querySelector('input.yzm_input')
                if yzm_frame:
                    status = await self.pass_verify(page)
                    return status
                else:
                    self.last_status = False
                    print('finish follow')
                    return "Success"
            else:
                print("pass followed")
                return "Pass"
        else:
            print("skip female")
            return "Pass"

    async def pass_verify(self, web_page):
        print("%s 阿哦，遇到验证码了" % time.strftime("%H:%M:%S", time.localtime()))

        if self.real_count % 100 > 0 or self.real_count == 0 or self.last_status:
            await asyncio.sleep(1)
            yzm_img = await web_page.waitForSelector("img.yzm_img")
            img = await yzm_img.screenshot()
            yzm_res = self.cjy.PostPic(img, "6004")
            error_no = yzm_res.get("err_no")
            pic_id = yzm_res.get("pic_id")
            input_text = yzm_res.get("pic_str")
            if input_text and error_no == 0:
                self.last_status = False
                await web_page.type("input[action-type='yzm_input']", input_text, {"delay": 2})
                await asyncio.sleep(1)
                submit_btn = await web_page.querySelector("[action-type='yzm_submit']")
                await submit_btn.click()
                await asyncio.sleep(random.randint(1, 3))
                yzm_frame_new = await web_page.querySelector('div.layer_verification')
                if yzm_frame_new:
                    self.cjy.ReportError(pic_id)
                    print("现在时间: %s , 验证码未通过" % (time.strftime("%H:%M:%S", time.localtime())))
                    png_name = f"{time.strftime('%Y%m%d%H%M%S', time.localtime())}.png"
                    await web_page.screenshot({'path': f'./errImg/{png_name}'})
                    return "Fail"
                else:
                    print("验证成功")
                    return "Success"
            else:
                return "Fail"
        else:
            self.last_status = True
            sleep_time = random.randint(90 * 60, 120 * 60)
            print("现在时间: %s , 休息时间 : %s 小时 %s 分 %s 秒" % (
                time.strftime("%H:%M:%S", time.localtime()), int(sleep_time / 3600),
                int((sleep_time % 3600) / 60), (sleep_time % 3600) % 60))
            await asyncio.sleep(sleep_time)
            return "Sleep"

    async def pyppeteer_get(self):
        brownser = await self.launch_brownser()
        try:
            # "_id": {"$gte": ObjectId(user_id)}
            userid = self.follow_json["mac_id"]
            sys_user_list = list(collection.find({"_id": {"$gte": ObjectId(userid)}}))
            page = await brownser.newPage()

            for index, user in enumerate(sys_user_list):
                self.last_follow = str(user["_id"])
                self.write_to_txt()
                follow_id = user["user"]["id"]
                follow_name = user["user"]["screen_name"]
                follow_avatar = user["user"]["avatar_hd"]
                follow_who = user["from_who"]
                follow_fans = user["user"]["followers_count"]
                follow_num = user["user"]["follow_count"]
                url = f"https://weibo.com/u/{user['user']['id']}?is_all=1"
                date = time.strftime("%Y%m%d", time.localtime())

                await self.query_page(url, ".WB_frame_c", page)
                status = await self.prase_page(page)
                if status == "Sleep" or status == "Fail":
                    await self.query_page(url, ".WB_frame_c", page)
                elif status == "Success":
                    data = {"userid": follow_id,
                            "avatar": follow_avatar,
                            "name": follow_name,
                            "source": follow_who,
                            "fans": follow_fans,
                            "follow": follow_num,
                            "date":date}
                    if not FOLLOW_COLLECTION.find_one({"userid": follow_id, "source": follow_who}):
                        FOLLOW_COLLECTION.insert_one(data)

                self.real_count = FOLLOW_COLLECTION.find({"date":date}).count()
                print("已经关注 %s 人,当前时间：%s" % (self.real_count, time.strftime("%H:%M:%S", time.localtime())))
                print("%s 粉丝数：%s 关注了:%s 人" % (follow_name, follow_fans, follow_num))

                if self.real_count > 500:
                    print("今天已将关注500人，bye")
                    break
        finally:
            print("ok 今天的关注结束啦")

    def write_to_txt(self):
        if sys.platform == "darwin":
            self.follow_json["mac_id"] = self.last_follow
        else:
            self.follow_json["win_id"] = self.last_follow

        with open('follow.json', 'w') as f:
            json.dump(self.follow_json, f)

    def validate_config(self):
        path = Path("follow.json")
        if not path.is_file():
            sys.exit(u'当前路径：%s 不存在关注文件config.json' % path.resolve())

        with open("follow.json") as file:
            try:
                self.follow_json = json.loads(file.read())
                print(self.follow_json)
            except ValueError:
                sys.exit(u'follow.json 格式不正确')


if __name__ == '__main__':
    login = Follow()
    asyncio.get_event_loop().run_until_complete(login.pyppeteer_get())
