#!/usr/bin/env python3 #检查设备表结构
import mysql.connector

DB_CONFIG = {'host':'127.0.0.1','user':'root','password':'aV5mV7kQ!@#','database':'lj-06','port':3306}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("🔍 检查 t_device_info 表结构:")
    cursor.execute("DESCRIBE t_device_info")
    columns = cursor.fetchall()
    
    for col in columns:
        print(f"  {col[0]} - {col[1]} - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
    
    print("\n🔍 检查 t_device_info_history 表结构:")
    cursor.execute("DESCRIBE t_device_info_history")
    columns = cursor.fetchall()
    
    for col in columns:
        print(f"  {col[0]} - {col[1]} - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
    
    print("\n🔍 检查设备数据样例:")
    cursor.execute("SELECT * FROM t_device_info LIMIT 3")
    devices = cursor.fetchall()
    
    if devices:
        cursor.execute("SHOW COLUMNS FROM t_device_info")
        column_names = [col[0] for col in cursor.fetchall()]
        print(f"字段名: {column_names}")
        
        for device in devices:
            print(f"设备数据: {dict(zip(column_names, device))}")
    else:
        print("暂无设备数据")
    
    conn.close()
    
except Exception as e:
    print(f"❌ 检查失败: {e}") 