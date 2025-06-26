import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Determine if running in Docker
IS_DOCKER = os.getenv('IS_DOCKER', 'true').lower() == 'true'

# Database configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '123456')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'lj-06')

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '123456')  # Redis密码配置

# Application configuration
APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = int(os.getenv('APP_PORT', 8001))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ==================== 客户定制化UI配置 ====================
# 客户可以直接修改以下配置来定制大屏界面

# 大屏标题 - 显示在页面顶部
BIGSCREEN_TITLE = os.getenv('BIGSCREEN_TITLE', '智能穿戴演示大屏')

# 公司信息
COMPANY_NAME = os.getenv('COMPANY_NAME', '智能科技有限公司')
COMPANY_LOGO_URL = os.getenv('COMPANY_LOGO_URL', '/static/images/logo.png')

# 主题配色
THEME_COLOR = os.getenv('THEME_COLOR', '#1890ff')  # 主色调
BACKGROUND_COLOR = os.getenv('BACKGROUND_COLOR', '#0a0e27')  # 背景色

# 页脚信息
FOOTER_TEXT = os.getenv('FOOTER_TEXT', '© 2024 智能科技有限公司 版权所有')

# Build database URI with proper password encoding
encoded_password = quote_plus(MYSQL_PASSWORD)
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 
    f"mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")

# 压力测试配置
STRESS_TEST_CONFIG = {
    'URL': 'http://localhost:5001/upload_health_data',
    'BASE_ID': 'A5GTQ24B26000732',
    'DEVICE_COUNT': 500,
    'INTERVAL': 5,
    'MAX_WORKERS': 50,
    'TIMEOUT': 10,
    'TARGET_QPS': 200,
    'QUEUE_SIZE': 10000,
}

# MySQL监控配置
MYSQL_CONFIG = {
    'host': MYSQL_HOST,
    'user': MYSQL_USER, 
    'password': MYSQL_PASSWORD,
    'db': MYSQL_DATABASE,
    'port': MYSQL_PORT,
    'charset': 'utf8mb4'
}

# 数据库连接池配置
DB_POOL_CONFIG = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

# 性能优化配置
PERFORMANCE_CONFIG = {
    'batch_size': 100,
    'batch_timeout': 2,
    'async_workers': 10,
    'redis_pipeline_size': 50,
    'enable_compression': True,
}

# 健康数据范围配置
HEALTH_DATA_RANGES = {
    'heart_rate': (60, 120),
    'blood_oxygen': (95, 100),
    'body_temperature': (36.0, 37.5),
    'blood_pressure_systolic': (110, 140),
    'blood_pressure_diastolic': (70, 90),
    'step': (800, 1500),
    'distance': (500, 1000),
    'calorie': (40000, 50000),
    'latitude': (22.5, 22.6),
    'longitude': (114.0, 114.3),
    'stress': (30, 80),
}

# ==================== 企业微信告警配置 ====================
# 企业微信告警相关配置，如不使用可设置为空字符串
CORP_ID = os.getenv('CORP_ID', 'wwde8dcde15c6b9657')  # 企业ID
CORP_SECRET = os.getenv('CORP_SECRET', 'C8MfcXQvHb2Lf-sDWITNjEVGnFrNGsKhOAU_d8nwR38')  # 应用密钥
CORP_AGENT_ID = os.getenv('CORP_AGENT_ID', '1000002')  # 应用AgentId
CORP_API_URL = os.getenv('CORP_API_URL', 'https://qyapi.weixin.qq.com')  # 企业微信API地址
CORP_WECHAT_ENABLED = os.getenv('CORP_WECHAT_ENABLED', 'true').lower() == 'true'  # 是否启用企业微信告警
CORP_WECHAT_TOUSER = os.getenv('CORP_WECHAT_TOUSER', '@all')  # 接收人，@all表示全部成员

# ==================== 微信小程序配置 ====================
# 微信小程序相关配置，如不使用可设置为空字符串
WECHAT_APP_ID = os.getenv('WECHAT_APP_ID', 'wx10dcc9f0235e1d77')  # 微信小程序AppID
WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET', 'b7e9088f3f5fe18a9cfb990c641138b3')  # 微信小程序密钥
WECHAT_TEMPLATE_ID = os.getenv('WECHAT_TEMPLATE_ID', 'oJpIEzSJW67s-W_tDTbnB5uS1biiglLH5jcaALofujk')  # 微信模板消息ID
WECHAT_USER_OPENID = os.getenv('WECHAT_USER_OPENID', 'ofYhV6W_mDuDnm8lVbgVbgEMtvWc')  # 微信用户OpenID
WECHAT_API_URL = os.getenv('WECHAT_API_URL', 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={ACCESS_TOKEN}')  # 微信API地址
WECHAT_ALERT_ENABLED = os.getenv('WECHAT_ALERT_ENABLED', 'true').lower() == 'true'  # 是否启用微信告警 