#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BigScreen大屏蓝图
主要大屏功能模块
"""

from flask import Blueprint

# 创建大屏蓝图
bigscreen_bp = Blueprint('bigscreen', __name__, 
                        template_folder='templates',
                        static_folder='static')

# 导入路由
from . import routes 