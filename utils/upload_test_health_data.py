#!/usr/bin/env python3
import requests
import json
import random
from datetime import datetime, timedelta

# 部门1923231005240295439的用户设备
USER_DEVICES = [
    {'name': '中学', 'device_sn': 'A5GTQ2460300053'},
    {'name': '小学', 'device_sn': 'A5GTQ24919001193'}
]

API_URL = "http://localhost:5001/upload_health_data"

def generate_health_data(device_sn, timestamp):
    """生成健康数据"""
    return {
        'id': device_sn,
        'upload_method': 'wifi',
        'heart_rate': random.randint(60, 100),
        'blood_oxygen': random.randint(96, 100),
        'body_temperature': f"{random.uniform(36.2, 37.2):.1f}",
        'blood_pressure_systolic': random.randint(110, 130),
        'blood_pressure_diastolic': random.randint(70, 85),
        'step': random.randint(1000, 3000),
        'distance': f"{random.uniform(800, 2500):.1f}",
        'calorie': f"{random.uniform(30000, 60000):.1f}",
        'latitude': f"{22.5500 + random.uniform(-0.001, 0.001):.6f}",
        'longitude': f"{114.0500 + random.uniform(-0.001, 0.001):.6f}",
        'altitude': '0.0',
        'stress': random.randint(20, 60),
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'sleepData': '{"code":0,"data":[{"endTimeStamp":1747440420000,"startTimeStamp":1747418280000,"type":2}],"name":"sleep","type":"history"}',
        'exerciseDailyData': '{"code":0,"data":[{"strengthTimes":2,"totalTime":5}],"name":"daily","type":"history"}',
        'exerciseWeekData': 'null',
        'scientificSleepData': 'null',
        'workoutData': '{"code":0,"data":[],"name":"workout","type":"history"}'
    }

def upload_test_data():
    """上传测试数据"""
    success_count = 0
    error_count = 0
    
    print("🧪 开始上传健康数据测试...")
    
    # 为每个用户上传5个数据点
    for user in USER_DEVICES:
        print(f"\n👤 处理用户: {user['name']} ({user['device_sn']})")
        
        for i in range(5):
            # 生成过去24小时内的随机时间点
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 24))
            data = generate_health_data(user['device_sn'], timestamp)
            
            try:
                response = requests.post(API_URL, json={'data': data}, timeout=10)
                if response.status_code == 200:
                    success_count += 1
                    print(f"  ✅ 第{i+1}个数据点上传成功")
                else:
                    error_count += 1
                    print(f"  ❌ 第{i+1}个数据点上传失败: HTTP {response.status_code}")
            except Exception as e:
                error_count += 1
                print(f"  ❌ 第{i+1}个数据点上传异常: {e}")
    
    print(f"\n📊 上传结果:")
    print(f"  ✅ 成功: {success_count}个")
    print(f"  ❌ 失败: {error_count}个")
    
    if error_count == 0:
        print("\n🎉 所有测试数据上传成功!")
        return True
    else:
        print(f"\n⚠️ 有{error_count}个数据点上传失败")
        return False

def upload_week_data():
    """上传过去一周的数据"""
    print("\n📅 开始上传过去一周的数据...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    total_success = 0
    total_error = 0
    
    for user in USER_DEVICES:
        print(f"\n👤 处理用户: {user['name']}")
        current_time = start_date
        user_success = 0
        user_error = 0
        
        while current_time < end_date:
            data = generate_health_data(user['device_sn'], current_time)
            
            try:
                response = requests.post(API_URL, json={'data': data}, timeout=10)
                if response.status_code == 200:
                    user_success += 1
                    total_success += 1
                else:
                    user_error += 1
                    total_error += 1
                    if user_error > 10:  # 连续错误太多则跳过
                        print(f"  ⚠️ 错误过多，跳过用户 {user['name']}")
                        break
            except Exception as e:
                user_error += 1
                total_error += 1
                if user_error > 10:
                    print(f"  ⚠️ 异常过多，跳过用户 {user['name']}: {e}")
                    break
            
            current_time += timedelta(minutes=5)
            
            if total_success % 100 == 0 and total_success > 0:
                print(f"  📈 已处理 {total_success} 个数据点...")
        
        print(f"  ✅ {user['name']} 完成: 成功{user_success}个, 失败{user_error}个")
    
    print(f"\n🎉 一周数据上传完成!")
    print(f"📊 总计: 成功{total_success}个, 失败{total_error}个")

if __name__ == "__main__":
    print("=== 健康数据上传测试 ===")
    print(f"目标用户: {[f'{u['name']}({u['device_sn']})' for u in USER_DEVICES]}")
    
    # 先测试5个数据点
    if upload_test_data():
        choice = input("\n是否继续上传过去一周的数据? (y/N): ")
        if choice.lower() == 'y':
            upload_week_data()
        else:
            print("仅完成测试数据上传")
    else:
        print("测试失败，请检查服务状态") 