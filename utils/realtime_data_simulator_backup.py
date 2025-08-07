#!/usr/bin/env python3
"""实时健康数据模拟器 - 验证大屏显示效果"""
import requests,json,random,time,threading,signal,sys
from datetime import datetime,timedelta
import mysql.connector
from concurrent.futures import ThreadPoolExecutor

# 配置
HEALTH_API = "http://localhost:8001/upload_health_data"  # 健康数据上传API
DEVICE_API = "http://localhost:8001/upload_device_info"  # 设备信息上传API
BOOT_API = "http://localhost:9998"  # Spring Boot API
ADMIN_API = "http://localhost:8080"  # 前端管理界面
DB_CONFIG = {'host':'127.0.0.1','user':'root','password':'aV5mV7kQ!@#','database':'lj-06','port':3306}  # Docker MySQL配置

class RealtimeSimulator:
    def __init__(self):
        self.running = True
        self.users = []
        self.device_states = {}  # 设备状态缓存
        self.session = requests.Session()
        self.stats = {'health_success': 0, 'health_error': 0, 'device_success': 0, 'device_error': 0}
        
        # 虚假设备配置
        self.fake_device_probability = 0.3  # 30%概率使用虚假设备号
        self.fake_device_prefixes = ['TEST', 'DEMO', 'SIM', 'FAKE', 'DEV']  # 虚假设备前缀
        self.used_fake_devices = set()  # 已使用的虚假设备号，避免重复
        
    def get_org_users(self, org_id=1):
        """获取指定组织下所有佩戴手表的用户"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            # 使用GROUP BY去重，选择第一个部门名称
            sql = """
            SELECT u.id,u.user_name,u.device_sn,u.phone,MIN(o.name) as dept_name 
            FROM sys_user u 
            LEFT JOIN sys_user_org uo ON u.id = uo.user_id 
            LEFT JOIN sys_org_units o ON uo.org_id = o.id
            WHERE u.device_sn IS NOT NULL AND u.device_sn != '' AND u.device_sn != '-' and uo.is_deleted = 0
            AND u.is_deleted = 0 AND (uo.org_id = %s OR u.customer_id = %s)
            GROUP BY u.id, u.user_name, u.device_sn, u.phone
            """
            cursor.execute(sql, (org_id, org_id))
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            print(f"获取用户失败: {e}")
            return []
    
    def init_device_states(self):
        """初始化设备状态"""
        for user in self.users:
            device_sn = user['device_sn']
            self.device_states[device_sn] = {
                'battery_level': random.randint(30, 100),  # 初始电量
                'voltage': random.randint(3500, 4200),
                'charging_status': 'NONE',
                'wear_state': random.choice([0, 1]),  # 0佩戴 1未佩戴
                'last_charge_time': datetime.now() - timedelta(hours=random.randint(1, 12))
            }
    
    def update_device_state(self, device_sn):
        """更新设备状态（模拟真实变化）"""
        state = self.device_states[device_sn]
        
        # 电量随时间降低
        now = datetime.now()
        time_since_charge = now - state['last_charge_time']
        battery_drain = int(time_since_charge.total_seconds() / 3600 * 2)  # 每小时降2%
        state['battery_level'] = max(10, state['battery_level'] - battery_drain)
        
        # 低电量时可能充电
        if state['battery_level'] < 20 and random.random() < 0.3:
            state['charging_status'] = 'CHARGING'
            state['battery_level'] = min(100, state['battery_level'] + 5)
            if state['battery_level'] >= 90:
                state['charging_status'] = 'NONE'
                state['last_charge_time'] = now
        
        # 佩戴状态偶尔变化
        if random.random() < 0.05:  # 5%概率改变佩戴状态
            state['wear_state'] = 1 - state['wear_state']
        
        # 电压与电量关联
        state['voltage'] = 3500 + (state['battery_level'] * 7)  # 3500-4200mV
    
    def generate_health_data(self, user):
        """生成真实的健康数据"""
        device_sn = user['device_sn']
        timestamp = datetime.now()
        hour = timestamp.hour
        
        # 根据时间调整基础值
        is_sleep = hour < 6 or hour > 22
        is_work = 9 <= hour <= 17
        
        base_hr = 55 if is_sleep else (75 if is_work else 68)
        base_stress = 25 if is_sleep else (45 if is_work else 35)
        
        # 佩戴状态影响数据质量
        wear_state = self.device_states[device_sn]['wear_state']
        noise_factor = 1.5 if wear_state == 1 else 1.0  # 未佩戴时数据噪声更大
        
        # 固定基础位置(煤矿集团总部附近)
        base_lat = 22.5500  # 基础纬度
        base_lng = 114.0500  # 基础经度
        
        # 100米范围内的随机偏移: 纬度1度≈111km，经度1度≈96km(22.5°N)
        lat_offset = random.uniform(-0.0005, 0.0005)  # ±55米纬度偏移
        lng_offset = random.uniform(-0.0006, 0.0006)  # ±58米经度偏移
        
        return {
            'id': device_sn,
            'upload_method': 'wifi',
            'heart_rate': max(50, int(random.gauss(base_hr, 8 * noise_factor))),
            'blood_oxygen': random.randint(94 if wear_state == 1 else 96, 100),
            'body_temperature': f"{random.uniform(36.0, 37.5):.1f}",
            'blood_pressure_systolic': random.randint(105, 140),
            'blood_pressure_diastolic': random.randint(65, 90),
            'step': random.randint(0, 50) if is_sleep else random.randint(100, 800),
            'distance': f"{random.uniform(0, 30) if is_sleep else random.uniform(50, 500):.1f}",
            'calorie': f"{random.uniform(10000, 20000) if is_sleep else random.uniform(20000, 50000):.1f}",
            'latitude': f"{base_lat + lat_offset:.6f}",  # 控制在100米范围内
            'longitude': f"{base_lng + lng_offset:.6f}",  # 控制在100米范围内
            'altitude': '0.0',
            'stress': max(0, int(random.gauss(base_stress, 12 * noise_factor))),
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sleepData': '{"code":0,"data":[{"endTimeStamp":1747440420000,"startTimeStamp":1747418280000,"type":2}],"name":"sleep","type":"history"}',
            'exerciseDailyData': '{"code":0,"data":[{"strengthTimes":2,"totalTime":5}],"name":"daily","type":"history"}',
            'exerciseWeekData': 'null',
            'scientificSleepData': 'null',
            'workoutData': '{"code":0,"data":[],"name":"workout","type":"history"}'
        }
    
    def generate_device_info(self, user):
        """生成设备信息数据"""
        device_sn = user['device_sn']
        state = self.device_states[device_sn]
        
        # 根据配置概率使用数据库不存在的设备序列号进行测试
        if random.random() < self.fake_device_probability:
            # 生成唯一的虚假设备序列号
            max_attempts = 10
            for _ in range(max_attempts):
                prefix = random.choice(self.fake_device_prefixes)
                suffix = f"{random.randint(10000, 99999)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
                fake_device_sn = f"{prefix}{suffix}"
                
                if fake_device_sn not in self.used_fake_devices:
                    self.used_fake_devices.add(fake_device_sn)
                    actual_serial = fake_device_sn
                    print(f"[测试] 使用虚假设备号: {fake_device_sn} (原设备: {device_sn})")
                    break
            else:
                # 如果生成失败，使用真实设备号
                actual_serial = device_sn
                print(f"[警告] 虚假设备号生成失败，使用真实设备: {device_sn}")
        else:
            # 使用真实的设备序列号
            actual_serial = device_sn
        
        # 随机生成设备信息基础数据
        device_models = [
            'HUAWEI WATCH 4-DD6', 'HUAWEI WATCH GT 3-A1B', 
            'HUAWEI WATCH FIT 2-C2D', 'HUAWEI WATCH GT 2e-E3F'
        ]
        
        return {
            'System Software Version': f'ARC-AL00CN {random.randint(4,5)}.{random.randint(0,2)}.{random.randint(0,9)}.{random.randint(100,999)}(SP{random.randint(10,99)}C{random.randint(100,999)}E{random.randint(100,999)}R{random.randint(100,999)}P{random.randint(100,999)})',
            'Wifi Address': ':'.join([f'{random.randint(0,255):02x}' for _ in range(6)]),
            'Bluetooth Address': ':'.join([f'{random.randint(0,255):02X}' for _ in range(6)]),
            'IP Address': f'192.168.{random.randint(1,254)}.{random.randint(2,254)}\\nfe80::{random.randint(0,255):x}:{random.randint(0,255):x}ff:fef{random.randint(0,15):x}:a{random.randint(100,999):x}',
            'Network Access Mode': random.choice([1, 2, 3]),
            'SerialNumber': actual_serial,  # 使用真实或虚假的设备序列号
            'Device Name': random.choice(device_models),
            'IMEI': f'{random.randint(100000000000000, 999999999999999)}',
            'batteryLevel': state['battery_level'],
            'voltage': state['voltage'],
            'chargingStatus': 'CHARGING' if state['charging_status'] == 'CHARGING' else 'NONE',
            'status': 'ACTIVE',
            'wearState': state['wear_state']
        }
    
    def upload_health_data(self, user):
        """上传健康数据"""
        try:
            data = self.generate_health_data(user)
            response = self.session.post(HEALTH_API, json={'data': data}, timeout=5)
            if response.status_code == 200:
                self.stats['health_success'] += 1
                return True
            else:
                self.stats['health_error'] += 1
                try:
                    error_detail = response.json() if response.text else f"状态码: {response.status_code}"
                except:
                    error_detail = f"状态码: {response.status_code}, 响应: {response.text[:100]}"
                print(f"健康数据上传失败 {user['user_name']}({user['device_sn']}): {error_detail}")
                return False
        except Exception as e:
            self.stats['health_error'] += 1
            print(f"健康数据上传异常 {user['user_name']}({user['device_sn']}): {e}")
            return False
    
    def upload_device_info(self, user):
        """上传设备信息"""
        try:
            device_sn = user['device_sn']
            self.update_device_state(device_sn)  # 更新设备状态
            data = self.generate_device_info(user)
            
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
    
    def health_data_worker(self):
        """健康数据上传工作线程 - 每5秒执行"""
        while self.running:
            try:
                # 确保设备号唯一性，避免重复设备同时上传
                unique_users = {}
                for user in self.users:
                    device_sn = user['device_sn']
                    if device_sn not in unique_users:
                        unique_users[device_sn] = user
                
                unique_user_list = list(unique_users.values())
                
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(self.upload_health_data, user) for user in unique_user_list]
                    success_count = sum(1 for f in futures if f.result())
                    error_count = len(unique_user_list) - success_count
                    
                if error_count > 0:
                    print(f"[健康] 成功: {success_count}/{len(unique_user_list)} 用户 (失败: {error_count})")
                else:
                    print(f"[健康] 成功: {success_count}/{len(unique_user_list)} 用户")
                time.sleep(5)
            except Exception as e:
                print(f"健康数据工作线程异常: {e}")
                time.sleep(5)
    
    def device_info_worker(self):
        """设备信息上传工作线程 - 每20秒执行"""
        while self.running:
            try:
                # 确保设备号唯一性
                unique_users = {}
                for user in self.users:
                    device_sn = user['device_sn']
                    if device_sn not in unique_users:
                        unique_users[device_sn] = user
                
                unique_user_list = list(unique_users.values())
                
                with ThreadPoolExecutor(max_workers=3) as executor:
                    futures = [executor.submit(self.upload_device_info, user) for user in unique_user_list]
                    success_count = sum(1 for f in futures if f.result())
                    error_count = len(unique_user_list) - success_count
                    
                if error_count > 0:
                    print(f"[设备] 成功: {success_count}/{len(unique_user_list)} 用户 (失败: {error_count})")
                else:
                    print(f"[设备] 成功: {success_count}/{len(unique_user_list)} 用户")
                time.sleep(20)
            except Exception as e:
                print(f"设备信息工作线程异常: {e}")
                time.sleep(20)
    
    def status_monitor(self):
        """状态监控线程"""
        while self.running:
            time.sleep(60)  # 每分钟显示一次统计
            if not self.running:
                break
            print(f"\n=== 运行统计 ===")
            print(f"健康数据: 成功{self.stats['health_success']} 失败{self.stats['health_error']}")
            print(f"设备信息: 成功{self.stats['device_success']} 失败{self.stats['device_error']}")
            print(f"活跃用户: {len(self.users)}人")
            print(f"虚假设备: 已生成{len(self.used_fake_devices)}个 (概率{int(self.fake_device_probability*100)}%)")
            
            # 显示最近使用的虚假设备
            if self.used_fake_devices:
                recent_fake = list(self.used_fake_devices)[-3:]  # 显示最新3个
                print(f"  最近虚假设备: {', '.join(recent_fake)}")
            
            # 显示设备状态采样
            sample_users = self.users[:3]
            for user in sample_users:
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
        print("=== 实时健康数据模拟器 ===")
        
        # 获取用户
        self.users = self.get_org_users(org_id=1)
        if not self.users:
            print("错误: 未找到org_id=1的佩戴手表用户")
            return
        
        print(f"找到 {len(self.users)} 个用户:")
        for user in self.users:
            dept = user.get('dept_name', '未知部门')
            print(f"  {user['user_name']} ({user['device_sn']}) - {dept}")
        
        # 初始化设备状态
        self.init_device_states()
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print(f"\n开始实时模拟:")
        print(f"- 健康数据: 每5秒上传")
        print(f"- 设备信息: 每20秒上传")
        print(f"- 虚假设备概率: {int(self.fake_device_probability*100)}% (前缀: {', '.join(self.fake_device_prefixes)})")
        print(f"- 按 Ctrl+C 停止")
        print("=" * 40)
        
        # 启动工作线程
        threads = [
            threading.Thread(target=self.health_data_worker, daemon=True),
            threading.Thread(target=self.device_info_worker, daemon=True),
            threading.Thread(target=self.status_monitor, daemon=True)
        ]
        
        for t in threads:
            t.start()
        
        # 主线程等待
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
        
        print("\n模拟器已停止")
        print(f"最终统计: 健康{self.stats['health_success']}成功/{self.stats['health_error']}失败, 设备{self.stats['device_success']}成功/{self.stats['device_error']}失败")

if __name__ == "__main__":
    simulator = RealtimeSimulator()
    simulator.run() 