# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/2
"""
import motor
import asyncio
import random
import json
import sys
import fileinput
import motor.core

from pathlib import Path
from pyppeteer.launcher import launch
from pyppeteer.page import Page
from pyppeteer.browser import Browser
from bson.objectid import ObjectId

client = motor.motor_tornado.MotorClient()
db = client["uncleblue"]
USER_COLLECTION = db["douban_users"]
FOLLOW_COLLECTION = db["douban_follow"]

D_WIDTH, D_HEIGHT = 1366, 768


class Follow(object):
    def __init__(self, maxtab=20, timeout=1000 * 60, headless=False):
        self.loop = asyncio.get_event_loop()
        self.timeout = timeout
        self.maxtab = maxtab
        self.headless = headless
        self.follow_json = None
        self.validate_config()

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

    def write_data(self, id):
        self.follow_json["objectid"] = str(id)

        with open("follow.json", "w") as f:
            json.dump(self.follow_json, f)

    async def launch(self) -> Browser:
        p = Path("./userData").resolve()
        brownser: Browser = await launch(headless=False,
                                         userDataDir=p,
                                         ignoreHTTPSErrors=True,
                                         ignoreDefaultArgs=['--enable-automation'],
                                         loop=self.loop,
                                         dumpio=True,
                                         args=['--disable-infobars',
                                               f'--window-size={D_WIDTH},{D_HEIGHT}',
                                               '--no-sandbox',
                                               '--incognito',
                                               '--ignore-certificate-errors',
                                               '--disable-setuid-sandbox',
                                               '--disable-extensions'
                                               ])
        return brownser

    async def start_pages(self, user, browser: Browser):
        url = user["url"]
        page = await browser.newPage()
        await page.setViewport({"width": D_WIDTH, "height": D_HEIGHT})
        await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get:() => false})')
        try:
            await page.goto(url, {
                "waitUntil": [
                    'load',
                    'domcontentloaded']
            })
            status = await self.prase_pages(user, page)
            print("status ",status)
            await asyncio.sleep(random.randint(1,3))
            await page.close()
            return status
        except TimeoutError:
            await page.reload()
        except Exception as e:
            print(url,e)
        finally:
            pass
            # await page.close()

    async def stare_single_page(self, users, browser: Browser):
        page = await browser.newPage()
        await page.setViewport({"width": D_WIDTH, "height": D_HEIGHT})
        await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get:() => false})')
        for user in users:
            url = user["url"]
            try:
                await page.goto(url, {
                    "waitUntil": [
                        'load',
                        'domcontentloaded']
                })
                status = await self.prase_pages(user, page)
                print("status ", status)
                await asyncio.sleep(random.randint(1, 3))
                await page.close()
                return status
            except TimeoutError:
                await page.reload()
            except Exception as e:
                print(url, e)
            finally:
                pass

    async def prase_pages(self, user, page: Page):
        self.write_data(user["_id"])
        user_opt = await page.querySelector("div.user-opt")
        if user_opt:
            follow_btn = await user_opt.querySelector("a.add_contact")
            if follow_btn:
                await asyncio.sleep(random.randint(1, 3))
                await follow_btn.click()
                print("%s关注成功！" % user["name"])
                if not await FOLLOW_COLLECTION.find_one({"_id":user["_id"]}):
                    await FOLLOW_COLLECTION.insert_one(user)
                # await page.close()
                return True
            else:
                friend = await user_opt.querySelector("span.user-cs")
                if friend:
                    text = await page.evaluate('element => element.innerText', friend)
                    if text == "已关注":
                        print("user:%s ,账号已关注" % user["name"])
                    else:
                        print("friend exists")
                else:
                    print("无此账号")
                # await page.close()
                return False
        else:
            print("应该是打开了其他页面")
            # await page.close()
            return False

    def callback(self, future):
        print('这是回调函数，返回结果', future.result())

    async def start(self):
        start_id = self.follow_json["objectid"]
        cursor = USER_COLLECTION.find({"_id": {"$gte": ObjectId(start_id)}})
        users = (await cursor.to_list(length=1000))[:30]
        browser = await self.launch()

        await self.stare_single_page(users,browser)
        return
        # step = 5
        # total = 0
        # for index in range(0, len(users), step):
        #     page_users = [user for user in users[index:index + step]]
        #     tasks = []
        #     for user in page_users:
        #         task = asyncio.create_task(self.start_pages(user, browser))
        #         tasks.append(task)
        #     results = await asyncio.gather(*tasks)
        #     number = sum(1 if r else 0 for r in results)
        #     print("本轮已经关注%s人" % number)
        #     total += number
        #     print("一共已经关注%s人" % total)
        #
        # if total > 499:
        #     print("今日关注已经结束")


if __name__ == '__main__':
    follow = Follow(timeout=1000 * 60, headless=False)
    follow.loop.run_until_complete(follow.start())
