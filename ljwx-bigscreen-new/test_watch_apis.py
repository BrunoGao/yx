#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watch端接口测试脚本
测试五个核心接口功能
"""

import requests
import json
import time

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_DEVICE_SN = "TEST_DEVICE_001"
TEST_USER_ID = "TEST_USER_001"
TEST_CUSTOMER_ID = "TEST_CUSTOMER_001"
TEST_ORG_ID = "TEST_ORG_001"

def test_health_data_upload():
    """测试健康数据上传接口"""
    print("=" * 50)
    print("测试健康数据上传接口")
    print("=" * 50)
    
    url = f"{BASE_URL}/watch/upload_health_data"
    
    # 测试数据1: 单个健康数据
    test_data1 = {
        "data": {
            "deviceSn": TEST_DEVICE_SN,
            "userId": TEST_USER_ID,
            "orgId": TEST_ORG_ID,
            "heartRate": 75,
            "pressureHigh": 120,
            "pressureLow": 80,
            "bloodOxygen": 98,
            "temperature": 36.5,
            "latitude": 39.9042,
            "longitude": 116.4074,
            "timestamp": "2024-01-15T10:30:00"
        }
    }
    
    # 测试数据2: 多个健康数据
    test_data2 = {
        "data": [
            {
                "deviceSn": TEST_DEVICE_SN,
                "userId": TEST_USER_ID,
                "orgId": TEST_ORG_ID,
                "heartRate": 72,
                "pressureHigh": 118,
                "pressureLow": 78,
                "bloodOxygen": 97,
                "temperature": 36.3,
                "latitude": 39.9042,
                "longitude": 116.4074,
                "timestamp": "2024-01-15T10:35:00"
            },
            {
                "deviceSn": TEST_DEVICE_SN,
                "userId": TEST_USER_ID,
                "orgId": TEST_ORG_ID,
                "heartRate": 78,
                "pressureHigh": 125,
                "pressureLow": 82,
                "bloodOxygen": 96,
                "temperature": 36.7,
                "latitude": 39.9042,
                "longitude": 116.4074,
                "timestamp": "2024-01-15T10:40:00"
            }
        ]
    }
    
    try:
        # 测试单个数据
        print("测试单个健康数据上传...")
        response1 = requests.post(url, json=test_data1, headers={'Content-Type': 'application/json'})
        print(f"状态码: {response1.status_code}")
        print(f"响应: {response1.json()}")
        
        time.sleep(1)
        
        # 测试多个数据
        print("\n测试多个健康数据上传...")
        response2 = requests.post(url, json=test_data2, headers={'Content-Type': 'application/json'})
        print(f"状态码: {response2.status_code}")
        print(f"响应: {response2.json()}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

def test_device_info_upload():
    """测试设备信息上传接口"""
    print("\n" + "=" * 50)
    print("测试设备信息上传接口")
    print("=" * 50)
    
    url = f"{BASE_URL}/watch/upload_device_info"
    
    test_data = {
        "SerialNumber": TEST_DEVICE_SN,
        "deviceName": "测试智能手表",
        "customerId": TEST_CUSTOMER_ID,
        "status": "online"
    }
    
    try:
        response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

def test_common_event_upload():
    """测试通用事件上传接口"""
    print("\n" + "=" * 50)
    print("测试通用事件上传接口")
    print("=" * 50)
    
    url = f"{BASE_URL}/watch/upload_common_event"
    
    test_data = {
        "eventType": "heart_rate_alert",
        "deviceSn": TEST_DEVICE_SN,
        "eventValue": "心率异常: 120次/分钟",
        "customerId": TEST_CUSTOMER_ID,
        "userId": TEST_USER_ID,
        "orgId": TEST_ORG_ID,
        "severityLevel": "warning"
    }
    
    try:
        response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

def test_device_message_send():
    """测试设备消息发送接口"""
    print("\n" + "=" * 50)
    print("测试设备消息发送接口")
    print("=" * 50)
    
    url = f"{BASE_URL}/watch/send_device_message"
    
    test_data = {
        "deviceSn": TEST_DEVICE_SN,
        "customerId": TEST_CUSTOMER_ID,
        "userId": TEST_USER_ID,
        "orgId": TEST_ORG_ID,
        "message": "这是一条测试消息",
        "message_type": "notification",
        "sender_type": "system",
        "receiver_type": "device",
        "message_status": "sent",
        "department_info": "技术部"
    }
    
    try:
        response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

def test_device_message_receive():
    """测试设备消息接收接口"""
    print("\n" + "=" * 50)
    print("测试设备消息接收接口")
    print("=" * 50)
    
    url = f"{BASE_URL}/watch/receive_device_messages/{TEST_DEVICE_SN}"
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

def test_health_data_config():
    """测试健康数据配置获取接口"""
    print("\n" + "=" * 50)
    print("测试健康数据配置获取接口")
    print("=" * 50)
    
    url = f"{BASE_URL}/watch/health_data_config"
    params = {
        "customer_id": TEST_CUSTOMER_ID,
        "device_sn": TEST_DEVICE_SN
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")

def main():
    """主测试函数"""
    print("开始测试Watch端五个核心接口...")
    print(f"测试服务器: {BASE_URL}")
    print(f"测试设备SN: {TEST_DEVICE_SN}")
    
    # 测试五个核心接口
    test_health_data_upload()      # 接口1: 健康数据上传
    test_device_info_upload()      # 接口2: 设备信息上传
    test_common_event_upload()     # 接口3: 通用事件上传
    test_device_message_send()     # 接口4: 设备消息发送
    test_device_message_receive()  # 接口4: 设备消息接收
    test_health_data_config()      # 接口5: 健康数据配置
    
    print("\n" + "=" * 50)
    print("所有接口测试完成!")
    print("=" * 50)

if __name__ == "__main__":
    main() 