#!/usr/bin/env python3
"""API接口测试验证器 - 测试接口并验证数据库插入"""
import requests,json,time,random
from datetime import datetime
import mysql.connector

# 配置
API_BASE = "http://localhost:8001"
DB_CONFIG = {'host':'127.0.0.1','user':'root','password':'aV5mV7kQ!@#','database':'lj-06','port':3306}

class APITestValidator:
    def __init__(self):
        self.session = requests.Session()
        
    def get_db_connection(self):
        """获取数据库连接"""
        return mysql.connector.connect(**DB_CONFIG)
    
    def test_device_info_api(self, test_data):
        """测试设备信息接口"""
        print(f"🔧 测试设备信息接口...")
        
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查设备是否已存在
        cursor.execute("SELECT COUNT(*) as count FROM t_device_info WHERE serial_number = %s", (test_data['SerialNumber'],))
        before_count = cursor.fetchone()['count']
        
        # 发送API请求
        start_time = time.time()
        try:
            response = self.session.post(f"{API_BASE}/upload_device_info", json=test_data, timeout=10)
            response_time = time.time() - start_time
            
            print(f"  ✅ 状态码: {response.status_code}, 响应时间: {response_time:.3f}s")
            
            if response.status_code == 200:
                # 验证数据库插入
                time.sleep(0.5)  # 等待数据库写入
                cursor.execute("SELECT COUNT(*) as count FROM t_device_info WHERE serial_number = %s", (test_data['SerialNumber'],))
                after_count = cursor.fetchone()['count']
                
                print(f"  📊 数据库: 插入前{before_count}条 -> 插入后{after_count}条")
                
                # 获取插入的记录详情
                cursor.execute("""
                    SELECT device_sn,device_name,battery_level,voltage,charging_status,wear_state,
                           system_version,wifi_address,bluetooth_address,created_time
                    FROM t_device_info WHERE serial_number = %s ORDER BY updated_time DESC LIMIT 1
                """, (test_data['SerialNumber'],))
                db_record = cursor.fetchone()
                
                if db_record:
                    print(f"  🔍 数据库记录: 设备{db_record['device_sn']}, 电量{db_record['battery_level']}%, 佩戴状态{db_record['wear_state']}")
                    return True
            else:
                print(f"  ❌ API调用失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def test_health_data_api(self, test_data):
        """测试健康数据接口"""
        print(f"💓 测试健康数据接口...")
        
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        device_sn = test_data['data']['id']
        
        # 检查健康数据记录数
        cursor.execute("SELECT COUNT(*) as count FROM health_data WHERE device_sn = %s", (device_sn,))
        before_count = cursor.fetchone()['count']
        
        start_time = time.time()
        try:
            response = self.session.post(f"{API_BASE}/upload_health_data", json=test_data, timeout=10)
            response_time = time.time() - start_time
            
            print(f"  ✅ 状态码: {response.status_code}, 响应时间: {response_time:.3f}s")
            
            if response.status_code == 200:
                time.sleep(0.5)
                cursor.execute("SELECT COUNT(*) as count FROM health_data WHERE device_sn = %s", (device_sn,))
                after_count = cursor.fetchone()['count']
                
                print(f"  📊 数据库: 插入前{before_count}条 -> 插入后{after_count}条")
                
                # 获取最新健康记录
                cursor.execute("""
                    SELECT device_sn,heart_rate,blood_oxygen,body_temperature,step_count,
                           latitude,longitude,stress_level,created_time
                    FROM health_data WHERE device_sn = %s ORDER BY created_time DESC LIMIT 1
                """, (device_sn,))
                db_record = cursor.fetchone()
                
                if db_record:
                    print(f"  🔍 健康数据: 心率{db_record['heart_rate']}, 血氧{db_record['blood_oxygen']}%, 体温{db_record['body_temperature']}°C")
                    return True
            else:
                print(f"  ❌ API调用失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def test_common_event_api(self, test_data):
        """测试通用事件接口"""
        print(f"📡 测试通用事件接口...")
        
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        device_sn = test_data['deviceSn']
        
        # 检查事件记录数
        cursor.execute("SELECT COUNT(*) as count FROM device_events WHERE device_sn = %s", (device_sn,))
        before_count = cursor.fetchone()['count']
        
        start_time = time.time()
        try:
            response = self.session.post(f"{API_BASE}/upload_common_event", json=test_data, timeout=10)
            response_time = time.time() - start_time
            
            print(f"  ✅ 状态码: {response.status_code}, 响应时间: {response_time:.3f}s")
            
            if response.status_code == 200:
                time.sleep(0.5)
                cursor.execute("SELECT COUNT(*) as count FROM device_events WHERE device_sn = %s", (device_sn,))
                after_count = cursor.fetchone()['count']
                
                print(f"  📊 数据库: 插入前{before_count}条 -> 插入后{after_count}条")
                
                # 获取最新事件记录
                cursor.execute("""
                    SELECT device_sn,event_type,event_value,created_time
                    FROM device_events WHERE device_sn = %s ORDER BY created_time DESC LIMIT 1
                """, (device_sn,))
                db_record = cursor.fetchone()
                
                if db_record:
                    print(f"  🔍 事件记录: 类型{db_record['event_type']}, 值{db_record['event_value']}")
                    return True
            else:
                print(f"  ❌ API调用失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def generate_test_data(self):
        """生成测试数据"""
        timestamp = datetime.now()
        device_sn = f"TEST{random.randint(10000,99999)}A"  # 使用测试设备号
        
        # 设备信息测试数据
        device_info = {
            'System Software Version': f'ARC-AL00CN 4.{random.randint(0,2)}.{random.randint(0,9)}.{random.randint(100,999)}',
            'Wifi Address': ':'.join([f'{random.randint(0,255):02x}' for _ in range(6)]),
            'Bluetooth Address': ':'.join([f'{random.randint(0,255):02X}' for _ in range(6)]),
            'IP Address': f'192.168.{random.randint(1,254)}.{random.randint(2,254)}',
            'Network Access Mode': random.choice([1, 2, 3]),
            'SerialNumber': device_sn,
            'Device Name': 'HUAWEI WATCH 4-DD6',
            'IMEI': f'{random.randint(100000000000000, 999999999999999)}',
            'batteryLevel': random.randint(20, 100),
            'voltage': random.randint(3500, 4200),
            'chargingStatus': random.choice(['NONE', 'CHARGING']),
            'status': 'ACTIVE',
            'wearState': random.choice([0, 1])
        }
        
        # 健康数据测试数据
        health_data = {
            'data': {
                'id': device_sn,
                'upload_method': 'wifi',
                'heart_rate': random.randint(60, 120),
                'blood_oxygen': random.randint(95, 100),
                'body_temperature': f"{random.uniform(36.0, 37.5):.1f}",
                'blood_pressure_systolic': random.randint(110, 140),
                'blood_pressure_diastolic': random.randint(70, 90),
                'step': random.randint(100, 2000),
                'distance': f"{random.uniform(100, 1000):.1f}",
                'calorie': f"{random.uniform(20000, 50000):.1f}",
                'latitude': f"{random.uniform(22.5, 22.6):.6f}",
                'longitude': f"{random.uniform(114.0, 114.1):.6f}",
                'altitude': '0.0',
                'stress': random.randint(20, 80),
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        # 通用事件测试数据
        common_event = {
            'eventType': 'com.tdtech.ohos.action.WEAR_STATUS_CHANGED',
            'eventValue': str(random.choice([0, 1])),
            'deviceSn': device_sn,
            'heatlhData': json.dumps({
                'data': {
                    'deviceSn': device_sn,
                    'heart_rate': random.randint(60, 120),
                    'blood_oxygen': random.randint(95, 100),
                    'body_temperature': '0.0',
                    'step': 0,
                    'distance': '0.0',
                    'calorie': '0.0',
                    'latitude': '0',
                    'longitude': '0',
                    'altitude': '0',
                    'stress': 0,
                    'upload_method': 'wifi',
                    'blood_pressure_systolic': random.randint(110, 140),
                    'blood_pressure_diastolic': random.randint(70, 90),
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        }
        
        return device_info, health_data, common_event
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("=" * 60)
        print("🧪 API接口综合测试开始")
        print("=" * 60)
        
        # 生成测试数据
        device_info, health_data, common_event = self.generate_test_data()
        
        print(f"📋 测试设备号: {device_info['SerialNumber']}")
        print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # 测试三个接口
        device_success = self.test_device_info_api(device_info)
        health_success = self.test_health_data_api(health_data)
        event_success = self.test_common_event_api(common_event)
        
        # 生成测试报告
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        
        results = [
            ("设备信息接口", device_success),
            ("健康数据接口", health_success),
            ("通用事件接口", event_success)
        ]
        
        success_count = sum(1 for _, success in results if success)
        
        for name, success in results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{name}: {status}")
        
        print(f"\n总体结果: {success_count}/3 接口测试通过")
        print("=" * 60)

if __name__ == "__main__":
    validator = APITestValidator()
    validator.run_comprehensive_test() 