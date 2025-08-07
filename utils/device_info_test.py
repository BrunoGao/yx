#!/usr/bin/env python3
"""设备信息上传测试脚本 - 使用指定设备序列号"""
import requests,json,random,time
from datetime import datetime,timedelta

# 配置
DEVICE_API="http://localhost:5001/upload_device_info" #设备信息上传API#
TEST_DEVICES=["A5GTQ2460300053","A5GTQ24919001193","A5GTQ24A17000135"] #测试设备列表#

class DeviceInfoTester:
    def __init__(self):
        self.session=requests.Session()
        self.device_states={} #设备状态缓存#
        self.init_device_states()
        
    def init_device_states(self): #初始化设备状态#
        for device_sn in TEST_DEVICES:
            self.device_states[device_sn]={'battery_level':random.randint(30,100),'voltage':random.randint(3500,4200),'charging_status':'NONE','wear_state':random.choice([0,1]),'last_charge_time':datetime.now()-timedelta(hours=random.randint(1,12))}
            
    def update_device_state(self,device_sn): #更新设备状态(模拟真实变化)#
        state=self.device_states[device_sn];now=datetime.now();time_since_charge=now-state['last_charge_time'];battery_drain=int(time_since_charge.total_seconds()/3600*2);state['battery_level']=max(10,state['battery_level']-battery_drain) #电量随时间降低#
        if state['battery_level']<20 and random.random()<0.3:state['charging_status']='CHARGING';state['battery_level']=min(100,state['battery_level']+5);state['last_charge_time']=now if state['battery_level']>=90 else state['last_charge_time'] #低电量时可能充电#
        if random.random()<0.05:state['wear_state']=1-state['wear_state'] #佩戴状态偶尔变化#
        state['voltage']=3500+(state['battery_level']*7) #电压与电量关联#
        
    def generate_device_info(self,device_sn,timestamp=None): #生成设备信息数据#
        if timestamp is None:timestamp=datetime.now()
        state=self.device_states[device_sn];device_models=['HUAWEI WATCH 4-DD6','HUAWEI WATCH GT 3-A1B','HUAWEI WATCH FIT 2-C2D','HUAWEI WATCH GT 2e-E3F']
        return {'System Software Version':f'ARC-AL00CN {random.randint(4,5)}.{random.randint(0,2)}.{random.randint(0,9)}.{random.randint(100,999)}(SP{random.randint(10,99)}C{random.randint(100,999)}E{random.randint(100,999)}R{random.randint(100,999)}P{random.randint(100,999)})','Wifi Address':':'.join([f'{random.randint(0,255):02x}' for _ in range(6)]),'Bluetooth Address':':'.join([f'{random.randint(0,255):02X}' for _ in range(6)]),'IP Address':f'192.168.{random.randint(1,254)}.{random.randint(2,254)}\\nfe80::{random.randint(0,255):x}:{random.randint(0,255):x}ff:fef{random.randint(0,15):x}:a{random.randint(100,999):x}','Network Access Mode':random.choice([1,2,3]),'SerialNumber':device_sn,'Device Name':random.choice(device_models),'IMEI':f'{random.randint(100000000000000,999999999999999)}','batteryLevel':state['battery_level'],'voltage':state['voltage'],'chargingStatus':'CHARGING' if state['charging_status']=='CHARGING' else 'NONE','status':'ACTIVE','wearState':state['wear_state'],'timestamp':timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        
    def upload_device_info(self,device_sn,timestamp=None): #上传设备信息#
        try:
            self.update_device_state(device_sn);data=self.generate_device_info(device_sn,timestamp);response=self.session.post(DEVICE_API,json=data,timeout=10)
            if response.status_code==200:print(f"✅ 设备{device_sn}上传成功: 电量{data['batteryLevel']}% 状态{data['status']}");return True
            else:print(f"❌ 设备{device_sn}上传失败: {response.status_code} - {response.text[:100]}");return False
        except Exception as e:print(f"❌ 设备{device_sn}上传异常: {e}");return False
        
    def test_initial_upload(self): #测试初始上传5个#
        print("🔧 开始初始测试 - 上传5个设备信息...")
        success_count=0
        for i in range(5):
            device_sn=random.choice(TEST_DEVICES);success=self.upload_device_info(device_sn);success_count+=success;time.sleep(2) #间隔2秒#
        print(f"📊 初始测试完成: {success_count}/5 成功");return success_count==5
        
    def upload_week_data(self): #上传过去一周数据#
        print("📅 开始上传过去一周数据 (5分钟间隔)...")
        end_time=datetime.now();start_time=end_time-timedelta(days=7);current_time=start_time;upload_count=0;success_count=0
        
        while current_time<=end_time:
            device_sn=random.choice(TEST_DEVICES);success=self.upload_device_info(device_sn,current_time);upload_count+=1;success_count+=success
            if upload_count%10==0:print(f"⏳ 已上传{upload_count}条 成功{success_count}条 当前时间{current_time.strftime('%m-%d %H:%M')}")
            current_time+=timedelta(minutes=5);time.sleep(0.1) #快速模拟，每0.1秒一条#
            
        print(f"🎉 一周数据上传完成: {success_count}/{upload_count} 成功")
        
    def run(self): #主运行函数#
        print("=== 设备信息上传测试 ===")
        print(f"测试设备: {', '.join(TEST_DEVICES)}")
        print(f"API地址: {DEVICE_API}")
        print("=" * 40)
        
        # 初始测试
        if self.test_initial_upload():
            print("✅ 初始测试通过，开始上传一周数据...")
            time.sleep(2)
            self.upload_week_data()
        else:
            print("❌ 初始测试失败，请检查API状态")

if __name__=="__main__":
    tester=DeviceInfoTester()
    tester.run() 