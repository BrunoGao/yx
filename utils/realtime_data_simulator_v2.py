#!/usr/bin/env python3
"""实时健康数据模拟器 - 改进版，支持虚假设备号测试"""
import requests,json,random,time,threading,signal,sys
from datetime import datetime,timedelta
import mysql.connector
from concurrent.futures import ThreadPoolExecutor

# 配置
HEALTH_API = "http://localhost:8001/upload_health_data"  
DEVICE_API = "http://localhost:8001/upload_device_info"  
DB_CONFIG = {'host':'127.0.0.1','user':'root','password':'aV5mV7kQ!@#','database':'lj-06','port':3306}

class RealtimeSimulator:
    def __init__(self):
        self.running = True
        self.users = []
        self.device_states = {}
        self.session = requests.Session()
        self.stats = {'health_success': 0, 'health_error': 0, 'device_success': 0, 'device_error': 0}
        
        # 虚假设备配置 🆕
        self.fake_device_probability = 0.3  # 30%概率使用虚假设备号
        self.fake_device_prefixes = ['TEST', 'DEMO', 'SIM', 'FAKE', 'DEV']
        self.used_fake_devices = set()  # 避免重复生成
        
    def get_org_users(self, org_id=1):
        """获取用户"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
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
                'battery_level': random.randint(30, 100),
                'voltage': random.randint(3500, 4200),
                'charging_status': 'NONE',
                'wear_state': random.choice([0, 1]),
                'last_charge_time': datetime.now() - timedelta(hours=random.randint(1, 12))
            }
    
    def update_device_state(self, device_sn):
        """更新设备状态"""
        state = self.device_states[device_sn]
        now = datetime.now()
        time_since_charge = now - state['last_charge_time']
        battery_drain = int(time_since_charge.total_seconds() / 3600 * 2)
        state['battery_level'] = max(10, state['battery_level'] - battery_drain)
        
        if state['battery_level'] < 20 and random.random() < 0.3:
            state['charging_status'] = 'CHARGING'
            state['battery_level'] = min(100, state['battery_level'] + 5)
            if state['battery_level'] >= 90:
                state['charging_status'] = 'NONE'
                state['last_charge_time'] = now
        
        if random.random() < 0.05:
            state['wear_state'] = 1 - state['wear_state']
        
        state['voltage'] = 3500 + (state['battery_level'] * 7)
    
    def generate_fake_device_sn(self):
        """生成唯一的虚假设备序列号 🆕"""
        for _ in range(10):
            prefix = random.choice(self.fake_device_prefixes)
            suffix = f"{random.randint(10000, 99999)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
            fake_sn = f"{prefix}{suffix}"
            
            if fake_sn not in self.used_fake_devices:
                self.used_fake_devices.add(fake_sn)
                return fake_sn
        return None
    
    def generate_device_info(self, user):
        """生成设备信息 - 支持虚假设备号 🆕"""
        device_sn = user['device_sn']
        state = self.device_states[device_sn]
        
        # 30%概率使用虚假设备号
        if random.random() < self.fake_device_probability:
            fake_sn = self.generate_fake_device_sn()
            if fake_sn:
                actual_serial = fake_sn
                print(f"[测试] 虚假设备: {fake_sn} (原:{device_sn})")
            else:
                actual_serial = device_sn
                print(f"[警告] 虚假设备生成失败: {device_sn}")
        else:
            actual_serial = device_sn
        
        device_models = ['HUAWEI WATCH 4-DD6', 'HUAWEI WATCH GT 3-A1B', 'HUAWEI WATCH FIT 2-C2D']
        
        return {
            'System Software Version': f'ARC-AL00CN {random.randint(4,5)}.{random.randint(0,2)}.{random.randint(0,9)}.{random.randint(100,999)}',
            'SerialNumber': actual_serial,  # 🆕 使用真实或虚假设备号
            'Device Name': random.choice(device_models),
            'batteryLevel': state['battery_level'],
            'voltage': state['voltage'],
            'chargingStatus': 'CHARGING' if state['charging_status'] == 'CHARGING' else 'NONE',
            'status': 'ACTIVE',
            'wearState': state['wear_state']
        }
    
    def generate_health_data(self, user):
        """生成健康数据"""
        device_sn = user['device_sn']
        timestamp = datetime.now()
        hour = timestamp.hour
        
        is_sleep = hour < 6 or hour > 22
        is_work = 9 <= hour <= 17
        
        base_hr = 55 if is_sleep else (75 if is_work else 68)
        base_stress = 25 if is_sleep else (45 if is_work else 35)
        
        wear_state = self.device_states[device_sn]['wear_state']
        noise_factor = 1.5 if wear_state == 1 else 1.0
        
        base_lat = 22.5500
        base_lng = 114.0500
        lat_offset = random.uniform(-0.0005, 0.0005)
        lng_offset = random.uniform(-0.0006, 0.0006)
        
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
            'latitude': f"{base_lat + lat_offset:.6f}",
            'longitude': f"{base_lng + lng_offset:.6f}",
            'altitude': '0.0',
            'stress': max(0, int(random.gauss(base_stress, 12 * noise_factor))),
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
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
                print(f"健康上传失败 {user['user_name']}: {response.status_code}")
                return False
        except Exception as e:
            self.stats['health_error'] += 1
            print(f"健康上传异常 {user['user_name']}: {e}")
            return False
    
    def upload_device_info(self, user):
        """上传设备信息"""
        try:
            device_sn = user['device_sn']
            self.update_device_state(device_sn)
            data = self.generate_device_info(user)
            
            response = self.session.post(DEVICE_API, json=data, timeout=5)
            if response.status_code == 200:
                self.stats['device_success'] += 1
                return True
            else:
                self.stats['device_error'] += 1
                print(f"设备上传失败 {user['user_name']}: {response.status_code}")
                return False
        except Exception as e:
            self.stats['device_error'] += 1
            print(f"设备上传异常 {user['user_name']}: {e}")
            return False
    
    def health_data_worker(self):
        """健康数据工作线程"""
        while self.running:
            try:
                unique_users = {user['device_sn']: user for user in self.users}
                user_list = list(unique_users.values())
                
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(self.upload_health_data, user) for user in user_list]
                    success = sum(1 for f in futures if f.result())
                    error = len(user_list) - success
                    
                status = f"[健康] {success}/{len(user_list)} 成功"
                if error > 0:
                    status += f" (失败:{error})"
                print(status)
                time.sleep(5)
            except Exception as e:
                print(f"健康线程异常: {e}")
                time.sleep(5)
    
    def device_info_worker(self):
        """设备信息工作线程"""
        while self.running:
            try:
                unique_users = {user['device_sn']: user for user in self.users}
                user_list = list(unique_users.values())
                
                with ThreadPoolExecutor(max_workers=3) as executor:
                    futures = [executor.submit(self.upload_device_info, user) for user in user_list]
                    success = sum(1 for f in futures if f.result())
                    error = len(user_list) - success
                    
                status = f"[设备] {success}/{len(user_list)} 成功"
                if error > 0:
                    status += f" (失败:{error})"
                print(status)
                time.sleep(20)
            except Exception as e:
                print(f"设备线程异常: {e}")
                time.sleep(20)
    
    def status_monitor(self):
        """状态监控"""
        while self.running:
            time.sleep(60)
            if not self.running:
                break
            print(f"\n=== 📊 运行统计 ===")
            print(f"健康数据: ✅{self.stats['health_success']} ❌{self.stats['health_error']}")
            print(f"设备信息: ✅{self.stats['device_success']} ❌{self.stats['device_error']}")
            print(f"活跃用户: 👥{len(self.users)}人")
            print(f"虚假设备: 🎭{len(self.used_fake_devices)}个 (概率{int(self.fake_device_probability*100)}%)")
            
            if self.used_fake_devices:
                recent = list(self.used_fake_devices)[-3:]
                print(f"  最近虚假: {', '.join(recent)}")
            
            # 设备状态采样
            for user in self.users[:3]:
                state = self.device_states[user['device_sn']]
                battery = "🔌充电" if state['charging_status'] == 'CHARGING' else f"🔋{state['battery_level']}%"
                wear = "⌚佩戴" if state['wear_state'] == 0 else "🚫未戴"
                print(f"  {user['user_name']}: {battery} {wear}")
            print("按 Ctrl+C 停止模拟\n")
    
    def signal_handler(self, signum, frame):
        """信号处理"""
        print("\n收到停止信号，正在关闭...")
        self.running = False
    
    def run(self):
        """主程序"""
        print("=== 🏥 实时健康数据模拟器 v2.0 ===")
        
        self.users = self.get_org_users(org_id=1)
        if not self.users:
            print("❌ 未找到org_id=1的用户")
            return
        
        print(f"找到 {len(self.users)} 个用户:")
        for user in self.users:
            dept = user.get('dept_name', '未知部门')
            print(f"  👤 {user['user_name']} ({user['device_sn']}) - {dept}")
        
        self.init_device_states()
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print(f"\n🚀 开始实时模拟:")
        print(f"- 💓 健康数据: 每5秒上传")
        print(f"- 📱 设备信息: 每20秒上传")
        print(f"- 🎭 虚假设备: {int(self.fake_device_probability*100)}%概率 (前缀: {', '.join(self.fake_device_prefixes)})")
        print(f"- ⏹️  按 Ctrl+C 停止")
        print("=" * 50)
        
        threads = [
            threading.Thread(target=self.health_data_worker, daemon=True),
            threading.Thread(target=self.device_info_worker, daemon=True),
            threading.Thread(target=self.status_monitor, daemon=True)
        ]
        
        for t in threads:
            t.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
        
        print("\n✅ 模拟器已停止")
        print(f"📈 最终统计: 健康{self.stats['health_success']}✅/{self.stats['health_error']}❌, 设备{self.stats['device_success']}✅/{self.stats['device_error']}❌")
        if self.used_fake_devices:
            print(f"🎭 生成虚假设备 {len(self.used_fake_devices)} 个: {', '.join(self.used_fake_devices)}")

if __name__ == "__main__":
    simulator = RealtimeSimulator()
    simulator.run() 