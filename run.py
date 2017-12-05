#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from aiohttp import web

sys.path.append('src/')

from app import app

port = 9000
web.run_app(app, port=port)
