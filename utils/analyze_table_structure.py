#!/usr/bin/env python3
"""分析表结构和数据情况"""
import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def analyze_tables():
    conn = pymysql.connect(
        host=MYSQL_HOST, 
        port=MYSQL_PORT, 
        user=MYSQL_USER, 
        password=MYSQL_PASSWORD, 
        database=MYSQL_DATABASE
    )
    
    try:
        with conn.cursor() as cursor:
            print('📊 分析主表 t_user_health_data 结构:')
            cursor.execute('DESCRIBE t_user_health_data')
            main_columns = cursor.fetchall()
            print('主表字段:')
            for col in main_columns:
                print(f'  {col[0]} - {col[1]} - {col[2]} - {col[3]}')
            
            print('\n📊 检查主表数据量和样本:')
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data')
            total_count = cursor.fetchone()[0]
            print(f'主表总数据: {total_count}条')
            
            # 检查是否有org_id和user_id字段
            main_field_names = [col[0] for col in main_columns]
            has_org_id = 'org_id' in main_field_names
            has_user_id = 'user_id' in main_field_names
            print(f'主表包含org_id字段: {has_org_id}')
            print(f'主表包含user_id字段: {has_user_id}')
            
            # 检查需要迁移的字段
            migrate_fields = ['sleep_data', 'exercise_daily_data', 'workout_data', 'scientific_sleep_data', 'exercise_week_data']
            existing_migrate_fields = [field for field in migrate_fields if field in main_field_names]
            print(f'需要迁移的字段: {existing_migrate_fields}')
            
            # 检查样本数据
            if total_count > 0:
                print('\n📊 主表样本数据:')
                sample_fields = ['id', 'device_sn', 'timestamp', 'create_time']
                if has_org_id: sample_fields.append('org_id')
                if has_user_id: sample_fields.append('user_id')
                sample_fields.extend(existing_migrate_fields)
                
                cursor.execute(f'SELECT {",".join(sample_fields)} FROM t_user_health_data LIMIT 3')
                samples = cursor.fetchall()
                for i, row in enumerate(samples):
                    print(f'  样本{i+1}: {dict(zip(sample_fields, row))}')
            
            print('\n📊 检查每日表 t_user_health_data_daily:')
            try:
                cursor.execute('DESCRIBE t_user_health_data_daily')
                daily_columns = cursor.fetchall()
                print('每日表字段:')
                for col in daily_columns:
                    print(f'  {col[0]} - {col[1]} - {col[2]} - {col[3]}')
                
                cursor.execute('SELECT COUNT(*) FROM t_user_health_data_daily')
                daily_count = cursor.fetchone()[0]
                print(f'每日表数据: {daily_count}条')
            except Exception as e:
                print(f'每日表不存在或查询失败: {e}')
            
            print('\n📊 检查每周表 t_user_health_data_weekly:')
            try:
                cursor.execute('DESCRIBE t_user_health_data_weekly')
                weekly_columns = cursor.fetchall()
                print('每周表字段:')
                for col in weekly_columns:
                    print(f'  {col[0]} - {col[1]} - {col[2]} - {col[3]}')
                
                cursor.execute('SELECT COUNT(*) FROM t_user_health_data_weekly')
                weekly_count = cursor.fetchone()[0]
                print(f'每周表数据: {weekly_count}条')
            except Exception as e:
                print(f'每周表不存在或查询失败: {e}')
            
            print('\n📊 检查设备与用户关联表:')
            try:
                cursor.execute('SHOW TABLES LIKE "%user%"')
                user_tables = cursor.fetchall()
                print('用户相关表:')
                for table in user_tables:
                    print(f'  {table[0]}')
                
                # 检查sys_user表
                cursor.execute('DESCRIBE sys_user')
                user_columns = cursor.fetchall()
                user_field_names = [col[0] for col in user_columns]
                print(f'sys_user表字段: {user_field_names}')
                
                if 'device_sn' in user_field_names:
                    cursor.execute('SELECT COUNT(*) FROM sys_user WHERE device_sn IS NOT NULL AND device_sn != ""')
                    user_device_count = cursor.fetchone()[0]
                    print(f'sys_user表中有设备号的用户: {user_device_count}个')
                    
                    # 样本数据
                    cursor.execute('SELECT id, user_name, device_sn, org_id FROM sys_user WHERE device_sn IS NOT NULL AND device_sn != "" LIMIT 3')
                    user_samples = cursor.fetchall()
                    for row in user_samples:
                        print(f'  用户样本: ID:{row[0]}, 用户名:{row[1]}, 设备号:{row[2]}, 组织ID:{row[3]}')
                        
            except Exception as e:
                print(f'用户表查询失败: {e}')
                
    except Exception as e:
        print(f"❌ 分析失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_tables() 