#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Shawling'

import asyncio
import functools
import inspect
import json
import os
import sys
from urllib import parse

import aiohttp_jinja2
import jinja2
from aiohttp import web


def get(path):
    '''
    Define decorator @get('/path')
    '''

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper

    return decorator


def post(path):
    '''
    Define decorator @post('/path')
    '''

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper

    return decorator


class APIError(Exception):
    def __init__(self, code, message='', para=''):
        super(APIError, self).__init__(message)
        self.code = code
        self.message = message
        self.para = para


@web.middleware
async def logger_factory(request, handler):
    logger.info('Request: %s %s' % (request.method, request.path))
    return await handler(request)


@web.middleware
async def response_factory(request, handler):
    logger.debug('Response handler...')
    r = await handler(request)
    if isinstance(r, web.StreamResponse):
        return r
    if isinstance(r, bytes):
        resp = web.Response(body=r)
        resp.content_type = 'application/octet-stream'
        return resp
    if isinstance(r, str):
        # 是否包含重定向方法
        if r.startswith('redirect:'):
            return web.HTTPFound(r[9:])
        resp = web.Response(body=r.encode('utf-8'))
        resp.content_type = 'text/html;charset=utf-8'
        return resp
    if isinstance(r, dict):
        template = r.get('__template__')
        if template is None:
            r['req'] = str(request.rel_url)
            return web.json_response(r)
        else:
            resp = aiohttp_jinja2.render_template(template, request, r)
            return resp
    if isinstance(r, int) and r >= 100 and r < 600:
        # 返回Response Code
        return web.Response(status=r)
    # default:
    resp = web.Response(body=str(r).encode('utf-8'))
    resp.content_type = 'text/plain;charset=utf-8'
    return resp


def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True


def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True


def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL
                      and param.kind != inspect.Parameter.KEYWORD_ONLY
                      and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError(
                'request parameter must be the last named parameter in function: %s%s'
                % (fn.__name__, str(sig)))
    return found


# 初步取出参数，并对参数进行简单处理
class RequestHandler(object):
    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest(reason='Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest(reason='JSON Format Error.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded'
                                   ) or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest(
                        reason='Unsupported Content-Type: %s' % request.
                        content_type)
            if request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args:
                # remove all unamed kw:
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k, v in request.match_info.items():
                if k in kw:
                    logger.warning(
                        'Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        # check required kw:
        if self._required_kw_args:
            for name in self._required_kw_args:
                if name not in kw:
                    return web.HTTPBadRequest(
                        reason='Missing argument: %s' % name)
        logger.info('call with args: %s' % str(kw))
        try:
            # 根据获取到的参数调用处理函数，api函数执行过程中产生的错误通过APIError raise，并形成JSON返回
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(errcode=e.code, errmsg=e.message, err_para=e.para)


def add_static(app, path, webRef):
    app.router.add_static('/%s/' % webRef, path)
    logger.info('add resources /%s/ => %s' % (webRef, path))


# 根据封装在fn中的方法与路径构建路由
def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(
            fn):
        fn = asyncio.coroutine(fn)
    logger.info('add route %s %s => %s(%s)' %
                (method, path, fn.__name__,
                 ', '.join(inspect.signature(fn).parameters.keys())))

    app.router.add_route(method, path, RequestHandler(app, fn))


# 遍历文件中的函数
def add_routes(app, module_home_path, module_name):
    if module_home_path not in sys.path:
        sys.path.append(module_home_path)
    if module_name not in sys.modules:
        n = module_name.rfind('.')
        # 如果没有找到
        if n == (-1):
            mod = __import__(module_name, globals(), locals())
        else:
            name = module_name[n + 1:]
            mod = getattr(
                __import__(module_name[:n], globals(), locals(), [name]), name)
        for attr in dir(mod):
            if attr.startswith('_'):
                continue
            fn = getattr(mod, attr)
            if callable(fn):
                method = getattr(fn, '__method__', None)
                path = getattr(fn, '__route__', None)
                if method and path:
                    add_route(app, fn)


# 递归遍历目录下view_开头的py文件
def scan_handles_dir(app, path):
    for dir in os.listdir(path):
        childDir = os.path.join(path, dir)
        if os.path.isdir(childDir):
            scan_handles_dir(app, childDir)
        else:
            if childDir[-2:] == 'py' and dir[:5] == 'view_':
                add_routes(app, path, dir[:-3])


def initlog(log_path):
    import logging
    import logging.handlers
    import os

    # 生成一个日志对象
    logger = logging.getLogger()
    # 生成一个Handler。logging支持许多Handler，例如FileHandler, SocketHandler,
    # SMTPHandler等，我由于要写文件就使用了FileHandler。
    # LOG_FILE是一个全局变量，它就是一个文件名，如：'crawl.log'

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # WARNING级别日志
    log_levels = ['debug', 'info', 'warning', 'error', 'critical']
    levelDict = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }

    # Filter过滤，只有level相同才输出
    class LogLevelFilter(logging.Filter):
        def __init__(self, name='', level=logging.DEBUG):
            super(LogLevelFilter, self).__init__(name)
            self.level = level

        def filter(self, record):
            return record.levelno == self.level

    for level in log_levels:
        PATH = os.path.join(log_path, level)
        if not os.path.exists(PATH):
            os.makedirs(PATH)
        FILE = os.path.join(PATH, '%s.log' % level)
        # 每天生成一个文件，最多30个文件
        hdlr = logging.handlers.TimedRotatingFileHandler(
            FILE, when='D', interval=1, backupCount=30)
        # 生成一个格式器，用于规范日志的输出格式。如果没有这行代码，那么缺省的
        # 格式就是："%(message)s"。也就是写日志时，信息是什么日志中就是什么，
        # 没有日期，没有信息级别等信息。logging支持许多种替换值，详细请看
        # Formatter的文档说明。这里有三项：时间，信息级别，日志信息
        formatter = logging.Formatter('%(asctime)s %(message)s')
        # 将格式器设置到处理器上
        hdlr.setFormatter(formatter)
        # 设置日志级别
        hdlr.setLevel(levelDict[level])
        # 设置日志只包含本级别
        filter = LogLevelFilter(level=levelDict[level])
        hdlr.addFilter(filter)
        # 将处理器加到日志对象上
        logger.addHandler(hdlr)

    # 添加控制台logger
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    # 设置日志信息输出的级别。logging提供多种级别的日志信息，如：NOTSET,
    # DEBUG, INFO, WARNING, ERROR, CRITICAL等。每个级别都对应一个数值。
    # 如果不执行此句，缺省为30(WARNING)。可以执行：logging.getLevelName
    # (logger.getEffectiveLevel())来查看缺省的日志级别。日志对象对于不同
    # 的级别信息提供不同的函数进行输出，如：info(), error(), debug()等。当
    # 写入日志时，小于指定级别的信息将被忽略。因此为了输出想要的日志级别一定
    # 要设置好此参数。这里我设为NOTSET（值为0），也就是想输出所有信息
    consoleHandler.setLevel(logging.DEBUG)

    # 顶级控制最低log级别
    logger.setLevel(logging.DEBUG)

    return logger


logger = initlog('/log/app')