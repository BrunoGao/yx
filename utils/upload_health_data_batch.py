#!/usr/bin/env python3 #批量上传健康数据
import mysql.connector,requests,json,random,time
from datetime import datetime
from data_cleanup_and_generator import DataCleanupAndGenerator

def upload_health_for_all_users():
    """为所有用户上传健康数据"""
    gen = DataCleanupAndGenerator()
    
    if not gen.connect_db():
        return False
    
    try:
        # 获取所有有设备的用户
        gen.cursor.execute("""
            SELECT device_sn, real_name 
            FROM sys_user 
            WHERE device_sn IS NOT NULL AND device_sn != '' AND device_sn != 'NULL'
            ORDER BY id
        """)
        users = gen.cursor.fetchall()
        
        if not users:
            print("❌ 未找到有效用户")
            return False
        
        print(f"🏥 找到 {len(users)} 个用户，开始上传健康数据...")
        
        success_count = 0
        failed_count = 0
        
        for user in users:
            device_sn = user['device_sn']
            user_name = user['real_name']
            
            try:
                # 生成健康数据
                health_data = gen.generate_health_data(device_sn, user_name)
                
                # 上传健康数据
                if gen.upload_health_data(health_data):
                    success_count += 1
                    if success_count % 10 == 0:
                        print(f"✅ 已上传 {success_count}/{len(users)} 个用户的健康数据")
                else:
                    failed_count += 1
                    
            except Exception as e:
                print(f"❌ 为用户 {device_sn} 上传健康数据失败: {e}")
                failed_count += 1
        
        print(f"🎯 健康数据上传完成: 成功 {success_count}, 失败 {failed_count}")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ 批量上传健康数据失败: {e}")
        return False
    finally:
        if gen.conn:
            gen.conn.close()

if __name__ == "__main__":
    upload_health_for_all_users() 