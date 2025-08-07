from flask import Flask
from .config import Config
from .extensions import db, redis
import logging

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    redis.init_app(app)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    # 注册蓝图
    from .blueprints.watch import watch_bp
    from .blueprints.bigscreen import bigscreen_bp
    from .blueprints.api import api_bp
    
    app.register_blueprint(watch_bp)
    app.register_blueprint(bigscreen_bp)
    app.register_blueprint(api_bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app 