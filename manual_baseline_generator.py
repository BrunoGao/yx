#!/usr/bin/env python3
"""
手动健康基线生成脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from datetime import date, timedelta
import mysql.connector

# Flask应用配置
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1:3306/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '123456', 
    'database': 'test',
    'port': 3306
}

def generate_health_baseline_manual(target_date):
    """手动生成健康基线"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"🔧 开始生成 {target_date} 的健康基线...")
        
        # 1. 查询当天的健康数据，按用户分组计算基线
        cursor.execute("""
            SELECT 
                user_id,
                org_id,
                device_sn,
                AVG(heart_rate) as avg_heart_rate,
                AVG(blood_oxygen) as avg_blood_oxygen, 
                AVG(temperature) as avg_temperature,
                AVG(pressure_high) as avg_pressure_high,
                AVG(pressure_low) as avg_pressure_low,
                AVG(stress) as avg_stress,
                AVG(sleep) as avg_sleep,
                COUNT(*) as data_points
            FROM t_user_health_data
            WHERE DATE(timestamp) = %s
            AND user_id IS NOT NULL
            GROUP BY user_id, org_id, device_sn
            HAVING COUNT(*) >= 3
        """, (target_date,))
        
        health_data = cursor.fetchall()
        
        if not health_data:
            print(f"❌ {target_date} 没有足够的健康数据生成基线")
            cursor.close()
            conn.close()
            return {'success': False, 'message': '没有足够数据'}
        
        print(f"📊 找到 {len(health_data)} 个用户的健康数据")
        
        # 2. 为每个用户生成基线记录
        baseline_count = 0
        features = ['heart_rate', 'blood_oxygen', 'temperature', 'pressure_high', 'pressure_low', 'stress', 'sleep']
        
        for row in health_data:
            user_id, org_id, device_sn = row[0], row[1], row[2]
            feature_values = row[3:10]  # 7个特征的平均值
            data_points = row[10]
            
            for i, feature in enumerate(features):
                if feature_values[i] is not None and feature_values[i] > 0:
                    try:
                        cursor.execute("""
                            INSERT INTO t_health_baseline 
                            (user_id, org_id, device_sn, feature_name, mean_value, baseline_date, baseline_time, sample_count)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            mean_value = VALUES(mean_value),
                            sample_count = VALUES(sample_count)
                        """, (user_id, org_id, device_sn, feature, feature_values[i], target_date, 
                             datetime.now(), data_points))
                        baseline_count += 1
                    except Exception as e:
                        print(f"⚠️ 插入基线失败 {user_id}-{feature}: {e}")
        
        # 3. 生成组织级别基线
        org_baseline_count = 0
        cursor.execute("""
            SELECT 
                org_id,
                AVG(heart_rate) as avg_heart_rate,
                AVG(blood_oxygen) as avg_blood_oxygen,
                AVG(temperature) as avg_temperature, 
                AVG(pressure_high) as avg_pressure_high,
                AVG(pressure_low) as avg_pressure_low,
                AVG(stress) as avg_stress,
                AVG(sleep) as avg_sleep,
                COUNT(DISTINCT user_id) as user_count,
                COUNT(*) as total_data_points
            FROM t_user_health_data
            WHERE DATE(timestamp) = %s
            AND org_id IS NOT NULL
            GROUP BY org_id
            HAVING COUNT(DISTINCT user_id) >= 2
        """, (target_date,))
        
        org_data = cursor.fetchall()
        
        for row in org_data:
            org_id = row[0]
            org_feature_values = row[1:8]
            user_count = row[8]
            total_data_points = row[9]
            
            for i, feature in enumerate(features):
                if org_feature_values[i] is not None and org_feature_values[i] > 0:
                    try:
                        cursor.execute("""
                            INSERT INTO t_org_health_baseline
                            (org_id, feature_name, mean_value, baseline_date, user_count, sample_count)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            mean_value = VALUES(mean_value),
                            user_count = VALUES(user_count),
                            sample_count = VALUES(sample_count)
                        """, (org_id, feature, org_feature_values[i], target_date, user_count, total_data_points))
                        org_baseline_count += 1
                    except Exception as e:
                        print(f"⚠️ 插入组织基线失败 {org_id}-{feature}: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 基线生成完成:")
        print(f"   用户基线: {baseline_count} 条")
        print(f"   组织基线: {org_baseline_count} 条")
        
        return {
            'success': True,
            'user_baselines': baseline_count,
            'org_baselines': org_baseline_count,
            'date': str(target_date)
        }
        
    except Exception as e:
        print(f"❌ 基线生成失败: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    from datetime import datetime
    
    # 生成昨天和今天的基线
    yesterday = date.today() - timedelta(days=1)
    today = date.today()
    
    print("=" * 50)
    print("🔧 手动健康基线生成工具")
    print("=" * 50)
    
    # 生成昨天的基线
    result_yesterday = generate_health_baseline_manual(yesterday)
    print()
    
    # 生成今天的基线（如果有数据）
    result_today = generate_health_baseline_manual(today)
    
    print("\n" + "=" * 50)
    print("📊 生成结果汇总:")
    print(f"昨天 ({yesterday}): {result_yesterday}")
    print(f"今天 ({today}): {result_today}")
    print("=" * 50)