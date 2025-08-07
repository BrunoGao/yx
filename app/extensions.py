from flask_sqlalchemy import SQLAlchemy
import redis

# 数据库扩展
db = SQLAlchemy()

class RedisHelper:
    """Redis助手类"""
    
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
    
    def get(self, key):
        """获取值"""
        try:
            return self.redis.get(key)
        except Exception:
            return None
    
    def setex(self, key, ttl, value):
        """设置带过期时间的值"""
        try:
            return self.redis.setex(key, ttl, value)
        except Exception:
            return False
    
    def ping(self):
        """测试连接"""
        try:
            return self.redis.ping()
        except Exception:
            return False

# 创建Redis实例
redis = RedisHelper() 