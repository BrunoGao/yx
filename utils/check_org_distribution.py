#!/usr/bin/env python3
"""检查org_id分布差异"""
import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def check_org_distribution():
    conn = pymysql.connect(
        host=MYSQL_HOST, 
        port=MYSQL_PORT, 
        user=MYSQL_USER, 
        password=MYSQL_PASSWORD, 
        database=MYSQL_DATABASE
    )
    
    try:
        with conn.cursor() as cursor:
            print('📊 检查分区表中org_id=2的数据:')
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data_partitioned WHERE org_id = 2')
            partition_org2 = cursor.fetchone()[0]
            print(f'分区视图中org_id=2的数据: {partition_org2}条')
            
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data WHERE org_id = 2')
            main_org2 = cursor.fetchone()[0]
            print(f'主表中org_id=2的数据: {main_org2}条')
            
            print('\n📊 检查分区表中org_id分布:')
            cursor.execute('SELECT org_id, COUNT(*) FROM t_user_health_data_partitioned GROUP BY org_id ORDER BY COUNT(*) DESC LIMIT 10')
            partition_org_dist = cursor.fetchall()
            for org_id, count in partition_org_dist:
                print(f'  org_id={org_id}: {count}条')
            
            print('\n📊 检查主表中org_id分布:')
            cursor.execute('SELECT org_id, COUNT(*) FROM t_user_health_data GROUP BY org_id ORDER BY COUNT(*) DESC LIMIT 10')
            main_org_dist = cursor.fetchall()
            for org_id, count in main_org_dist:
                print(f'  org_id={org_id}: {count}条')
            
            print('\n📊 检查分区表中NULL org_id:')
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data_partitioned WHERE org_id IS NULL')
            partition_null = cursor.fetchone()[0]
            print(f'分区视图中org_id为NULL的数据: {partition_null}条')
            
            print('\n📊 检查数据时间范围差异:')
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM t_user_health_data')
            main_time_range = cursor.fetchone()
            print(f'主表时间范围: {main_time_range[0]} 到 {main_time_range[1]}')
            
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM t_user_health_data_partitioned')
            partition_time_range = cursor.fetchone()
            print(f'分区视图时间范围: {partition_time_range[0]} 到 {partition_time_range[1]}')
                
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_org_distribution() 