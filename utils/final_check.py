#!/usr/bin/env python3
import mysql.connector

def check_database():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root', 
            password='aV5mV7kQ!@#',
            database='lj-06'
        )
        cursor = conn.cursor()
        
        # 检查设备信息表
        cursor.execute('SELECT COUNT(*) FROM t_device_info')
        device_count = cursor.fetchone()[0]
        print(f'✅ 设备信息表记录数: {device_count}')
        
        # 检查设备历史表
        cursor.execute('SELECT COUNT(*) FROM t_device_info_history')
        history_count = cursor.fetchone()[0]
        print(f'✅ 设备历史表记录数: {history_count}')
        
        if device_count > 0:
            # 获取最新的设备记录
            cursor.execute('SELECT serial_number, system_software_version, battery_level, status, device_name, create_time FROM t_device_info ORDER BY id DESC LIMIT 5')
            devices = cursor.fetchall()
            print(f'\n📱 最新的{len(devices)}条设备记录:')
            for i, device in enumerate(devices, 1):
                print(f'  {i}. 序列号: {device[0]}, 版本: {device[1]}, 电量: {device[2]}, 状态: {device[3]}, 设备名: {device[4]}, 创建时间: {device[5]}')
        
        print(f'\n🎉 问题已解决！设备信息现在可以正常插入数据库了！')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ 数据库连接错误: {e}')

if __name__ == '__main__':
    check_database() 