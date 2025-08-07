#!/usr/bin/env python3
"""数据库配置文件 - utils目录专用"""
import os

# MySQL配置
MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')  # 宿主MySQL
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'aV5mV7kQ!@#')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'lj-06')

# Redis配置
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'info')

print(f"📊 数据库配置: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
print(f"🔧 Redis配置: {REDIS_HOST}:{REDIS_PORT}")
