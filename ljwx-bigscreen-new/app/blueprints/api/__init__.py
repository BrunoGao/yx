#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API蓝图
通用API接口模块
"""

from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 导入路由
from . import routes 