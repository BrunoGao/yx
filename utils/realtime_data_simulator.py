#!/usr/bin/env python3
"""实时健康数据模拟器V6.0-三大核心接口批量测试"""
import requests,json,random,time,threading,signal,sys,mysql.connector
from datetime import datetime,timedelta
from concurrent.futures import ThreadPoolExecutor

# 配置
HEALTH_API = "http://localhost:5001/upload_health_data"  #健康数据上传API
DEVICE_API = "http://localhost:5001/upload_device_info"  #设备信息上传API  
ALERT_API = "http://localhost:5001/upload_common_event"  #系统事件告警API
DB_CONFIG = {'host':'127.0.0.1','user':'root','password':'123456','database':'test','port':3306}

class RealtimeSimulator:
    def __init__(self):
        self.running = True
        self.users = []
        self.device_states = {}  #设备状态缓存
        self.session = requests.Session()
        self.stats = {'health_success': 0, 'health_error': 0, 'device_success': 0, 'device_error': 0, 'alert_success': 0, 'alert_error': 0}
        
    def get_real_devices(self, org_id=1939964806110937090):
        """从数据库获取真实设备和员工信息"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            sql = """SELECT u.id, u.user_name, u.device_sn, u.phone, 
                           COALESCE(o.name, 'Unknown') as org_name, 
                           u.customer_id, uo.org_id 
                    FROM sys_user u
                    LEFT JOIN sys_user_org uo ON u.id = uo.user_id
                    LEFT JOIN sys_org_units o ON uo.org_id = o.id
                    WHERE u.device_sn IN ('CRFTQ23409001890', 'CRFTQ23409001891', 'CRFTQ23409001892', 'CRFTQ23409001893', 'CRFTQ23409001894', 'CRFTQ23409001895')
                    AND uo.org_id = %s AND u.is_deleted = 0 ORDER BY u.device_sn"""
            cursor.execute(sql, (org_id,))
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            return users if users else []
        except Exception as e:
            print(f"获取真实设备失败: {e}")
            return []
    
    def init_device_states(self):
        """初始化设备状态"""
        for user in self.users:
            device_sn = user['device_sn']
            self.device_states[device_sn] = {
                'battery_level': random.randint(30, 100), 'voltage': random.randint(3500, 4200),
                'charging_status': 'NONE', 'wear_state': random.choice([0, 1]),
                'last_charge_time': datetime.now() - timedelta(hours=random.randint(1, 12))
            }
    
    def update_device_state(self, device_sn):
        """更新设备状态（模拟真实变化）"""
        state = self.device_states[device_sn]
        now = datetime.now()
        time_since_charge = now - state['last_charge_time']
        battery_drain = int(time_since_charge.total_seconds() / 3600 * 2)  #每小时降2%
        state['battery_level'] = max(10, state['battery_level'] - battery_drain)
        
        #低电量时可能充电
        if state['battery_level'] < 20 and random.random() < 0.3:
            state['charging_status'] = 'CHARGING'
            state['battery_level'] = min(100, state['battery_level'] + 5)
            if state['battery_level'] >= 90:
                state['charging_status'] = 'NONE'
                state['last_charge_time'] = now
        
        #佩戴状态偶尔变化
        if random.random() < 0.05: state['wear_state'] = 1 - state['wear_state']  #5%概率改变佩戴状态
        state['voltage'] = 3500 + (state['battery_level'] * 7)  #电压与电量关联
    
    def generate_health_data(self, user):
        """生成真实健康数据"""
        device_sn = user['device_sn']
        timestamp = datetime.now()
        hour = timestamp.hour
        is_sleep = hour < 6 or hour > 22
        is_work = 9 <= hour <= 17
        base_hr = 55 if is_sleep else (75 if is_work else 68)
        base_stress = 25 if is_sleep else (45 if is_work else 35)
        wear_state = self.device_states[device_sn]['wear_state']
        noise_factor = 1.5 if wear_state == 1 else 1.0  #未佩戴时数据噪声更大
        
        #固定基础位置(煤矿集团总部附近)
        base_lat, base_lng = 22.5500, 114.0500
        lat_offset = random.uniform(-0.0005, 0.0005)  #±55米纬度偏移
        lng_offset = random.uniform(-0.0006, 0.0006)  #±58米经度偏移
        
        return {
            'data': {
                'deviceSn': device_sn, 'upload_method': 'wifi',
                'heart_rate': max(50, int(random.gauss(base_hr, 8 * noise_factor))),
                'blood_oxygen': random.randint(94 if wear_state == 1 else 96, 100),
                'body_temperature': f"{random.uniform(36.0, 37.5):.1f}",
                'blood_pressure_systolic': random.randint(105, 140),
                'blood_pressure_diastolic': random.randint(65, 90),
                'step': random.randint(0, 50) if is_sleep else random.randint(100, 800),
                'distance': f"{random.uniform(0, 30) if is_sleep else random.uniform(50, 500):.1f}",
                'calorie': f"{random.uniform(10000, 20000) if is_sleep else random.uniform(20000, 50000):.1f}",
                'latitude': f"{base_lat + lat_offset:.6f}", 'longitude': f"{base_lng + lng_offset:.6f}",
                'altitude': '0.0', 'stress': max(0, int(random.gauss(base_stress, 12 * noise_factor))),
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'sleepData': '{"code":0,"data":[{"endTimeStamp":1747440420000,"startTimeStamp":1747418280000,"type":2}],"name":"sleep","type":"history"}',
                'exerciseDailyData': '{"code":0,"data":[{"strengthTimes":2,"totalTime":5}],"name":"daily","type":"history"}',
                'exerciseWeekData': 'null', 'scientificSleepData': 'null',
                'workoutData': '{"code":0,"data":[],"name":"workout","type":"history"}',
                'customerId': user['customer_id'], 'orgId': user['org_id'], 'userId': user['id']
            }
        }
    
    def generate_device_info(self, user):
        """生成设备信息数据"""
        device_sn = user['device_sn']
        state = self.device_states[device_sn]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        wear_status = '1' if state['wear_state'] == 0 else '0'  #确保wearable_status为字符串类型且值为'0'或'1'
        
        return {
            'System Software Version': f'ARC-AL00CN {random.randint(4,5)}.{random.randint(0,2)}.{random.randint(0,9)}.{random.randint(100,999)}(SP{random.randint(10,99)}C{random.randint(100,999)}E{random.randint(100,999)}R{random.randint(100,999)}P{random.randint(100,999)})',
            'Wifi Address': ':'.join([f'{random.randint(0,255):02x}' for _ in range(6)]),
            'Bluetooth Address': ':'.join([f'{random.randint(0,255):02X}' for _ in range(6)]),
            'IP Address': f'192.168.{random.randint(1,254)}.{random.randint(2,254)}\\nfe80::{random.randint(0,255):x}:{random.randint(0,255):x}ff:fef{random.randint(0,15):x}:a{random.randint(100,999):x}',
            'Network Access Mode': str(random.choice([1, 2, 3])), 'SerialNumber': device_sn, 'serial_number': device_sn,
            'Device Name': 'HUAWEI WATCH GT 3-A1B', 'IMEI': f'{random.randint(100000000000000, 999999999999999)}',
            'batteryLevel': str(state['battery_level']), 'voltage': str(state['voltage']),
            'chargingStatus': 'CHARGING' if state['charging_status'] == 'CHARGING' else 'NONE',
            'status': 'ACTIVE', 'wearable_status': wear_status, 'wearState': str(state['wear_state']),
            'customerId': str(user['customer_id']), 'orgId': str(user['org_id']), 'userId': str(user['id']),
            'update_time': timestamp, 'timestamp': timestamp
        }
    
    def generate_alert_event(self, user):
        """生成系统事件告警数据 - 严格按照HttpService.uploadCommonEvent方法实现"""
        device_sn = user['device_sn']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 随机选择事件类型(匹配数据库中的AlertRules规则类型)
        event_types = [
            ('com.tdtech.ohos.action.WEAR_STATUS_CHANGED', str(random.choice([0, 1]))),  # 佩戴状态变化
            ('com.tdtech.ohos.action.SOS_EVENT', '1'),  # SOS紧急求助信号
            ('com.tdtech.ohos.action.FALLDOWN_EVENT', '1'),  # 跌倒检测事件
            ('com.tdtech.ohos.action.HEARTRATE_HIGH_ALERT', str(random.randint(120, 180))),  # 心率过高告警
            ('com.tdtech.ohos.action.HEARTRATE_LOW_ALERT', str(random.randint(30, 49))),  # 心率过低告警
            ('com.tdtech.ohos.action.SPO2_LOW_ALERT', str(random.randint(85, 89))),  # 血氧过低告警
            ('com.tdtech.ohos.action.TEMPERATURE_HIGH_ALERT', str(random.randint(375, 390))),  # 体温过高告警
            ('com.tdtech.ohos.action.STRESS_HIGH_ALERT', str(random.randint(70, 100))),  # 压力过高告警
        ]
        
        event_type, event_value = random.choice(event_types)
        
        # 生成位置信息(与HttpService中保持一致)
        base_lat, base_lng = 22.5500, 114.0500
        lat_offset = random.uniform(-0.0005, 0.0005)
        lng_offset = random.uniform(-0.0006, 0.0006)
        latitude = f"{base_lat + lat_offset:.6f}"
        longitude = f"{base_lng + lng_offset:.6f}"
        altitude = "0.0"  # 固定高度值
        
        # 生成healthData - 完整的健康数据JSON对象(与Utils.getHealthInfo()格式一致)
        health_data = self.generate_health_data(user)['data']
        health_data_obj = {
            'deviceSn': device_sn,
            'upload_method': 'wifi',
            'heart_rate': health_data['heart_rate'],
            'blood_oxygen': health_data['blood_oxygen'],
            'body_temperature': health_data['body_temperature'],
            'blood_pressure_systolic': health_data['blood_pressure_systolic'],
            'blood_pressure_diastolic': health_data['blood_pressure_diastolic'],
            'step': health_data['step'],
            'distance': health_data['distance'],
            'calorie': health_data['calorie'],
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude,
            'stress': health_data['stress'],
            'timestamp': timestamp,
            'sleepData': health_data['sleepData'],
            'exerciseDailyData': health_data['exerciseDailyData'],
            'exerciseWeekData': health_data['exerciseWeekData'],
            'scientificSleepData': health_data['scientificSleepData'],
            'workoutData': health_data['workoutData'],
            'customerId': user['customer_id'],
            'orgId': user['org_id'],
            'userId': user['id']
        }
        
        # 构建完整的commonEvent数据结构(与HttpService.uploadCommonEvent完全一致)
        return {
            'eventType': event_type,
            'eventValue': event_value,
            'deviceSn': device_sn,
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude,
            'timestamp': timestamp,
            'healthData': {'data': health_data_obj}  # 嵌套格式: healthData.data, 匹配alert.py的期望格式
        }
    
    def upload_health_data(self, user):
        """上传健康数据"""
        try:
            data = self.generate_health_data(user)
            response = self.session.post(HEALTH_API, json=data, timeout=5)
            if response.status_code == 200:
                self.stats['health_success'] += 1
                return True
            else:
                self.stats['health_error'] += 1
                print(f"健康数据上传失败 {user['user_name']}({user['device_sn']}): {response.status_code}")
                return False
        except Exception as e:
            self.stats['health_error'] += 1
            print(f"健康数据上传异常 {user['user_name']}({user['device_sn']}): {e}")
            return False
    
    def upload_device_info(self, user):
        """上传设备信息"""
        try:
            device_sn = user['device_sn']
            self.update_device_state(device_sn)  #更新设备状态
            device_info = self.generate_device_info(user)
            data = [device_info]  # 包装成数组，因为/device/upload是批量接口
            response = self.session.post(DEVICE_API, json=data, timeout=5)
            if response.status_code == 200:
                self.stats['device_success'] += 1
                return True
            else:
                self.stats['device_error'] += 1
                print(f"设备信息上传失败 {user['user_name']}: {response.status_code}")
                return False
        except Exception as e:
            self.stats['device_error'] += 1
            print(f"设备信息上传异常 {user['user_name']}: {e}")
            return False
    
    def upload_alert_event(self, user):
        """上传系统事件告警"""
        try:
            data = self.generate_alert_event(user)
            response = self.session.post(ALERT_API, json=data, timeout=5)
            if response.status_code == 200:
                self.stats['alert_success'] += 1
                return True
            else:
                self.stats['alert_error'] += 1
                # 打印详细错误信息
                try:
                    error_detail = response.json()
                    print(f"告警事件上传失败 {user['user_name']}: {response.status_code} - {error_detail}")
                except:
                    print(f"告警事件上传失败 {user['user_name']}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.stats['alert_error'] += 1
            print(f"告警事件上传异常 {user['user_name']}: {e}")
            return False
    
    def health_data_worker(self):
        """健康数据上传工作线程-每5秒执行"""
        while self.running:
            try:
                unique_users = {user['device_sn']: user for user in self.users}  #确保设备号唯一性
                unique_user_list = list(unique_users.values())
                
                with ThreadPoolExecutor(max_workers=3) as executor:
                    futures = [executor.submit(self.upload_health_data, user) for user in unique_user_list]
                    success_count = sum(1 for f in futures if f.result())
                    error_count = len(unique_user_list) - success_count
                    
                if error_count > 0:
                    print(f"[健康] 成功: {success_count}/{len(unique_user_list)} 设备 (失败: {error_count})")
                else:
                    print(f"[健康] 成功: {success_count}/{len(unique_user_list)} 设备")
                time.sleep(5)
            except Exception as e:
                print(f"健康数据工作线程异常: {e}")
                time.sleep(5)
    
    def device_info_worker(self):
        """设备信息上传工作线程-每20秒执行"""
        while self.running:
            try:
                unique_users = {user['device_sn']: user for user in self.users}  #确保设备号唯一性
                unique_user_list = list(unique_users.values())
                
                with ThreadPoolExecutor(max_workers=3) as executor:
                    futures = [executor.submit(self.upload_device_info, user) for user in unique_user_list]
                    success_count = sum(1 for f in futures if f.result())
                    error_count = len(unique_user_list) - success_count
                    
                if error_count > 0:
                    print(f"[设备] 成功: {success_count}/{len(unique_user_list)} 设备 (失败: {error_count})")
                else:
                    print(f"[设备] 成功: {success_count}/{len(unique_user_list)} 设备")
                time.sleep(20)
            except Exception as e:
                print(f"设备信息工作线程异常: {e}")
                time.sleep(20)
    
    def alert_event_worker(self):
        """系统事件告警上传工作线程-每15秒执行"""
        while self.running:
            try:
                time.sleep(15)  #15秒执行一次
                if not self.running: break
                
                #随机选择1-2个用户产生告警事件
                if self.users:
                    selected_users = random.sample(self.users, min(random.randint(1, 2), len(self.users)))
                    
                    with ThreadPoolExecutor(max_workers=2) as executor:
                        futures = [executor.submit(self.upload_alert_event, user) for user in selected_users]
                        success_count = sum(1 for f in futures if f.result())
                        error_count = len(selected_users) - success_count
                        
                    if error_count > 0:
                        print(f"[告警] 成功: {success_count}/{len(selected_users)} 事件 (失败: {error_count})")
                    else:
                        print(f"[告警] 成功: {success_count}/{len(selected_users)} 事件")
                        
            except Exception as e:
                print(f"告警事件工作线程异常: {e}")
                time.sleep(15)
    
    def status_monitor(self):
        """状态监控线程"""
        while self.running:
            time.sleep(60)  #每分钟显示一次统计
            if not self.running: break
            print(f"\n=== 运行统计 ===")
            print(f"健康数据: 成功{self.stats['health_success']} 失败{self.stats['health_error']}")
            print(f"设备信息: 成功{self.stats['device_success']} 失败{self.stats['device_error']}")
            print(f"告警事件: 成功{self.stats['alert_success']} 失败{self.stats['alert_error']}")
            print(f"活跃设备: {len(self.users)}台")
            
            #显示设备状态采样
            for user in self.users:
                state = self.device_states[user['device_sn']]
                status = "充电中" if state['charging_status'] == 'CHARGING' else f"{state['battery_level']}%"
                wear = "佩戴" if state['wear_state'] == 0 else "未佩戴"
                print(f"  {user['user_name']}: 电量{status} {wear}")
            print("按 Ctrl+C 停止模拟\n")
    
    def signal_handler(self, signum, frame):
        """信号处理"""
        print("\n收到停止信号，正在关闭...")
        self.running = False
    
    def run(self):
        """主运行函数"""
        print("=== 实时健康数据模拟器V6.0-三大核心接口批量测试 ===")
        
        #获取真实设备
        self.users = self.get_real_devices(org_id=1939964806110937090)
        if not self.users:
            print("❌ 未找到真实设备，程序退出")
            return
        print(f"找到 {len(self.users)} 个真实设备:")
        
        for user in self.users:
            print(f"  {user['user_name']} ({user['device_sn']}) - {user['org_name']}")
        
        #初始化设备状态
        self.init_device_states()
        
        #注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print(f"\n开始实时模拟:")
        print(f"- 健康数据: 每5秒上传 → {HEALTH_API}")
        print(f"- 设备信息: 每20秒上传 → {DEVICE_API}")
        print(f"- 告警事件: 每15秒上传 → {ALERT_API}")
        print(f"- 真实设备: {len(self.users)}台")
        print(f"- 按 Ctrl+C 停止")
        print("=" * 50)
        
        #启动工作线程
        threads = [
            threading.Thread(target=self.health_data_worker, daemon=True),
            threading.Thread(target=self.device_info_worker, daemon=True),
            threading.Thread(target=self.alert_event_worker, daemon=True),
            threading.Thread(target=self.status_monitor, daemon=True)
        ]
        
        for t in threads:
            t.start()
        
        #主线程等待
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
        
        print("\n模拟器已停止")
        print(f"最终统计:")
        print(f"  健康数据: {self.stats['health_success']}成功/{self.stats['health_error']}失败")
        print(f"  设备信息: {self.stats['device_success']}成功/{self.stats['device_error']}失败")
        print(f"  告警事件: {self.stats['alert_success']}成功/{self.stats['alert_error']}失败")

if __name__ == "__main__":
    simulator = RealtimeSimulator()
    simulator.run() 