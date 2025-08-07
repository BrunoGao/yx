#!/usr/bin/env python3
"""健康数据迁移脚本 - 补充org_id/user_id，迁移JSON数据，创建分区表"""
import pymysql
from datetime import datetime, timedelta
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

class HealthDataMigrator:
    def __init__(self):
        self.conn = pymysql.connect(
            host=MYSQL_HOST, 
            port=MYSQL_PORT, 
            user=MYSQL_USER, 
            password=MYSQL_PASSWORD, 
            database=MYSQL_DATABASE,
            autocommit=False
        )
    
    def step1_update_org_user_ids(self): # 步骤1: 更新主表的org_id和user_id
        """根据device_sn查询并更新org_id和user_id"""
        print("🔄 步骤1: 更新主表的org_id和user_id...")
        
        with self.conn.cursor() as cursor:
            # 查询设备与用户的关联关系
            cursor.execute("""
                SELECT u.id as user_id, u.device_sn, uo.org_id
                FROM sys_user u 
                LEFT JOIN sys_user_org uo ON u.id = uo.user_id 
                WHERE u.device_sn IS NOT NULL AND u.device_sn != '' AND u.device_sn != '-'
                AND uo.org_id IS NOT NULL
            """)
            device_mappings = cursor.fetchall()
            
            print(f"找到 {len(device_mappings)} 个设备用户映射关系")
            
            updated_count = 0
            for user_id, device_sn, org_id in device_mappings:
                print(f"  更新设备 {device_sn} -> 用户ID: {user_id}, 组织ID: {org_id}")
                
                cursor.execute("""
                    UPDATE t_user_health_data 
                    SET user_id = %s, org_id = %s, update_time = NOW()
                    WHERE device_sn = %s AND (user_id IS NULL OR org_id IS NULL)
                """, (user_id, org_id, device_sn))
                
                affected = cursor.rowcount
                updated_count += affected
                print(f"    更新了 {affected} 条记录")
            
            # 对于没有用户关联的设备，设置默认值
            print("  为无用户关联的设备设置默认值...")
            cursor.execute("""
                UPDATE t_user_health_data 
                SET user_id = 0, org_id = 1, update_time = NOW()
                WHERE user_id IS NULL OR org_id IS NULL
            """)
            default_updated = cursor.rowcount
            print(f"    设置默认值的记录: {default_updated} 条")
            
            self.conn.commit()
            print(f"✅ 步骤1完成: 总共更新 {updated_count + default_updated} 条记录")
    
    def step2_migrate_daily_data(self): # 步骤2: 迁移每日数据
        """迁移sleep_data, exercise_daily_data, workout_data, scientific_sleep_data到每日表"""
        print("\n🔄 步骤2: 迁移每日数据到t_user_health_data_daily...")
        
        with self.conn.cursor() as cursor:
            # 查询有每日数据的记录，按设备和日期分组
            cursor.execute("""
                SELECT 
                    device_sn, user_id, org_id, DATE(timestamp) as date,
                    MAX(sleep_data) as sleep_data, 
                    MAX(exercise_daily_data) as exercise_daily_data, 
                    MAX(workout_data) as workout_data, 
                    MAX(scientific_sleep_data) as scientific_sleep_data,
                    MIN(create_time) as create_time
                FROM t_user_health_data 
                WHERE (sleep_data IS NOT NULL 
                    OR exercise_daily_data IS NOT NULL 
                    OR workout_data IS NOT NULL 
                    OR scientific_sleep_data IS NOT NULL)
                AND user_id IS NOT NULL AND org_id IS NOT NULL
                GROUP BY device_sn, user_id, org_id, DATE(timestamp)
                ORDER BY date DESC
               
            """)
            daily_records = cursor.fetchall()
            
            print(f"找到 {len(daily_records)} 个每日数据分组")
            
            migrated_count = 0
            for record in daily_records:
                device_sn, user_id, org_id, date, sleep_data, exercise_daily_data, workout_data, scientific_sleep_data, create_time = record
                
                # 检查是否已存在
                cursor.execute("""
                    SELECT id FROM t_user_health_data_daily 
                    WHERE device_sn = %s AND date = %s
                """, (device_sn, date))
                
                if cursor.fetchone():
                    continue  # 已存在，跳过
                
                # 插入每日表
                cursor.execute("""
                    INSERT INTO t_user_health_data_daily 
                    (device_sn, user_id, org_id, date, sleep_data, exercise_daily_data, workout_data, create_time, update_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (device_sn, user_id, org_id, date, sleep_data, exercise_daily_data, workout_data, create_time))
                
                migrated_count += 1
                if migrated_count % 100 == 0:
                    print(f"    已迁移 {migrated_count} 条每日记录...")
                    self.conn.commit()
            
            self.conn.commit()
            print(f"✅ 步骤2完成: 迁移 {migrated_count} 条每日记录")
    
    def step3_migrate_weekly_data(self): # 步骤3: 迁移每周数据
        """迁移exercise_week_data到每周表"""
        print("\n🔄 步骤3: 迁移每周数据到t_user_health_data_weekly...")
        
        with self.conn.cursor() as cursor:
            # 查询有每周数据的记录，按设备和周分组
            cursor.execute("""
                SELECT 
                    device_sn, user_id, org_id, 
                    DATE_SUB(DATE(timestamp), INTERVAL WEEKDAY(DATE(timestamp)) DAY) as week_start,
                    MAX(exercise_week_data) as exercise_week_data,
                    MIN(create_time) as create_time
                FROM t_user_health_data 
                WHERE exercise_week_data IS NOT NULL
                AND user_id IS NOT NULL AND org_id IS NOT NULL
                GROUP BY device_sn, user_id, org_id, DATE_SUB(DATE(timestamp), INTERVAL WEEKDAY(DATE(timestamp)) DAY)
                ORDER BY week_start DESC
         
            """)
            weekly_records = cursor.fetchall()
            
            print(f"找到 {len(weekly_records)} 个每周数据分组")
            
            migrated_count = 0
            for record in weekly_records:
                device_sn, user_id, org_id, week_start, exercise_week_data, create_time = record
                
                # 检查是否已存在
                cursor.execute("""
                    SELECT id FROM t_user_health_data_weekly 
                    WHERE device_sn = %s AND week_start = %s
                """, (device_sn, week_start))
                
                if cursor.fetchone():
                    continue  # 已存在，跳过
                
                # 插入每周表
                cursor.execute("""
                    INSERT INTO t_user_health_data_weekly 
                    (device_sn, user_id, org_id, week_start, exercise_week_data, create_time, update_time)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (device_sn, user_id, org_id, week_start, exercise_week_data, create_time))
                
                migrated_count += 1
                if migrated_count % 50 == 0:
                    print(f"    已迁移 {migrated_count} 条每周记录...")
                    self.conn.commit()
            
            self.conn.commit()
            print(f"✅ 步骤3完成: 迁移 {migrated_count} 条每周记录")
    
    def step4_create_monthly_partitions(self): # 步骤4: 创建月度分区表
        """创建按月分区的表"""
        print("\n🔄 步骤4: 创建月度分区表...")
        
        # 生成需要的月份列表
        start_date = datetime(2024, 11, 1)
        end_date = datetime(2025, 6, 1)
        months = []
        
        current = start_date
        while current < end_date:
            months.append(current.strftime('%Y%m'))
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        with self.conn.cursor() as cursor:
            for month in months:
                table_name = f't_user_health_data_{month}'
                print(f"  创建分区表: {table_name}")
                
                # 检查表是否存在
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                if cursor.fetchone():
                    print(f"    表 {table_name} 已存在，跳过创建")
                    continue
                
                # 创建分区表
                create_sql = f"""
                CREATE TABLE {table_name} (
                    id int NOT NULL AUTO_INCREMENT,
                    phone_number varchar(20) DEFAULT NULL,
                    heart_rate int DEFAULT NULL,
                    pressure_high int DEFAULT NULL,
                    pressure_low int DEFAULT NULL,
                    blood_oxygen int DEFAULT NULL,
                    stress int DEFAULT NULL,
                    temperature double(5,2) DEFAULT NULL,
                    step int DEFAULT NULL,
                    timestamp datetime NOT NULL,
                    user_name varchar(255) NOT NULL,
                    latitude decimal(10,6) DEFAULT NULL,
                    longitude decimal(10,6) DEFAULT NULL,
                    altitude double DEFAULT NULL,
                    device_sn varchar(255) NOT NULL,
                    distance double DEFAULT NULL,
                    calorie double DEFAULT NULL,
                    is_deleted tinyint(1) NOT NULL DEFAULT '0',
                    create_user varchar(255) DEFAULT NULL,
                    create_user_id bigint DEFAULT NULL,
                    create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    update_user varchar(255) DEFAULT NULL,
                    update_user_id bigint DEFAULT NULL,
                    update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    upload_method enum('wifi','bluetooth') NOT NULL DEFAULT 'wifi',
                    org_id bigint DEFAULT NULL,
                    user_id bigint DEFAULT NULL,
                    PRIMARY KEY (id),
                    KEY idx_device_sn (device_sn),
                    KEY idx_timestamp (timestamp),
                    KEY idx_user_id (user_id),
                    KEY idx_org_id (org_id),
                    KEY idx_create_time (create_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
                """
                
                cursor.execute(create_sql)
                print(f"    ✅ 创建表 {table_name} 成功")
            
            self.conn.commit()
            print(f"✅ 步骤4完成: 创建了 {len(months)} 个月度分区表")
    
    def step5_migrate_to_partitions(self): # 步骤5: 迁移数据到分区表
        """将主表数据迁移到对应的月度分区表"""
        print("\n🔄 步骤5: 迁移数据到月度分区表...")
        
        with self.conn.cursor() as cursor:
            # 查询数据按月分组
            cursor.execute("""
                SELECT DATE_FORMAT(timestamp, '%Y%m') as month, COUNT(*) as count
                FROM t_user_health_data 
                GROUP BY DATE_FORMAT(timestamp, '%Y%m')
                ORDER BY month
            """)
            month_stats = cursor.fetchall()
            
            print("数据分布:")
            for month, count in month_stats:
                print(f"  {month}: {count}条")
            
            total_migrated = 0
            for month, count in month_stats:
                if month < '202411' or month > '202505':
                    print(f"  跳过月份 {month} (超出分区范围)")
                    continue
                
                table_name = f't_user_health_data_{month}'
                print(f"  迁移 {month} 数据到 {table_name}...")
                
                # 检查目标表是否有数据
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                existing_count = cursor.fetchone()[0]
                if existing_count > 0:
                    print(f"    表 {table_name} 已有 {existing_count} 条数据，跳过迁移")
                    continue
                
                # 批量迁移数据
                cursor.execute(f"""
                    INSERT INTO {table_name} 
                    (phone_number, heart_rate, pressure_high, pressure_low, blood_oxygen, stress, 
                     temperature, step, timestamp, user_name, latitude, longitude, altitude, 
                     device_sn, distance, calorie, is_deleted, create_user, create_user_id, 
                     create_time, update_user, update_user_id, update_time, upload_method, 
                     org_id, user_id)
                    SELECT 
                     phone_number, heart_rate, pressure_high, pressure_low, blood_oxygen, stress, 
                     temperature, step, timestamp, user_name, latitude, longitude, altitude, 
                     device_sn, distance, calorie, is_deleted, create_user, create_user_id, 
                     create_time, update_user, update_user_id, update_time, upload_method, 
                     org_id, user_id
                    FROM t_user_health_data 
                    WHERE DATE_FORMAT(timestamp, '%Y%m') = '{month}'
                """)
                
                migrated = cursor.rowcount
                total_migrated += migrated
                print(f"    ✅ 迁移 {migrated} 条记录到 {table_name}")
                
                self.conn.commit()
            
            print(f"✅ 步骤5完成: 总共迁移 {total_migrated} 条记录到分区表")
    
    def step6_create_partition_view(self): # 步骤6: 创建分区视图
        """创建统一的分区视图"""
        print("\n🔄 步骤6: 创建分区视图...")
        
        with self.conn.cursor() as cursor:
            # 删除旧视图
            cursor.execute("DROP VIEW IF EXISTS t_user_health_data_partitioned")
            
            # 创建新的分区视图
            view_sql = """
            CREATE VIEW t_user_health_data_partitioned AS
            SELECT * FROM t_user_health_data_202411
            UNION ALL SELECT * FROM t_user_health_data_202412
            UNION ALL SELECT * FROM t_user_health_data_202501
            UNION ALL SELECT * FROM t_user_health_data_202502
            UNION ALL SELECT * FROM t_user_health_data_202503
            UNION ALL SELECT * FROM t_user_health_data_202504
            UNION ALL SELECT * FROM t_user_health_data_202505
            """
            
            cursor.execute(view_sql)
            self.conn.commit()
            
            # 验证视图
            cursor.execute("SELECT COUNT(*) FROM t_user_health_data_partitioned")
            view_count = cursor.fetchone()[0]
            print(f"✅ 步骤6完成: 分区视图包含 {view_count} 条记录")
    
    def step7_cleanup_main_table(self): # 步骤7: 清理主表JSON字段
        """清理主表中已迁移的JSON字段"""
        print("\n🔄 步骤7: 清理主表JSON字段...")
        
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE t_user_health_data 
                SET sleep_data = NULL, 
                    exercise_daily_data = NULL, 
                    workout_data = NULL, 
                    scientific_sleep_data = NULL, 
                    exercise_week_data = NULL,
                    update_time = NOW()
                WHERE sleep_data IS NOT NULL 
                   OR exercise_daily_data IS NOT NULL 
                   OR workout_data IS NOT NULL 
                   OR scientific_sleep_data IS NOT NULL 
                   OR exercise_week_data IS NOT NULL
            """)
            
            cleaned_count = cursor.rowcount
            self.conn.commit()
            print(f"✅ 步骤7完成: 清理 {cleaned_count} 条记录的JSON字段")
    
    def run_migration(self): # 执行完整迁移
        """执行完整的数据迁移流程"""
        print("🚀 开始健康数据迁移...")
        print("=" * 80)
        
        try:
            self.step1_update_org_user_ids()
            self.step2_migrate_daily_data()
            self.step3_migrate_weekly_data()
            self.step4_create_monthly_partitions()
            self.step5_migrate_to_partitions()
            self.step6_create_partition_view()
            self.step7_cleanup_main_table()
            
            print("\n" + "=" * 80)
            print("🎉 数据迁移完成!")
            
            # 最终验证
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM t_user_health_data_daily")
                daily_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM t_user_health_data_weekly")
                weekly_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM t_user_health_data_partitioned")
                partition_count = cursor.fetchone()[0]
                
                print(f"📊 最终统计:")
                print(f"  每日表记录: {daily_count}条")
                print(f"  每周表记录: {weekly_count}条")
                print(f"  分区视图记录: {partition_count}条")
                
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            self.conn.rollback()
            raise
        finally:
            self.conn.close()

if __name__ == "__main__":
    migrator = HealthDataMigrator()
    migrator.run_migration() 