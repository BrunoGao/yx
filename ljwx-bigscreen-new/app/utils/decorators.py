#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具装饰器
API请求日志记录等通用装饰器
"""

import functools
import time
from flask import request, current_app, g

def log_api_request(endpoint, method):
    """
    API请求日志装饰器
    记录请求信息和响应时间
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # 记录请求开始时间
            start_time = time.time()
            
            # 记录请求信息
            current_app.logger.info(
                f"📍 API请求: {method} {endpoint} | "
                f"IP: {request.remote_addr} | "
                f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
            )
            
            # 执行原函数
            try:
                result = f(*args, **kwargs)
                
                # 计算响应时间
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                
                # 记录成功响应
                current_app.logger.info(
                    f"✅ API响应: {method} {endpoint} | "
                    f"响应时间: {response_time:.2f}ms"
                )
                
                return result
                
            except Exception as e:
                # 计算响应时间
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                # 记录错误响应
                current_app.logger.error(
                    f"❌ API错误: {method} {endpoint} | "
                    f"响应时间: {response_time:.2f}ms | "
                    f"错误: {str(e)}"
                )
                
                raise
        
        return decorated_function
    return decorator

def require_json(f):
    """
    要求JSON数据装饰器
    确保请求包含有效的JSON数据
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            current_app.logger.warning(f"⚠️ 非JSON请求: {request.endpoint}")
            return {'error': '请求必须包含JSON数据'}, 400
        return f(*args, **kwargs)
    return decorated_function 