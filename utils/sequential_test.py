#!/usr/bin/env python3
"""顺序设备上传测试 - 不使用并发"""
import requests
import time

API_BASE = "http://localhost:5001"

def test_sequential_devices(count=5):
    """顺序测试多个设备上传"""
    print(f"🔍 开始顺序上传{count}个设备...")
    
    results = []
    total_start = time.time()
    
    for i in range(1, count + 1):
        device_data = {
            'System Software Version': f'ARC-AL00CN 4.0.3.248(SP59C269E624R246P{str(i).zfill(3)})',
            'Wifi Address': f'89:09:cb:66:03:{str(i).zfill(2)}',
            'Bluetooth Address': f'E7:A0:9D:DB:58:{str(i).zfill(2)}',
            'IP Address': f'192.168.203.{98+i}\\nfe80::6c:81ff:fefc:a38b',
            'Network Access Mode': 2,
            'SerialNumber': f'SEQ_TEST_{str(i).zfill(3)}',
            'Device Name': 'HUAWEI WATCH FIT 3-F4G',
            'IMEI': f'50204495398{str(i).zfill(4)}',
            'batteryLevel': 80 + i,
            'voltage': 3915 + i,
            'chargingStatus': 'NONE',
            'status': 'ACTIVE',
            'wearState': 0
        }
        
        print(f"📱 上传设备 {i}/{count}: {device_data['SerialNumber']}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_BASE}/upload_device_info", 
                json=device_data, 
                timeout=30
            )
            
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            if response.status_code == 200:
                print(f"  ✅ 成功 - {duration}秒")
                results.append({'device': i, 'duration': duration, 'success': True})
            else:
                print(f"  ❌ 失败 - {duration}秒 - {response.status_code}")
                results.append({'device': i, 'duration': duration, 'success': False})
                
        except Exception as e:
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            print(f"  ❌ 异常 - {duration}秒 - {e}")
            results.append({'device': i, 'duration': duration, 'success': False})
        
        # 短暂间隔避免压力过大
        time.sleep(0.5)
    
    total_end = time.time()
    total_duration = round(total_end - total_start, 2)
    
    # 统计结果
    success_count = sum(1 for r in results if r['success'])
    avg_duration = round(sum(r['duration'] for r in results) / len(results), 2)
    max_duration = max(r['duration'] for r in results)
    min_duration = min(r['duration'] for r in results)
    
    print("\n" + "=" * 50)
    print("📊 测试结果统计:")
    print(f"  总设备数: {count}")
    print(f"  成功数量: {success_count}")
    print(f"  失败数量: {count - success_count}")
    print(f"  总耗时: {total_duration}秒")
    print(f"  平均耗时: {avg_duration}秒")
    print(f"  最快响应: {min_duration}秒")
    print(f"  最慢响应: {max_duration}秒")
    print("=" * 50)
    
    return success_count == count

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 LJWX 顺序设备上传测试")
    print("=" * 50)
    
    # 测试5个设备
    success = test_sequential_devices(5)
    
    if success:
        print("✅ 所有设备上传成功")
    else:
        print("❌ 部分设备上传失败") 