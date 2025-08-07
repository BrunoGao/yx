#!/usr/bin/env python3
"""检查用户组织关联"""
import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def check_user_org():
    conn = pymysql.connect(
        host=MYSQL_HOST, 
        port=MYSQL_PORT, 
        user=MYSQL_USER, 
        password=MYSQL_PASSWORD, 
        database=MYSQL_DATABASE
    )
    
    try:
        with conn.cursor() as cursor:
            print('📊 检查用户组织关联:')
            cursor.execute('DESCRIBE sys_user_org')
            user_org_columns = cursor.fetchall()
            print('sys_user_org表字段:')
            for col in user_org_columns:
                print(f'  {col[0]} - {col[1]}')
            
            cursor.execute('SELECT COUNT(*) FROM sys_user_org')
            user_org_count = cursor.fetchone()[0]
            print(f'用户组织关联数据: {user_org_count}条')
            
            if user_org_count > 0:
                cursor.execute('SELECT user_id, org_id FROM sys_user_org LIMIT 5')
                samples = cursor.fetchall()
                for row in samples:
                    print(f'  用户ID:{row[0]} -> 组织ID:{row[1]}')
            
            print('\n📊 检查设备用户关联:')
            cursor.execute("""
                SELECT u.id, u.device_sn, uo.org_id 
                FROM sys_user u 
                LEFT JOIN sys_user_org uo ON u.id = uo.user_id 
                WHERE u.device_sn IS NOT NULL AND u.device_sn != '' 
                LIMIT 5
            """)
            device_user_samples = cursor.fetchall()
            for row in device_user_samples:
                print(f'  用户ID:{row[0]}, 设备号:{row[1]}, 组织ID:{row[2]}')
            
            print('\n📊 检查主表中缺失org_id和user_id的数据:')
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data WHERE org_id IS NULL OR user_id IS NULL')
            missing_count = cursor.fetchone()[0]
            print(f'缺失org_id或user_id的数据: {missing_count}条')
            
            print('\n📊 检查主表中有JSON数据的记录:')
            cursor.execute("""
                SELECT COUNT(*) FROM t_user_health_data 
                WHERE sleep_data IS NOT NULL 
                OR exercise_daily_data IS NOT NULL 
                OR workout_data IS NOT NULL 
                OR scientific_sleep_data IS NOT NULL 
                OR exercise_week_data IS NOT NULL
            """)
            json_data_count = cursor.fetchone()[0]
            print(f'包含JSON数据的记录: {json_data_count}条')
                
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_user_org() 