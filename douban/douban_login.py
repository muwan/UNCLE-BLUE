# -*- coding: utf-8 -*-
"""
Description:
Author:henly Date:2021/3/9
"""

import asyncio
import random

from pyppeteer import launch

BASE_URL = "https://www.douban.com"
D_WIDTH, D_HEIGHT = 1366, 768


class Login(object):
    def __init__(self, user_name, user_password):
        self.user_name = user_name
        self.user_password = user_password
        self.loop = asyncio.get_event_loop()

    async def login(self):
        browser = await self.loop.create_task(
            launch(headless=False,
                   userDataDir="./userData",
                   ignoreHTTPSErrors=True,
                   ignoreDefaultArgs=['--enable-automation'],
                   loop=self.loop,
                   args=["--disable-infobars",
                         f"--window-size={D_WIDTH},{D_HEIGHT}",
                         "--no-sandbox",
                         '--incognito',
                         '--ignore-certificate-errors',
                         '--disable-setuid-sandbox'
                         ]))
        page = await browser.newPage()
        await page.setViewport({"width": D_WIDTH, "height": D_HEIGHT})
        await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get:() => false})')
        await page.goto(BASE_URL, {"timeout": 1000 * 60})
        await page.waitForSelector("div.login", options={"timeout": 60 * 1000})

        iframes = page.frames
        for iframe in iframes:
            url = iframe.url
            if 'accounts.douban.com/passport/login_popup' in url:
                await iframe.click('li.account-tab-account')
                await iframe.type("#username", self.user_name, {'delay': random.randint(60, 121)})
                await asyncio.sleep(random.randint(2, 4))
                await iframe.type("#password", self.user_password, {'delay': random.randint(60, 121)})
                await asyncio.sleep(random.randint(2, 4))
                await iframe.click("div.account-form-field-submit")
                await asyncio.sleep(100)


if __name__ == '__main__':
    user_name = input("user account:")
    password = input("password:")
    douban = Login(user_name, password)
    douban.loop.run_until_complete(douban.login())
