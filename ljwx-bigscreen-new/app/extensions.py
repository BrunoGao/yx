#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用扩展
初始化Flask扩展
"""

from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
import redis
import logging
from logging.handlers import RotatingFileHandler
import os

# 数据库扩展
db = SQLAlchemy()

# Redis扩展
redis_client = FlaskRedis()

def init_extensions(app):
    """初始化所有扩展"""
    db.init_app(app)
    redis_client.init_app(app)
    
    # 日志
    init_logging(app)
    
    return app

def init_logging(app):
    """初始化日志系统"""
    if not app.debug and not app.testing:
        # 创建日志目录
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 文件日志处理器
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, app.config['LOG_FILE']),
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info('LJWX BigScreen应用启动')

def get_redis():
    """获取Redis客户端"""
    return redis_client 