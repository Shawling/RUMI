#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import os
import sys
import time
from datetime import datetime


def scan_handles_dir(path):
    for dir in os.listdir(path):
        childDir = os.path.join(path, dir)
        if os.path.isdir(childDir):
            scan_handles_dir(childDir)
            if childDir not in sys.path:
                sys.path.append(childDir)


scan_handles_dir(os.path.dirname(os.path.abspath(__file__)))

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

import coroweb
from coroweb import logger
import orm
from config import configs
from atfetcher import atfetcher


def init_jinja2(app, path, **kw):
    logger.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True))
    logger.info('set jinja2 template path: %s' % path)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(path),
        filters=kw.get('filters', None),
        **options)


def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


async def creat_db(app):
    for key, value in configs['db'].items():
        await orm.create_pool(app, db_name=key, **value)


async def close_db(app):
    logger.info('closing db connection...')


async def wx_fetch_accesstoken(app):
    app['wx_atfetcher'] = atfetcher()
    app.loop.create_task(app['wx_atfetcher'].run())


def init_app():
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    app = web.Application(middlewares=[
        session_middleware(EncryptedCookieStorage(secret_key)),
        coroweb.logger_factory, coroweb.response_factory
    ])

    init_jinja2(
        app,
        path=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'app-name/templates'),
        filters=dict(datetime=datetime_filter),
    )

    coroweb.scan_handles_dir(app,
                             os.path.join(
                                 os.path.dirname(os.path.abspath(__file__)),
                                 'app-name/views'))
    coroweb.add_static(app,
                       os.path.join(
                           os.path.dirname(os.path.abspath(__file__)),
                           'app-name/resources'), 'resources')

    app.on_startup.append(creat_db)
    app.on_startup.append(wx_fetch_accesstoken)
    app.on_cleanup.append(close_db)

    return app


app = init_app()