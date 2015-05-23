#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: lonewolf
# Date: 2015-04-09 23:33:09
#

#
# 格式化日志信息
#

import datetime


# 时间格式
_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# 获取时间
def get_time():
    return datetime.datetime.now().strftime(_TIME_FORMAT)


# 日志
def log(level, content):
    time = get_time()
    return "%s [%s] %s" % (time, level, content)
