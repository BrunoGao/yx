#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API接口路由
"""

from flask import request, jsonify
from . import api_bp

@api_bp.route('/health')
def health():
    """API健康检查"""
    return jsonify({'status': 'ok', 'message': 'API服务运行正常'}) 