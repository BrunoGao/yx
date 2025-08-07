#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置
支持多环境配置管理
"""

import os
import urllib.parse
from datetime import timedelta
from dotenv import load_dotenv

# 加载config.env文件
load_dotenv('config.env')

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Redis配置 - 从config.env读取
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    # 解析Redis URL获取host和port
    _redis_parsed = urllib.parse.urlparse(REDIS_URL)
    REDIS_HOST = _redis_parsed.hostname or 'localhost'
    REDIS_PORT = _redis_parsed.port or 6379
    
    # 日志配置 - 从config.env读取
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'
    
    # 数据库配置 - 从config.env读取，处理特殊字符
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or '127.0.0.1'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '123456'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'test'
    
    APP_PORT = int(os.environ.get('APP_PORT', 8080)) # 右侧注释：应用端口
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    password = urllib.parse.quote_plus(Config.MYSQL_PASSWORD)  # 使用quote_plus编码密码
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{Config.MYSQL_USER}:{password}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}?charset=utf8mb4"

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # 使用内存数据库进行测试

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    password = urllib.parse.quote_plus(Config.MYSQL_PASSWORD)  # 使用quote_plus编码密码
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{Config.MYSQL_USER}:{password}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}?charset=utf8mb4"
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 生产环境日志配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(cls.LOG_FILE, maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('LJWX BigScreen startup')

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """获取配置类"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, config['default']) 