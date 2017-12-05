#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Default configurations.
'''

__author__ = 'Shawling'

configs = {
    # 'debug': True,
    'debug': False,
    # db默认数据库配置
    'db': {
        'default': {
            'host': '120.76.191.48',
            # 'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            # 'password': 'tangbo',
            # 'password': 'SHAWling123',
            'password': '',
            'db': 'rumi-serial'
        },
        'szrumi': {
            'host': '120.76.191.48',
            # 'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            # 'password': 'tangbo',
            # 'password': 'SHAWling123',
            'password': '',
            'db': 'szrumi'
        },
    },
    'cookie_key': 'rumi-serial'
}