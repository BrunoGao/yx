#!/usr/bin/env python3
import requests, json, random, time
from datetime import datetime, timedelta
import mysql.connector

# 配置
API_URL = "http://localhost:5001/upload_health_data"
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root', 
    'password': 'aV5mV7kQ!@#',
    'database': 'test',
    'port': 3306
}

class DeptHealthDataUploader:
    def __init__(self):
        self.session = requests.Session()
        self.success_count = 0
        self.error_count = 0
    
    def get_dept_users(self, dept_id):
        """获取部门非管理员用户"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            sql = '''
            SELECT DISTINCT u.id, u.user_name, u.device_sn
            FROM sys_user u 
            JOIN sys_user_org uo ON u.id = uo.user_id 
            WHERE uo.org_id = %s 
            AND u.device_sn IS NOT NULL 
            AND u.device_sn != '' 
            AND u.device_sn != '-' 
            AND u.is_deleted = 0
            AND NOT EXISTS (
                SELECT 1 FROM sys_user_role ur 
                JOIN sys_role r ON ur.role_id = r.id 
                WHERE ur.user_id = u.id AND r.is_admin = 1
            )
            ORDER BY u.user_name
            '''
            
            cursor.execute(sql, (dept_id,))
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            print(f"❌ 获取用户失败: {e}")
            return []
    
    def generate_realistic_data(self, device_sn, timestamp):
        """生成真实健康数据"""
        hour = timestamp.hour
        is_sleep_time = hour < 6 or hour > 22
        is_work_time = 9 <= hour <= 17
        
        base_hr = 70 if not is_sleep_time else 55
        base_stress = 30 if is_sleep_time else (50 if is_work_time else 35)
        
        # 煤矿集团总部位置(100米范围内随机)
        base_lat = 22.5500
        base_lng = 114.0500
        lat_offset = random.uniform(-0.0009, 0.0009)
        lng_offset = random.uniform(-0.0011, 0.0011)
        
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
            'latitude': f"{base_lat + lat_offset:.6f}",
            'longitude': f"{base_lng + lng_offset:.6f}",
            'altitude': '0.0',
            'stress': random.randint(base_stress-10, base_stress+15),
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sleepData': '{"code":0,"data":[{"endTimeStamp":1747440420000,"startTimeStamp":1747418280000,"type":2}],"name":"sleep","type":"history"}',
            'exerciseDailyData': '{"code":0,"data":[{"strengthTimes":2,"totalTime":5}],"name":"daily","type":"history"}',
            'exerciseWeekData': 'null',
            'scientificSleepData': 'null',
            'workoutData': '{"code":0,"data":[],"name":"workout","type":"history"}'
        }
    
    def upload_single(self, data):
        """上传单个数据点"""
        try:
            response = self.session.post(API_URL, json={'data': data}, timeout=10)
            if response.status_code == 200:
                self.success_count += 1
                return True, "成功"
            else:
                self.error_count += 1
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            self.error_count += 1
            return False, str(e)
    
    def test_upload(self, users, test_count=5):
        """测试上传数据"""
        print(f"🧪 开始测试上传 {test_count} 个数据点...")
        
        for i in range(test_count):
            # 随机选择用户和时间
            user = random.choice(users)
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 24))
            
            data = self.generate_realistic_data(user['device_sn'], timestamp)
            success, msg = self.upload_single(data)
            
            status = "✅" if success else "❌"
            print(f"{status} 测试{i+1}: {user['user_name']} ({user['device_sn']}) - {msg}")
            
            time.sleep(0.5)
        
        print(f"\n📊 测试结果: 成功{self.success_count}个, 失败{self.error_count}个")
        return self.error_count == 0
    
    def upload_week_data(self, users, interval_minutes=5):
        """上传过去一周的数据"""
        print(f"📅 开始上传过去7天的数据 (每{interval_minutes}分钟一次)...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        total_points = 0
        
        for user in users:
            print(f"\n👤 处理用户: {user['user_name']} ({user['device_sn']})")
            user_success = 0
            user_error = 0
            
            current_time = start_date
            while current_time < end_date:
                data = self.generate_realistic_data(user['device_sn'], current_time)
                success, msg = self.upload_single(data)
                
                if success:
                    user_success += 1
                else:
                    user_error += 1
                    if user_error > 5:  # 连续错误太多则跳过
                        print(f"⚠️ 错误过多，跳过用户 {user['user_name']}")
                        break
                
                current_time += timedelta(minutes=interval_minutes)
                total_points += 1
                
                if total_points % 100 == 0:
                    print(f"📈 已处理 {total_points} 个数据点...")
                
                time.sleep(0.1)  # 避免请求过快
            
            print(f"✅ {user['user_name']} 完成: 成功{user_success}个, 失败{user_error}个")
        
        print(f"\n🎉 全部完成!")
        print(f"📊 总计: 成功{self.success_count}个, 失败{self.error_count}个")

def main():
    dept_id = 1923231005240295439
    uploader = DeptHealthDataUploader()
    
    print("=== 部门健康数据上传器 ===")
    
    # 获取用户列表
    users = uploader.get_dept_users(dept_id)
    if not users:
        print("❌ 未找到部门用户")
        return
    
    print(f"👥 找到 {len(users)} 个用户:")
    for user in users:
        print(f"  - {user['user_name']} ({user['device_sn']})")
    
    # 测试上传5个数据点
    test_success = uploader.test_upload(users, 5)
    
    if test_success:
        print("\n✅ 测试成功! 开始上传完整数据...")
        confirm = input("是否继续上传过去一周的数据? (y/N): ")
        if confirm.lower() == 'y':
            uploader.upload_week_data(users, 5)
        else:
            print("取消上传")
    else:
        print("\n❌ 测试失败! 请检查API服务")

if __name__ == "__main__":
    main() 