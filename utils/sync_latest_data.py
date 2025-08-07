#!/usr/bin/env python3
"""同步最新数据到分区表"""
import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def sync_latest_data():
    conn = pymysql.connect(
        host=MYSQL_HOST, 
        port=MYSQL_PORT, 
        user=MYSQL_USER, 
        password=MYSQL_PASSWORD, 
        database=MYSQL_DATABASE,
        autocommit=False
    )
    
    try:
        with conn.cursor() as cursor:
            print('🔄 同步最新数据到分区表...')
            print('=' * 80)
            
            # 检查主表和分区视图的时间范围差异
            cursor.execute('SELECT MAX(timestamp) FROM t_user_health_data')
            main_max_time = cursor.fetchone()[0]
            print(f"主表最新时间: {main_max_time}")
            
            cursor.execute('SELECT MAX(timestamp) FROM t_user_health_data_partitioned')
            partition_max_time = cursor.fetchone()[0]
            print(f"分区视图最新时间: {partition_max_time}")
            
            if main_max_time <= partition_max_time:
                print("✅ 分区表数据已是最新，无需同步")
                return
            
            # 查询需要同步的数据
            cursor.execute("""
                SELECT COUNT(*) FROM t_user_health_data 
                WHERE timestamp > %s
            """, (partition_max_time,))
            missing_count = cursor.fetchone()[0]
            print(f"需要同步的数据: {missing_count}条")
            
            if missing_count == 0:
                print("✅ 无需同步数据")
                return
            
            # 按月分组查询需要同步的数据
            cursor.execute("""
                SELECT DATE_FORMAT(timestamp, '%%Y%%m') as month, COUNT(*) as count
                FROM t_user_health_data 
                WHERE timestamp > %s
                GROUP BY DATE_FORMAT(timestamp, '%%Y%%m')
                ORDER BY month
            """, (partition_max_time,))
            month_stats = cursor.fetchall()
            
            print("需要同步的数据分布:")
            for month, count in month_stats:
                print(f"  {month}: {count}条")
            
            total_synced = 0
            
            for month, count in month_stats:
                table_name = f't_user_health_data_{month}'
                print(f"\n🔄 同步 {month} 数据到 {table_name}...")
                
                # 检查目标表是否存在
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                if not cursor.fetchone():
                    print(f"  ❌ 表 {table_name} 不存在，跳过")
                    continue
                
                # 查询需要同步的数据（只查询分区表存在的字段）
                cursor.execute("""
                    SELECT 
                     heart_rate, pressure_high, pressure_low, blood_oxygen, stress, 
                     temperature, step, timestamp, latitude, longitude, altitude, 
                     device_sn, distance, calorie, is_deleted, create_user, create_user_id, 
                     create_time, update_user, update_user_id, update_time, 
                     org_id, user_id
                    FROM t_user_health_data 
                    WHERE DATE_FORMAT(timestamp, '%%Y%%m') = %s
                    AND timestamp > %s
                """, (month, partition_max_time))
                
                records = cursor.fetchall()
                print(f"  查询到 {len(records)} 条记录")
                
                if len(records) == 0:
                    continue
                
                # 批量插入数据（只插入分区表存在的字段）
                insert_sql = f"""
                    INSERT INTO {table_name} 
                    (heart_rate, pressure_high, pressure_low, blood_oxygen, stress, 
                     temperature, step, timestamp, latitude, longitude, altitude, 
                     device_sn, distance, calorie, is_deleted, create_user, create_user_id, 
                     create_time, update_user, update_user_id, update_time, 
                     org_id, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.executemany(insert_sql, records)
                synced_count = cursor.rowcount
                total_synced += synced_count
                
                print(f"  ✅ 同步 {synced_count} 条记录到 {table_name}")
                conn.commit()
            
            print(f"\n✅ 数据同步完成: 总计 {total_synced} 条记录")
            
            # 验证同步结果
            print("\n📊 验证同步结果:")
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data_partitioned')
            new_partition_count = cursor.fetchone()[0]
            print(f"  分区视图总记录: {new_partition_count}条")
            
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data')
            main_count = cursor.fetchone()[0]
            print(f"  主表总记录: {main_count}条")
            
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data_partitioned WHERE org_id = 2')
            org2_count = cursor.fetchone()[0]
            print(f"  分区视图中org_id=2的记录: {org2_count}条")
            
            cursor.execute('SELECT MAX(timestamp) FROM t_user_health_data_partitioned')
            new_partition_max_time = cursor.fetchone()[0]
            print(f"  分区视图最新时间: {new_partition_max_time}")
            
            if new_partition_count == main_count:
                print("  ✅ 主表与分区表数据量一致")
            else:
                print(f"  ❌ 主表与分区表数据量不一致 (差异: {abs(main_count - new_partition_count)}条)")
                
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    sync_latest_data() 