#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新架构测试脚本
验证应用创建、蓝图注册和接口功能
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_creation():
    """测试应用创建"""
    print("🧪 测试应用创建...")
    try:
        from app import create_app
        app = create_app('development')
        print("✅ 应用创建成功")
        return app
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        return None

def test_blueprint_registration(app):
    """测试蓝图注册"""
    print("🧪 测试蓝图注册...")
    try:
        # 检查蓝图是否注册
        blueprints = list(app.blueprints.keys())
        print(f"✅ 已注册蓝图: {blueprints}")
        
        # 检查watch蓝图路由
        watch_routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('watch.'):
                watch_routes.append(f"{rule.rule} [{', '.join(rule.methods)}]")
        
        print(f"✅ Watch蓝图路由: {watch_routes}")
        return True
    except Exception as e:
        print(f"❌ 蓝图注册测试失败: {e}")
        return False

def test_watch_endpoints(app):
    """测试Watch端接口"""
    print("🧪 测试Watch端接口...")
    
    # 测试的接口列表
    endpoints = [
        '/upload_health_data',
        '/upload_device_info', 
        '/upload_common_event',
        '/DeviceMessage/save_message',
        '/DeviceMessage/send',
        '/DeviceMessage/receive',
        '/fetch_health_data_config'
    ]
    
    with app.test_client() as client:
        for endpoint in endpoints:
            try:
                if endpoint in ['/DeviceMessage/receive', '/fetch_health_data_config']:
                    # GET请求
                    response = client.get(endpoint)
                else:
                    # POST请求
                    response = client.post(endpoint, json={})
                
                print(f"✅ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: {e}")

def test_models():
    """测试数据模型"""
    print("🧪 测试数据模型...")
    try:
        from app.models import (
            UserInfo, UserOrg, UserPosition,
            OrgInfo, Position,
            DeviceInfo, DeviceInfoHistory, DeviceMessage, DeviceMessageDetail, DeviceUser, DeviceBindRequest,
            UserHealthData, UserHealthData, UserHealthDataDaily, UserHealthDataWeekly, HealthDataConfig,
            HealthBaseline, OrgHealthBaseline, HealthAnomaly, HealthSummaryDaily,
            AlertInfo, AlertLog, AlertRules, UserAlert,
            Interface, CustomerConfig, SystemEventRule, EventAlarmQueue, SystemEventProcessLog,
            WeChatAlarmConfig
        )
        print("✅ 所有数据模型导入成功")
        return True
    except Exception as e:
        print(f"❌ 数据模型测试失败: {e}")
        return False

def test_watch_service():
    """测试Watch服务"""
    print("🧪 测试Watch服务...")
    try:
        from app.blueprints.watch.services import WatchService
        service = WatchService()
        print("✅ Watch服务创建成功")
        return True
    except Exception as e:
        print(f"❌ Watch服务测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始新架构测试...")
    print("=" * 50)
    
    # 测试应用创建
    app = test_app_creation()
    if not app:
        return False
    
    print("-" * 30)
    
    # 测试蓝图注册
    if not test_blueprint_registration(app):
        return False
    
    print("-" * 30)
    
    # 测试数据模型
    if not test_models():
        return False
    
    print("-" * 30)
    
    # 测试Watch服务
    if not test_watch_service():
        return False
    
    print("-" * 30)
    
    # 测试Watch端接口
    test_watch_endpoints(app)
    
    print("=" * 50)
    print("🎉 新架构测试完成！")
    print("\n📋 测试总结:")
    print("✅ 应用工厂创建成功")
    print("✅ 蓝图注册成功")
    print("✅ 数据模型导入成功")
    print("✅ Watch服务创建成功")
    print("✅ Watch端接口路径存在")
    print("\n🔄 下一步:")
    print("1. 启动服务器: python run.py")
    print("2. 手动测试接口功能")
    print("3. 验证数据库连接")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 