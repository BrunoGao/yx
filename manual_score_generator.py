#!/usr/bin/env python3
"""
健康评分生成脚本
基于健康基线数据计算Z分数和健康评分
"""
import mysql.connector
from datetime import datetime, date, timedelta
import math

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '123456',
    'database': 'test',
    'port': 3306
}

def generate_health_scores(target_date):
    """生成健康评分"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"🔧 开始生成 {target_date} 的健康评分...")
        
        # 1. 获取当天的健康数据用于评分计算
        cursor.execute("""
            SELECT 
                user_id, org_id, device_sn,
                heart_rate, blood_oxygen, temperature, 
                pressure_high, pressure_low, stress, sleep
            FROM t_user_health_data
            WHERE DATE(timestamp) = %s
            AND user_id IS NOT NULL
        """, (target_date,))
        
        health_data = cursor.fetchall()
        
        if not health_data:
            print(f"❌ {target_date} 没有健康数据用于评分")
            return {'success': False, 'message': '没有健康数据'}
        
        print(f"📊 找到 {len(health_data)} 条健康数据用于评分")
        
        # 2. 获取基线数据用于Z分数计算
        cursor.execute("""
            SELECT user_id, feature_name, mean_value, std_value
            FROM t_health_baseline
            WHERE baseline_date = %s
        """, (target_date,))
        
        baseline_data = cursor.fetchall()
        
        # 构建基线字典
        baselines = {}
        for row in baseline_data:
            user_id, feature_name, mean_value, std_value = row
            if user_id not in baselines:
                baselines[user_id] = {}
            baselines[user_id][feature_name] = {
                'mean': float(mean_value) if mean_value else 0,
                'std': float(std_value) if std_value else 1
            }
        
        print(f"📈 加载了 {len(baselines)} 个用户的基线数据")
        
        # 3. 正常值范围定义
        normal_ranges = {
            'heart_rate': {'min': 60, 'max': 100, 'weight': 0.20},
            'blood_oxygen': {'min': 95, 'max': 100, 'weight': 0.20},
            'temperature': {'min': 36.0, 'max': 37.5, 'weight': 0.15},
            'pressure_high': {'min': 90, 'max': 140, 'weight': 0.15},
            'pressure_low': {'min': 60, 'max': 90, 'weight': 0.10},
            'stress': {'min': 20, 'max': 60, 'weight': 0.10},
            'sleep': {'min': 6, 'max': 9, 'weight': 0.10}
        }
        
        # 4. 计算每条健康数据的评分
        score_count = 0
        feature_names = ['heart_rate', 'blood_oxygen', 'temperature', 'pressure_high', 'pressure_low', 'stress', 'sleep']
        
        for row in health_data:
            user_id, org_id, device_sn = row[0], row[1], row[2]
            values = row[3:10]  # 7个特征值
            
            # 为每个特征计算评分
            for i, feature in enumerate(feature_names):
                if values[i] is not None and values[i] > 0:
                    current_value = float(values[i])
                    
                    # 计算基于正常范围的基础评分
                    normal_range = normal_ranges[feature]
                    if normal_range['min'] <= current_value <= normal_range['max']:
                        base_score = 100  # 正常范围内满分
                        penalty = 0
                    else:
                        # 超出范围的惩罚
                        if current_value < normal_range['min']:
                            deviation = abs(current_value - normal_range['min']) / normal_range['min']
                        else:
                            deviation = abs(current_value - normal_range['max']) / normal_range['max']
                        
                        base_score = max(20, 100 - deviation * 100)  # 最低分20
                        penalty = min(80, deviation * 100)
                    
                    # 计算Z分数（如果有基线数据）
                    z_score = 0
                    if user_id in baselines and feature in baselines[user_id]:
                        baseline = baselines[user_id][feature]
                        if baseline['std'] > 0:
                            z_score = (current_value - baseline['mean']) / baseline['std']
                    
                    try:
                        cursor.execute("""
                            INSERT INTO t_health_score
                            (user_id, org_id, device_sn, feature_name, avg_value, z_score, score_value, penalty_value, score_date, baseline_time)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            avg_value = VALUES(avg_value),
                            z_score = VALUES(z_score),
                            score_value = VALUES(score_value),
                            penalty_value = VALUES(penalty_value)
                        """, (user_id, org_id, device_sn, feature, current_value, z_score, base_score, penalty, target_date, target_date))
                        score_count += 1
                    except Exception as e:
                        print(f"⚠️ 插入评分失败 {user_id}-{feature}: {e}")
        
        # 5. 生成组织级别评分
        org_score_count = 0
        cursor.execute("""
            SELECT org_id, feature_name,
                   AVG(score_value) as mean_score,
                   STD(score_value) as std_score,
                   MIN(score_value) as min_score,
                   MAX(score_value) as max_score,
                   COUNT(DISTINCT user_id) as user_count
            FROM t_health_score
            WHERE score_date = %s
            GROUP BY org_id, feature_name
        """, (target_date,))
        
        org_scores = cursor.fetchall()
        
        for row in org_scores:
            org_id, feature_name, mean_score, std_score, min_score, max_score, user_count = row
            try:
                cursor.execute("""
                    INSERT INTO t_org_health_score
                    (org_id, feature_name, score_date, mean_score, std_score, min_score, max_score, user_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    mean_score = VALUES(mean_score),
                    std_score = VALUES(std_score),
                    min_score = VALUES(min_score),
                    max_score = VALUES(max_score),
                    user_count = VALUES(user_count)
                """, (org_id, feature_name, target_date, mean_score or 0, std_score or 0, min_score or 0, max_score or 0, user_count))
                org_score_count += 1
            except Exception as e:
                print(f"⚠️ 插入组织评分失败 {org_id}-{feature_name}: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 健康评分生成完成:")
        print(f"   用户评分: {score_count} 条")
        print(f"   组织评分: {org_score_count} 条")
        
        return {
            'success': True,
            'user_scores': score_count,
            'org_scores': org_score_count,
            'date': str(target_date)
        }
        
    except Exception as e:
        print(f"❌ 评分生成失败: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":    
    today = date.today()
    
    print("=" * 50)
    print("🔧 健康评分生成工具")
    print("=" * 50)
    
    # 生成今天的评分
    result = generate_health_scores(today)
    
    print("\n" + "=" * 50)
    print(f"📊 评分生成结果: {result}")
    print("=" * 50)