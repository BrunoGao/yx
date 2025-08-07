#!/usr/bin/env python3
"""检查分区表字段结构"""
import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def check_partition_fields():
    conn = pymysql.connect(
        host=MYSQL_HOST, 
        port=MYSQL_PORT, 
        user=MYSQL_USER, 
        password=MYSQL_PASSWORD, 
        database=MYSQL_DATABASE
    )
    
    try:
        with conn.cursor() as cursor:
            print('📊 检查分区表字段结构:')
            cursor.execute('DESCRIBE t_user_health_data_202505')
            partition_columns = cursor.fetchall()
            partition_fields = [col[0] for col in partition_columns]
            print('分区表字段:')
            for col in partition_columns:
                print(f'  {col[0]} - {col[1]}')
            
            print('\n📊 检查主表字段结构:')
            cursor.execute('DESCRIBE t_user_health_data')
            main_columns = cursor.fetchall()
            main_fields = [col[0] for col in main_columns]
            print('主表字段:')
            for col in main_columns:
                print(f'  {col[0]} - {col[1]}')
            
            print('\n📊 字段差异分析:')
            main_only = set(main_fields) - set(partition_fields)
            partition_only = set(partition_fields) - set(main_fields)
            
            if main_only:
                print(f'主表独有字段: {list(main_only)}')
            if partition_only:
                print(f'分区表独有字段: {list(partition_only)}')
            
            common_fields = set(main_fields) & set(partition_fields)
            print(f'共同字段数量: {len(common_fields)}')
            print(f'共同字段: {sorted(list(common_fields))}')
                
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_partition_fields() 