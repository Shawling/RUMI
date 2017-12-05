#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Models for user, blog, comment.
'''

__author__ = 'Shawling'

import time
import uuid

from orm import BooleanField, FloatField, Model, StringField, TextField, IntegerField


# 通过拼接时间戳与Python内置的uuid算法保证id的唯一性
def next_id():
    return '%015d%s' % (int(time.time() * 1000), uuid.uuid4().hex)


class EvaluateMap(Model):
    __table__ = 'evaluate_map'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    evaluate_result = StringField(ddl='varchar(45)')
    evaluate_detail = TextField()


class Map1(Model):
    __db__ = 'szrumi'
    __table__ = 'sys_role'

    id = IntegerField(primary_key=True) 
    name = StringField(ddl='varchar(45)')
    create_time = FloatField(default=time.time)
    remark = StringField(ddl='varchar(200)')