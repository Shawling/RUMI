#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Shawling'

' url handlers '

import hashlib

from aiohttp.web import Request

import receive
import reply
from coroweb import get, logger, post


@get('/wx')
async def wx_profile_setting(*, signature, timestamp, nonce, echostr):
    if not signature or not timestamp or not nonce or not echostr:
        return "hello, this is handle view"
    token = 'rumi-wesmart'
    l1 = [token, timestamp, nonce]
    l1.sort()
    sha1 = hashlib.sha1()
    for v in l1:
        sha1.update(v.encode('utf-8'))
    hashcode = sha1.hexdigest()
    if hashcode == signature:
        return echostr
    else:
        return 'auth failed'


@post('/wx')
async def wx_chat(request):
    xml = await request.read()
    recMsg = receive.parse_xml(xml)
    if isinstance(recMsg, receive.Msg):
        toUser = recMsg.FromUserName
        fromUser = recMsg.ToUserName
        if recMsg.MsgType == 'text':
            content = recMsg.Content.decode('utf-8')
            replyMsg = reply.TextMsg(toUser, fromUser, content)
            return replyMsg.send()
        if recMsg.MsgType == 'image':
            mediaId = recMsg.MediaId
            replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
            return replyMsg.send()
        else:
            return reply.Msg().send()
    else:
        return reply.Msg().send()
