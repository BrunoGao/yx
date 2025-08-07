#!/usr/bin/env python3
"""单设备上传测试 - 快速诊断性能问题"""
import requests
import time
import json

API_BASE = "http://localhost:5001"

def test_single_device():
    """测试单个设备上传的性能"""
    device_data = {
        'System Software Version': 'ARC-AL00CN 4.0.3.248(SP59C269E624R246P867)',
        'Wifi Address': '89:09:cb:66:03:f4',
        'Bluetooth Address': 'E7:A0:9D:DB:58:41',
        'IP Address': '192.168.203.98\\nfe80::6c:81ff:fefc:a38b',
        'Network Access Mode': 2,
        'SerialNumber': 'TEST_DEVICE_001',
        'Device Name': 'HUAWEI WATCH FIT 3-F4G',
        'IMEI': '502044953985985',
        'batteryLevel': 80,
        'voltage': 3915,
        'chargingStatus': 'NONE',
        'status': 'ACTIVE',
        'wearState': 0
    }
    
    print("🔍 开始单设备上传测试...")
    print(f"设备序列号: {device_data['SerialNumber']}")
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_BASE}/upload_device_info", 
            json=device_data, 
            timeout=60  # 增加超时到60秒用于诊断
        )
        
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        print(f"⏱️  响应时间: {duration}秒")
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 设备上传成功")
            return True
        else:
            print(f"❌ 设备上传失败: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        print(f"⏱️  超时时间: {duration}秒")
        print("❌ 请求超时")
        return False
    except Exception as e:
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        print(f"⏱️  异常时间: {duration}秒")
        print(f"❌ 请求异常: {e}")
        return False

def test_api_health():
    """测试API健康状态"""
    try:
        response = requests.get(f"{API_BASE}/test", timeout=5)
        print(f"🏥 API健康检查: {response.status_code}")
        return response.status_code in [200, 404]
    except Exception as e:
        print(f"❌ API健康检查失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 LJWX 单设备上传性能测试")
    print("=" * 50)
    
    # 健康检查
    if not test_api_health():
        print("❌ API服务器不可用，退出测试")
        exit(1)
    
    # 单设备测试
    success = test_single_device()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 测试完成 - 设备上传成功")
    else:
        print("❌ 测试完成 - 设备上传失败")
    print("=" * 50) 