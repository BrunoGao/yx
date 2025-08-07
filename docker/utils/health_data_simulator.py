#!/usr/bin/env python3
"""健康数据模拟器 - 生成真实用户数据和基线"""
import requests,json,random,time,sys,os,argparse
from datetime import datetime,timedelta
import mysql.connector
from concurrent.futures import ThreadPoolExecutor,as_completed

# 配置
API_URL = "http://localhost:5001/upload_health_data"
BASELINE_API = "http://localhost:5001/api/baseline/generate"
DB_CONFIG = {'host':'127.0.0.1','user':'root','password':'aV5mV7kQ!@#','database':'lj-05','port':3306}

class HealthDataSimulator:
    def __init__(self):
        self.session = requests.Session()
        self.success_count = 0
        self.error_count = 0
    
    def get_users(self, limit=None):
        """获取用户列表"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id,user_name,device_sn FROM sys_user WHERE device_sn IS NOT NULL AND device_sn != '' AND device_sn != '-' AND is_deleted = 0"
            if limit: sql += f" LIMIT {limit}"
            cursor.execute(sql)
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            print(f"获取用户失败: {e}")
            return []
    
    def generate_realistic_data(self, device_sn, timestamp, user_profile=None):
        """生成更真实的健康数据"""
        # 基于时间的生理节律
        hour = timestamp.hour
        is_sleep_time = hour < 6 or hour > 22
        is_work_time = 9 <= hour <= 17
        
        # 基础值
        base_hr = 70 if not is_sleep_time else 55
        base_stress = 30 if is_sleep_time else (50 if is_work_time else 35)
        
        return {
            'id': device_sn,
            'upload_method': 'wifi',
            'heart_rate': random.randint(base_hr-10, base_hr+20),
            'blood_oxygen': random.randint(96, 100),
            'body_temperature': f"{random.uniform(36.2, 37.2):.1f}",
            'blood_pressure_systolic': random.randint(110, 130),
            'blood_pressure_diastolic': random.randint(70, 85),
            'step': random.randint(100, 500) if is_sleep_time else random.randint(800, 2500),
            'distance': f"{random.uniform(50, 200) if is_sleep_time else random.uniform(500, 2000):.1f}",
            'calorie': f"{random.uniform(15000, 25000) if is_sleep_time else random.uniform(35000, 65000):.1f}",
            'latitude': f"{random.uniform(22.5, 22.6):.14f}",
            'longitude': f"{random.uniform(114.0, 114.1):.14f}",
            'altitude': '0.0',
            'stress': random.randint(base_stress-10, base_stress+15),
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sleepData': '{"code":0,"data":[{"endTimeStamp":1747440420000,"startTimeStamp":1747418280000,"type":2}],"name":"sleep","type":"history"}',
            'exerciseDailyData': '{"code":0,"data":[{"strengthTimes":2,"totalTime":5}],"name":"daily","type":"history"}',
            'exerciseWeekData': 'null',
            'scientificSleepData': 'null',
            'workoutData': '{"code":0,"data":[],"name":"workout","type":"history"}'
        }
    
    def upload_batch(self, batch_data):
        """批量上传数据"""
        try:
            payload = {'data': batch_data}
            response = self.session.post(API_URL, json=payload, timeout=30)
            if response.status_code == 200:
                self.success_count += len(batch_data)
                return True
            else:
                self.error_count += len(batch_data)
                return False
        except Exception as e:
            self.error_count += len(batch_data)
            return False
    
    def simulate_user_period(self, user, days=7, interval_minutes=5):
        """模拟用户指定天数的数据"""
        device_sn = user['device_sn']
        user_name = user['user_name']
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        success_days = 0
        current_date = start_date
        
        while current_date < end_date:
            batch_data = []
            day_start = current_date.replace(hour=0, minute=0, second=0)
            day_end = day_start + timedelta(days=1)
            
            # 生成一天的数据
            current_time = day_start
            while current_time < day_end:
                data = self.generate_realistic_data(device_sn, current_time)
                batch_data.append(data)
                current_time += timedelta(minutes=interval_minutes)
            
            # 上传批量数据
            if self.upload_batch(batch_data):
                success_days += 1
            
            current_date += timedelta(days=1)
            time.sleep(0.1)
            
            if success_days % 3 == 0 and success_days > 0:
                print(f"用户{user_name}: 已完成{success_days}天数据")
        
        print(f"用户{user_name}完成: {success_days}天数据")
        return success_days
    
    def generate_baselines(self, days=7):
        """生成多天基线"""
        print("开始生成基线数据...")
        success_count = 0
        
        for i in range(days):
            target_date = (datetime.now() - timedelta(days=i+1)).strftime('%Y-%m-%d')
            try:
                response = self.session.post(BASELINE_API, json={'target_date': target_date}, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    user_count = result.get('user_baseline', {}).get('count', 0)
                    org_count = result.get('org_baseline', {}).get('count', 0)
                    print(f"✓ 基线生成({target_date}): 用户{user_count}条, 组织{org_count}条")
                    success_count += 1
                else:
                    print(f"✗ 基线生成失败({target_date}): {response.status_code}")
            except Exception as e:
                print(f"✗ 基线生成异常({target_date}): {e}")
            time.sleep(0.5)
        
        return success_count

def main():
    parser = argparse.ArgumentParser(description='健康数据模拟器')
    parser.add_argument('--users', type=int, default=3, help='用户数量限制')
    parser.add_argument('--days', type=int, default=7, help='模拟天数')
    parser.add_argument('--interval', type=int, default=5, help='数据间隔(分钟)')
    parser.add_argument('--baseline-days', type=int, default=7, help='基线生成天数')
    parser.add_argument('--quick', action='store_true', help='快速测试模式')
    parser.add_argument('--no-confirm', action='store_true', help='跳过确认')
    
    args = parser.parse_args()
    
    simulator = HealthDataSimulator()
    
    print("=== 健康数据模拟器 ===")
    
    if args.quick:
        # 快速测试模式
        print("快速测试模式...")
        test_devices = ['A5GTQ24B26000732']
        for device_sn in test_devices:
            for day in range(2):
                target_date = datetime.now() - timedelta(days=day)
                for hour in range(0, 24, 4):  # 每4小时一条
                    timestamp = target_date.replace(hour=hour, minute=0, second=0)
                    data = simulator.generate_realistic_data(device_sn, timestamp)
                    try:
                        response = requests.post(API_URL, json={'data': data}, timeout=5)
                        status = "✓" if response.status_code == 200 else "✗"
                        print(f"{status} {device_sn} {timestamp.strftime('%m-%d %H:%M')}")
                    except Exception as e:
                        print(f"✗ {device_sn} {timestamp.strftime('%m-%d %H:%M')} - {e}")
        
        # 生成基线
        simulator.generate_baselines(2)
        print("快速测试完成!")
        return
    
    # 获取用户
    users = simulator.get_users(limit=args.users)
    if not users:
        print("没有找到用户数据")
        return
    
    print(f"找到{len(users)}个用户:")
    for user in users:
        print(f"- {user['user_name']} ({user['device_sn']})")
    
    print(f"\n配置:")
    print(f"- 模拟天数: {args.days}天")
    print(f"- 数据间隔: {args.interval}分钟")
    print(f"- 基线天数: {args.baseline_days}天")
    
    # 确认
    if not args.no_confirm:
        confirm = input("\n是否开始模拟？(y/N): ")
        if confirm.lower() != 'y':
            print("取消操作")
            return
    
    print("\n开始模拟数据...")
    start_time = time.time()
    
    # 并发处理
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(simulator.simulate_user_period, user, args.days, args.interval): user for user in users}
        
        for future in as_completed(futures):
            user = futures[future]
            try:
                days = future.result()
                print(f"✓ 用户{user['user_name']}完成: {days}天")
            except Exception as e:
                print(f"✗ 用户{user['user_name']}失败: {e}")
    
    elapsed = time.time() - start_time
    print(f"\n数据上传完成!")
    print(f"成功: {simulator.success_count}条")
    print(f"失败: {simulator.error_count}条")
    print(f"耗时: {elapsed:.1f}秒")
    
    # 生成基线
    if simulator.success_count > 0:
        print("\n开始生成基线...")
        baseline_count = simulator.generate_baselines(args.baseline_days)
        print(f"基线生成完成: {baseline_count}天")
    
    print("\n=== 模拟完成 ===")

if __name__ == "__main__":
    main() 