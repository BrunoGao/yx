#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用工厂
创建和配置Flask应用
"""

from flask import Flask
from .config import config
from .extensions import db, redis_client
from .models import *  # 导入所有模型

def create_app(config_name='development'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    redis_client.init_app(app)
    
    # 注册蓝图
    from .blueprints.watch import watch_bp
    from .blueprints.bigscreen import bigscreen_bp
    from .blueprints.api import api_bp
    
    # 注册watch蓝图（不添加URL前缀以保持路径兼容）
    app.register_blueprint(watch_bp)
    
    # 注册其他蓝图
    app.register_blueprint(bigscreen_bp, url_prefix='/bigscreen')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app

def register_blueprints(app):
    """注册所有蓝图"""
    from .blueprints.bigscreen import bigscreen_bp
    from .blueprints.api import api_bp
    from .blueprints.watch import watch_bp
    
    # 大屏主功能
    app.register_blueprint(bigscreen_bp)
    
    # API接口
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Watch端接口 - 不添加前缀，保持原有路径兼容性
    app.register_blueprint(watch_bp)

def register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500 