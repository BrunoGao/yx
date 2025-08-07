#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LJWX BigScreen 开发环境启动
本地开发使用
"""

import os
from app import create_app

# 设置开发环境
os.environ.setdefault('FLASK_ENV', 'development')

# 创建应用实例
app = create_app('development')

if __name__ == '__main__':
    print("🚀 启动LJWX Bigscreen开发服务器")
    print(f"📊 数据库: {app.config['MYSQL_HOST']}:{app.config['MYSQL_PORT']}")
    print(f"🔧 Redis: {app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}")
    print("-" * 50)
    
    # 启动开发服务器
    app.run(
        host='0.0.0.0',
        port=app.config['APP_PORT'],
        debug=True,
        threaded=True
    ) 