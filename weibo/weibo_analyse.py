# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/4/5
"""

from pyppeteer.page import Page
from pyppeteer import launch
from pyppeteer.errors import TimeoutError
from pathlib import Path
from enum import Enum

import sys
import asyncio
import pymongo
import time

WINDOW_WIDTH, WINDOW_HEIGHT = 1366, 768
client = pymongo.MongoClient('localhost')
db = client['uncleblue']

SOURCE = db['weibo_sources']
FOLLOW_COLLECTION = db["weibo_follow"]
DAILY = db['weibo_daily']


class FollowState(Enum):
    AllFans = 1
    MyFans = 2
    HisFans = 3
    Either = 4


# follow_state = Enum("FollowState",("AllFans","MyFans","HisFans","Either"))

class WeiBoAnalyse(object):
    def __init__(self):
        # 互相关注
        self.double_follow = 0
        # 对方未关注
        self.unfollow = 0
        # 双方未关注
        self.double_unfollow = 0
        # 对方关注你，你未关注对方
        self.fans = 0

    def verify(self):
        path = Path("analyse.json")
        if not path.is_file():
            sys.exit(u'当前路径：%s 不存在关注文件 analyse.json' % path.resolve())


    async def launch(self) -> Page:
        p = Path("./userData").resolve()

        brownser = await launch(headless=True,
                                userDataDir=p,
                                args=[
                                        '--disable-infobars',
                                        f'--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}',
                                        '--no-sandbox'])
        page = await brownser.newPage()
        return page

    async def query_page(self, userid, selecter, page: Page) -> Page:
        try:
            url = f"https://weibo.com/u/{userid}?is_all=1"
            await page.setViewport({'width': WINDOW_WIDTH, 'height': WINDOW_HEIGHT})
            await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
            await page.goto(url, options={"timeout": 1000*60, "waitUntil": "networkidle0"})
            await page.waitForSelector(selecter,{"timeout":1000*30})
            return page
        except TimeoutError:
            print(TimeoutError)

    async def analyse_page(self,page:Page) -> FollowState:
        element = await page.querySelector("div[node-type='focusLink'] > a")
        if element :
            innerText = await page.evaluate('element => element.innerText', element)
            # Y已关注 单方面关注对方
            # Z互相关注
            # Y+关注 未关注对方，对方关注你
            # +关注 互相未关注
            if innerText == "Z互相关注":
                self.double_follow += 1
                print("互粉成功 %s 时间：%s" % (self.double_follow,time.strftime("%H:%M:%S", time.localtime())))
                return FollowState.AllFans
            elif innerText == "Y+关注":
                self.fans += 1
                print("对方已关注 %s 时间：%s" % (self.fans, time.strftime("%H:%M:%S", time.localtime())))
                return FollowState.MyFans
            elif innerText == "Y已关注":
                self.unfollow += 1
                print("对方未关注 %s 时间：%s" % (self.unfollow, time.strftime("%H:%M:%S", time.localtime())))
                return FollowState.HisFans
            elif innerText == "+关注":
                self.double_unfollow += 1
                print("都未关注 %s 时间：%s" % (self.double_unfollow, time.strftime("%H:%M:%S", time.localtime())))
                return FollowState.Either

    async def get_date_users(self):
        page = await self.launch()
        day_list = [str(i) for i in range(20210403,20210408)]
        for date in day_list:
            self.double_follow = 0
            self.unfollow = 0
            self.double_unfollow = 0
            self.fans = 0

            users = list(FOLLOW_COLLECTION.find({"date": date}))
            total = FOLLOW_COLLECTION.count_documents({"date": date})
            all_source = {}
            for user in users:
                userid = user["userid"]
                await self.query_page(userid, ".WB_frame_c", page)
                await asyncio.sleep(1)
                state = await self.analyse_page(page)
                source = SOURCE.find_one({"user.id": int(user["source"])})
                sourceid = str(source["user"]["id"])
                name = source["user"]["screen_name"]

                source_dic = all_source[sourceid] if all_source.get(sourceid) else {"followed": 0, "total": 0,
                                                                                    "name": name}
                source_dic["total"] = source_dic["total"] + 1

                if state == FollowState.AllFans:
                    followed = source_dic["followed"]
                    source_dic["followed"] = followed + 1
                    print("%s 的粉丝关注了" % source["user"]["screen_name"])
                elif state == FollowState.HisFans:
                    pass
                elif state == FollowState.MyFans:
                    pass
                elif state == FollowState.Either:
                    pass
                all_source[sourceid] = source_dic

            double_percent = "{:.2%}".format(self.double_follow / total)
            print("%s 互关率是 %s" % (date, double_percent))

            fans_percent = "{:.2%}".format(self.fans / total)
            print("%s 主动关注率 %s" % (date, self.fans))
            print("%s 当天关注情况是 %s" % (date, all_source))

            for key, one in all_source.items():
                onefolloewd = one["followed"]
                onetotal = one["total"]
                onename = one["name"]
                percent = "{:.2%}".format(onefolloewd / onetotal)

                print("%s 的粉丝关注率是 %s" % (onename, percent))

            if not DAILY.find_one({"date": date}):
                daily_record = {
                    "date": date,
                    "follow_analyse": all_source
                }
                DAILY.insert_one(daily_record)
            else:
                DAILY.update_one({"date": date}, {"$set": {"follow_analyse": all_source}})

        # date = time.strftime("%Y%m%d", time.localtime())


if __name__ == '__main__':
    login = WeiBoAnalyse()
    asyncio.get_event_loop().run_until_complete(login.get_date_users())


