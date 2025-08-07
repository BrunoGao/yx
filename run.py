#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康大屏 Flask 启动入口
"""
import os
from app import create_app

if __name__ == '__main__':
    app = create_app()
    host = app.config.get('APP_HOST', '0.0.0.0')
    port = int(app.config.get('APP_PORT', 5000))
    debug = app.config.get('DEBUG', True)
    print(f"🚀 启动健康大屏服务器: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True) 