#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watch端接口蓝图
保持与原有接口的完全兼容性
"""

from flask import Blueprint

# 创建蓝图，使用空前缀确保与原接口路径一致
watch_bp = Blueprint('watch', __name__)

# 导入路由
from . import routes 