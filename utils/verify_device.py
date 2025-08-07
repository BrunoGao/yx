#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证设备数据脚本"""
import mysql.connector

# 数据库配置
DB_CONFIG = {'host':'127.0.0.1','user':'root','password':'aV5mV7kQ!@#','database':'lj-06','port':3306}

def verify_device(serial_number):
    """验证设备数据"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        sql = """
        SELECT serial_number, system_software_version, device_name, 
               battery_level, status, user_id, org_id, create_time
        FROM t_device_info 
        WHERE serial_number = %s
        """
        
        cursor.execute(sql, (serial_number,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ 找到设备数据:")
            print(f"   序列号: {result[0]}")
            print(f"   系统版本: {result[1]}")
            print(f"   设备名: {result[2]}")
            print(f"   电池: {result[3]}%")
            print(f"   状态: {result[4]}")
            print(f"   用户ID: {result[5]}")
            print(f"   组织ID: {result[6]}")
            print(f"   创建时间: {result[7]}")
            return True
        else:
            print(f"❌ 未找到设备 {serial_number}")
            return False
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return False
    finally:
        if conn:
            conn.close()

def check_total_devices():
    """检查设备总数"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM t_device_info")
        total = cursor.fetchone()[0]
        print(f"📊 设备总数: {total}")
        
        cursor.execute("SELECT COUNT(*) FROM t_device_info WHERE user_id IS NOT NULL")
        bound = cursor.fetchone()[0]
        print(f"👥 绑定用户的设备: {bound}")
        
        return total, bound
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return 0, 0
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔍 验证设备数据")
    print("="*40)
    
    # 验证特定设备
    verify_device("A5GTQ24B26000732")
    print()
    
    # 检查总数
    check_total_devices() 