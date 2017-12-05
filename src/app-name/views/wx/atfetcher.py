# -*- coding: utf-8 -*-
# filename: basic.py
import asyncio
import json
import time

import aiohttp
from aiohttp import ClientSession
import sys

class atfetcher:
    def __init__(self):
        self.__accessToken = ''
        self.__leftTime = 0
        self.__fetching = False

    async def __real_get_access_token(self):
        self.__fetching = True
        appId = 'wx409ea91846084740'
        appSecret = 'b7af92994d51d1915d0c9c2a28ea3d9e'

        postUrl = ('https://api.weixin.qq.com/cgi-bin/token?grant_type='
                   'client_credential&appid=%s&secret=%s' % (appId, appSecret))

        async with ClientSession() as session:
            async with session.get(postUrl) as resp:
                urlResp = await resp.json()
                self.__accessToken = urlResp['access_token']
                self.__leftTime = urlResp['expires_in']
                self.__fetching = False

    async def get_access_token(self):
        if self.__leftTime < 10 and not self.__fetching:
            await self.__real_get_access_token()
        return self.__accessToken

    async def run(self):
        while (True):
            if self.__leftTime > 10 or self.__fetching:
                await asyncio.sleep(2)
                self.__leftTime -= 2
            else:
                await self.__real_get_access_token()
