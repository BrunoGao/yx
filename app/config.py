import os

class Config:
    """应用配置类"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///bigscreen.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis配置
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
    REDIS_DB = int(os.environ.get('REDIS_DB') or 0)
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    
    # 应用配置
    APP_HOST = os.environ.get('APP_HOST') or '0.0.0.0'
    APP_PORT = int(os.environ.get('APP_PORT') or 5000)
    
    # 大屏配置
    BIGSCREEN_TITLE = os.environ.get('BIGSCREEN_TITLE') or '健康监测大屏'
    COMPANY_NAME = os.environ.get('COMPANY_NAME') or '健康科技'
    COMPANY_LOGO_URL = os.environ.get('COMPANY_LOGO_URL') or '/static/images/logo.png'
    THEME_COLOR = os.environ.get('THEME_COLOR') or '#1890ff'
    BACKGROUND_COLOR = os.environ.get('BACKGROUND_COLOR') or '#001529'
    FOOTER_TEXT = os.environ.get('FOOTER_TEXT') or '© 2024 健康科技. All rights reserved.'
    
    # 微信配置
    WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID')
    WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET')
    WECHAT_TEMPLATE_ID = os.environ.get('WECHAT_TEMPLATE_ID')
    WECHAT_USER_OPENID = os.environ.get('WECHAT_USER_OPENID')
    WECHAT_API_URL = os.environ.get('WECHAT_API_URL') or 'https://api.weixin.qq.com'
    WECHAT_ALERT_ENABLED = os.environ.get('WECHAT_ALERT_ENABLED', 'False').lower() == 'true' 