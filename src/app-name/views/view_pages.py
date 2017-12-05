#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Shawling'

' url handlers '

import time
import aiohttp
from aiohttp import web
from config import configs
from coroweb import get, post
from models import EvaluateMap
from aiohttp_session import get_session


@get('/')
async def index(request):
    # return 'redirect:/people'
    session = await get_session(request)
    json = {
        'last_visit': session.get('last_visit', None)
    }
    session['last_visit'] = time.time()
    return json


@get('/people')
async def people():
    model = await EvaluateMap.findAll()
    return {model[0].id}


@get('/ws')
async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws