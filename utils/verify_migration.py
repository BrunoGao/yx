#!/usr/bin/env python3
"""验证数据迁移结果"""
import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def verify_migration():
    conn = pymysql.connect(
        host=MYSQL_HOST, 
        port=MYSQL_PORT, 
        user=MYSQL_USER, 
        password=MYSQL_PASSWORD, 
        database=MYSQL_DATABASE
    )
    
    try:
        with conn.cursor() as cursor:
            print('🔍 验证数据迁移结果...')
            print('=' * 80)
            
            # 1. 验证主表org_id和user_id更新
            print('📊 1. 主表org_id和user_id更新情况:')
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data WHERE org_id IS NULL OR user_id IS NULL')
            missing_count = cursor.fetchone()[0]
            print(f'  缺失org_id或user_id的记录: {missing_count}条')
            
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data WHERE org_id IS NOT NULL AND user_id IS NOT NULL')
            complete_count = cursor.fetchone()[0]
            print(f'  完整org_id和user_id的记录: {complete_count}条')
            
            # 2. 验证JSON字段清理
            print('\n📊 2. 主表JSON字段清理情况:')
            cursor.execute("""
                SELECT COUNT(*) FROM t_user_health_data 
                WHERE sleep_data IS NOT NULL 
                OR exercise_daily_data IS NOT NULL 
                OR workout_data IS NOT NULL 
                OR scientific_sleep_data IS NOT NULL 
                OR exercise_week_data IS NOT NULL
            """)
            remaining_json = cursor.fetchone()[0]
            print(f'  主表剩余JSON数据记录: {remaining_json}条')
            
            # 3. 验证每日表数据
            print('\n📊 3. 每日表数据情况:')
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data_daily')
            daily_total = cursor.fetchone()[0]
            print(f'  每日表总记录: {daily_total}条')
            
            cursor.execute("""
                SELECT COUNT(*) FROM t_user_health_data_daily 
                WHERE sleep_data IS NOT NULL 
                OR exercise_daily_data IS NOT NULL 
                OR workout_data IS NOT NULL
            """)
            daily_with_data = cursor.fetchone()[0]
            print(f'  包含数据的每日记录: {daily_with_data}条')
            
            # 样本数据
            cursor.execute("""
                SELECT device_sn, date, 
                       CASE WHEN sleep_data IS NOT NULL THEN '有睡眠数据' ELSE '无' END as sleep,
                       CASE WHEN exercise_daily_data IS NOT NULL THEN '有运动数据' ELSE '无' END as exercise,
                       CASE WHEN workout_data IS NOT NULL THEN '有锻炼数据' ELSE '无' END as workout
                FROM t_user_health_data_daily 
                ORDER BY date DESC 
                LIMIT 5
            """)
            daily_samples = cursor.fetchall()
            print('  每日表样本数据:')
            for row in daily_samples:
                print(f'    设备:{row[0]}, 日期:{row[1]}, 睡眠:{row[2]}, 运动:{row[3]}, 锻炼:{row[4]}')
            
            # 4. 验证每周表数据
            print('\n📊 4. 每周表数据情况:')
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data_weekly')
            weekly_total = cursor.fetchone()[0]
            print(f'  每周表总记录: {weekly_total}条')
            
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data_weekly WHERE exercise_week_data IS NOT NULL')
            weekly_with_data = cursor.fetchone()[0]
            print(f'  包含数据的每周记录: {weekly_with_data}条')
            
            # 样本数据
            cursor.execute("""
                SELECT device_sn, week_start,
                       CASE WHEN exercise_week_data IS NOT NULL THEN '有每周运动数据' ELSE '无' END as week_exercise
                FROM t_user_health_data_weekly 
                ORDER BY week_start DESC 
                LIMIT 5
            """)
            weekly_samples = cursor.fetchall()
            print('  每周表样本数据:')
            for row in weekly_samples:
                print(f'    设备:{row[0]}, 周开始:{row[1]}, 每周运动:{row[2]}')
            
            # 5. 验证分区表数据
            print('\n📊 5. 分区表数据情况:')
            partition_tables = [
                't_user_health_data_202411',
                't_user_health_data_202412',
                't_user_health_data_202501',
                't_user_health_data_202502',
                't_user_health_data_202503',
                't_user_health_data_202504',
                't_user_health_data_202505'
            ]
            
            total_partition_count = 0
            for table in partition_tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                total_partition_count += count
                print(f'  {table}: {count}条')
            
            print(f'  分区表总计: {total_partition_count}条')
            
            # 6. 验证分区视图
            print('\n📊 6. 分区视图数据情况:')
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data_partitioned')
            view_count = cursor.fetchone()[0]
            print(f'  分区视图总记录: {view_count}条')
            
            # 验证视图与分区表数据一致性
            if view_count == total_partition_count:
                print('  ✅ 分区视图与分区表数据一致')
            else:
                print(f'  ❌ 分区视图与分区表数据不一致 (视图:{view_count}, 分区表:{total_partition_count})')
            
            # 7. 验证数据完整性
            print('\n📊 7. 数据完整性验证:')
            cursor.execute('SELECT COUNT(*) FROM t_user_health_data')
            main_count = cursor.fetchone()[0]
            print(f'  主表记录: {main_count}条')
            print(f'  分区表记录: {total_partition_count}条')
            
            if main_count == total_partition_count:
                print('  ✅ 主表与分区表数据量一致')
            else:
                print(f'  ❌ 主表与分区表数据量不一致')
            
            # 8. 测试查询接口
            print('\n📊 8. 测试查询接口兼容性:')
            # 测试分区视图查询
            cursor.execute("""
                SELECT COUNT(*) FROM t_user_health_data_partitioned 
                WHERE org_id = 2 
                AND timestamp >= '2025-02-01' 
                AND timestamp <= '2025-05-28'
            """)
            partition_query_count = cursor.fetchone()[0]
            print(f'  分区视图查询结果: {partition_query_count}条')
            
            # 测试主表查询
            cursor.execute("""
                SELECT COUNT(*) FROM t_user_health_data 
                WHERE org_id = 2 
                AND timestamp >= '2025-02-01' 
                AND timestamp <= '2025-05-28'
            """)
            main_query_count = cursor.fetchone()[0]
            print(f'  主表查询结果: {main_query_count}条')
            
            if partition_query_count == main_query_count:
                print('  ✅ 查询结果一致，接口兼容性良好')
            else:
                print(f'  ❌ 查询结果不一致')
            
            print('\n' + '=' * 80)
            print('🎉 数据迁移验证完成!')
            
            # 总结
            success_items = []
            if missing_count == 0:
                success_items.append('org_id/user_id更新完整')
            if remaining_json == 0:
                success_items.append('JSON字段清理完成')
            if daily_total > 0:
                success_items.append(f'每日表迁移成功({daily_total}条)')
            if weekly_total > 0:
                success_items.append(f'每周表迁移成功({weekly_total}条)')
            if view_count == total_partition_count:
                success_items.append('分区视图创建成功')
            if main_count == total_partition_count:
                success_items.append('数据完整性验证通过')
            
            print(f'✅ 成功项目: {", ".join(success_items)}')
                
    except Exception as e:
        print(f"❌ 验证失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_migration() 