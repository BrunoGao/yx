#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LJWX BigScreen WSGI入口
生产环境使用
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# 创建应用实例
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == "__main__":
    app.run() 