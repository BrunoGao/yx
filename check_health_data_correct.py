#!/usr/bin/env python3
"""
检查健康基线和评分数据生成结果 - 使用正确配置
验证数据的正确性和完整性
"""
import mysql.connector
from datetime import date, datetime
import pandas as pd

# 使用正确的数据库配置 (从config.py获取)
DB_CONFIG = {
    'host': '127.0.0.1',  # 如果是Docker环境需要调整为 ljwx-mysql
    'user': 'root',
    'password': '123456',  # 根据原始check_health_data.py的配置
    'database': 'test',  # 正确数据库名
    'port': 3306
}

def check_health_data():
    """检查健康基线和评分数据"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        today = date.today()
        print("=" * 80)
        print(f"🔍 健康数据检查报告 - {today}")
        print("=" * 80)
        
        # 1. 检查数据库连接和基本表结构
        print("\n🔗 1. 数据库连接和表结构检查")
        print("-" * 60)
        
        # 检查关键表是否存在
        cursor.execute("SHOW TABLES LIKE 't_%health%'")
        tables = cursor.fetchall()
        print(f"✅ 找到健康相关表: {len(tables)} 个")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 2. 检查健康数据表 (t_user_health_data)
        print("\n📊 2. 健康数据表检查 (t_user_health_data)")
        print("-" * 60)
        
        try:
            cursor.execute("SELECT COUNT(*) FROM t_user_health_data WHERE DATE(create_time) = %s", (today,))
            data_count = cursor.fetchone()[0]
            print(f"✅ 今日健康数据记录总数: {data_count}")
            
            if data_count > 0:
                # 按体征统计数据
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN heart_rate IS NOT NULL THEN 1 END) as heart_rate_count,
                        COUNT(CASE WHEN blood_oxygen IS NOT NULL THEN 1 END) as blood_oxygen_count,
                        COUNT(CASE WHEN temperature IS NOT NULL THEN 1 END) as temperature_count,
                        COUNT(CASE WHEN pressure_high IS NOT NULL THEN 1 END) as pressure_high_count,
                        COUNT(CASE WHEN pressure_low IS NOT NULL THEN 1 END) as pressure_low_count,
                        COUNT(CASE WHEN stress IS NOT NULL THEN 1 END) as stress_count,
                        COUNT(CASE WHEN sleep IS NOT NULL THEN 1 END) as sleep_count
                    FROM t_user_health_data
                    WHERE DATE(create_time) = %s
                """, (today,))
                
                health_stats = cursor.fetchone()
                print(f"  心率数据: {health_stats[0]} 条")
                print(f"  血氧数据: {health_stats[1]} 条")
                print(f"  体温数据: {health_stats[2]} 条")
                print(f"  收缩压数据: {health_stats[3]} 条")
                print(f"  舒张压数据: {health_stats[4]} 条")
                print(f"  压力数据: {health_stats[5]} 条")
                print(f"  睡眠数据: {health_stats[6]} 条")
                
                # 用户分布
                cursor.execute("""
                    SELECT COUNT(DISTINCT device_sn) as unique_devices,
                           COUNT(DISTINCT user_id) as unique_users
                    FROM t_user_health_data
                    WHERE DATE(create_time) = %s
                """, (today,))
                
                user_stats = cursor.fetchone()
                print(f"  📈 涉及设备数: {user_stats[0]}, 涉及用户数: {user_stats[1]}")
            
        except Exception as e:
            print(f"⚠️ 健康数据表检查失败: {e}")
        
        # 3. 检查健康基线表 (t_health_baseline)
        print("\n📈 3. 健康基线数据检查 (t_health_baseline)")
        print("-" * 60)
        
        try:
            cursor.execute("SELECT COUNT(*) FROM t_health_baseline WHERE DATE(baseline_time) = %s", (today,))
            baseline_count = cursor.fetchone()[0]
            print(f"✅ 今日基线记录总数: {baseline_count}")
            
            if baseline_count > 0:
                # 按特征分组统计
                cursor.execute("""
                    SELECT feature_name, COUNT(*) as count, 
                           AVG(mean_value) as avg_mean, 
                           AVG(sample_count) as avg_samples
                    FROM t_health_baseline 
                    WHERE DATE(baseline_time) = %s 
                    GROUP BY feature_name
                    ORDER BY feature_name
                """, (today,))
                
                baseline_features = cursor.fetchall()
                for row in baseline_features:
                    feature, count, avg_mean, avg_samples = row
                    print(f"  {feature:15} | 记录数: {count:3} | 平均值: {avg_mean:8.2f} | 平均样本数: {avg_samples:6.1f}")
            else:
                print("  ⚠️ 今日无基线数据")
                
        except Exception as e:
            print(f"⚠️ 基线表检查失败: {e}")
        
        # 4. 检查最近几天的数据情况
        print("\n📅 4. 最近几天数据情况")
        print("-" * 60)
        
        for days_ago in range(5):
            check_date = date.today() - pd.Timedelta(days=days_ago)
            try:
                cursor.execute("SELECT COUNT(*) FROM t_user_health_data WHERE DATE(create_time) = %s", (check_date,))
                data_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM t_health_baseline WHERE DATE(baseline_time) = %s", (check_date,))
                baseline_count = cursor.fetchone()[0]
                
                print(f"  {check_date}: 健康数据 {data_count:5} 条, 基线数据 {baseline_count:3} 条")
                
            except Exception as e:
                print(f"  {check_date}: 检查失败 - {e}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ 数据检查完成")
        print("=" * 80)
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查数据库配置和连接状态")
        return False
    except Exception as e:
        print(f"❌ 数据检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 使用正确配置检查健康数据...")
    result = check_health_data()
    
    if not result:
        print("\n💡 可能的解决方案:")
        print("1. 检查数据库服务是否正常运行")
        print("2. 检查数据库连接参数是否正确")
        print("3. 检查是否需要在Docker环境中运行")
        print("4. 检查健康数据模拟器是否正在生成数据")