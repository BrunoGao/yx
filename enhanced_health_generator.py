#!/usr/bin/env python3
"""
优化后的健康基线和评分生成脚本
包含改进的标准差计算、数据过滤和异常值检测
"""
import mysql.connector
from datetime import date, datetime
import statistics
import math

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '123456',
    'database': 'test',
    'port': 3306
}

# 特征的合理范围配置
FEATURE_RANGES = {
    'heart_rate': {'min': 30.0, 'max': 200.0, 'min_std': 1.0},
    'blood_oxygen': {'min': 70.0, 'max': 100.0, 'min_std': 0.5},
    'temperature': {'min': 30.0, 'max': 45.0, 'min_std': 0.1},
    'pressure_high': {'min': 60.0, 'max': 250.0, 'min_std': 2.0},
    'pressure_low': {'min': 40.0, 'max': 150.0, 'min_std': 1.5},
    'stress': {'min': 0.0, 'max': 100.0, 'min_std': 1.0},
    'sleep': {'min': 0.0, 'max': 24.0, 'min_std': 0.2}
}

def generate_enhanced_baseline(target_date):
    """优化后的健康基线生成"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"🔧 开始生成优化后的健康基线 - {target_date}")
        
        # 清理旧数据
        cursor.execute("DELETE FROM t_health_baseline WHERE baseline_date = %s", (target_date,))
        print(f"🧹 已清理旧基线数据")
        
        baseline_count = 0
        features = list(FEATURE_RANGES.keys())
        
        for feature in features:
            print(f"📊 处理特征: {feature}")
            
            # 获取过滤后的健康数据
            range_config = FEATURE_RANGES[feature]
            cursor.execute(f"""
                SELECT 
                    user_id, org_id, device_sn, {feature}
                FROM t_user_health_data
                WHERE DATE(timestamp) = %s
                AND user_id IS NOT NULL
                AND {feature} IS NOT NULL
                AND {feature} BETWEEN %s AND %s
            """, (target_date, range_config['min'], range_config['max']))
            
            health_data = cursor.fetchall()
            
            if not health_data:
                print(f"  ⚠️ 特征 {feature} 无有效数据")
                continue
            
            # 按用户分组计算基线
            user_data = {}
            for row in health_data:
                user_id, org_id, device_sn, value = row
                key = (user_id, org_id, device_sn)
                if key not in user_data:
                    user_data[key] = []
                user_data[key].append(float(value))
            
            # 生成每个用户的基线
            for (user_id, org_id, device_sn), values in user_data.items():
                if len(values) >= 10:  # 提高最小样本数要求
                    mean_value = statistics.mean(values)
                    std_value = max(statistics.stdev(values) if len(values) > 1 else 0, 
                                  range_config['min_std'])  # 应用最小标准差
                    min_value = min(values)
                    max_value = max(values)
                    sample_count = len(values)
                    
                    try:
                        cursor.execute("""
                            INSERT INTO t_health_baseline 
                            (user_id, org_id, device_sn, feature_name, mean_value, std_value, 
                             min_value, max_value, sample_count, baseline_date, baseline_time, 
                             is_current, create_time, update_time)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW(), NOW())
                        """, (user_id, org_id, device_sn, feature, mean_value, std_value,
                             min_value, max_value, sample_count, target_date, target_date))
                        baseline_count += 1
                    except Exception as e:
                        print(f"  ⚠️ 插入基线失败 {device_sn}-{feature}: {e}")
            
            print(f"  ✅ 特征 {feature} 基线生成完成")
        
        # 生成组织级别基线
        org_baseline_count = 0
        for feature in features:
            cursor.execute("""
                SELECT org_id, mean_value, sample_count
                FROM t_health_baseline
                WHERE baseline_date = %s AND feature_name = %s
            """, (target_date, feature))
            
            org_data = cursor.fetchall()
            
            if len(org_data) >= 2:  # 至少2个用户
                org_groups = {}
                for row in org_data:
                    org_id, mean_value, sample_count = row
                    if org_id not in org_groups:
                        org_groups[org_id] = []
                    org_groups[org_id].append((float(mean_value), sample_count))
                
                for org_id, data in org_groups.items():
                    if len(data) >= 2:
                        means = [item[0] for item in data]
                        total_samples = sum(item[1] for item in data)
                        
                        org_mean = statistics.mean(means)
                        org_std = statistics.stdev(means) if len(means) > 1 else 0
                        org_min = min(means)
                        org_max = max(means)
                        user_count = len(means)
                        
                        try:
                            cursor.execute("""
                                INSERT INTO t_org_health_baseline
                                (org_id, feature_name, baseline_date, mean_value, std_value,
                                 min_value, max_value, user_count, sample_count, create_time, update_time)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                                ON DUPLICATE KEY UPDATE
                                mean_value = VALUES(mean_value),
                                std_value = VALUES(std_value),
                                min_value = VALUES(min_value),
                                max_value = VALUES(max_value),
                                user_count = VALUES(user_count),
                                sample_count = VALUES(sample_count)
                            """, (org_id, feature, target_date, org_mean, org_std,
                                 org_min, org_max, user_count, total_samples))
                            org_baseline_count += 1
                        except Exception as e:
                            print(f"  ⚠️ 插入组织基线失败 {org_id}-{feature}: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 优化后基线生成完成:")
        print(f"   用户基线: {baseline_count} 条")
        print(f"   组织基线: {org_baseline_count} 条")
        
        return {
            'success': True,
            'user_baselines': baseline_count,
            'org_baselines': org_baseline_count,
            'date': str(target_date)
        }
        
    except Exception as e:
        print(f"❌ 优化基线生成失败: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def generate_enhanced_scores(target_date):
    """优化后的健康评分生成"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"🎯 开始生成优化后的健康评分 - {target_date}")
        
        # 清理旧评分数据
        cursor.execute("DELETE FROM t_health_score WHERE score_date = %s", (target_date,))
        print(f"🧹 已清理旧评分数据")
        
        # 获取基线数据
        cursor.execute("""
            SELECT device_sn, feature_name, mean_value, std_value, min_value, max_value
            FROM t_health_baseline
            WHERE baseline_date = %s
        """, (target_date,))
        
        baseline_data = cursor.fetchall()
        baselines = {}
        for row in baseline_data:
            device_sn, feature_name, mean_value, std_value, min_value, max_value = row
            if device_sn not in baselines:
                baselines[device_sn] = {}
            baselines[device_sn][feature_name] = {
                'mean': float(mean_value),
                'std': float(std_value),
                'min': float(min_value),
                'max': float(max_value)
            }
        
        if not baselines:
            print("❌ 无基线数据，跳过评分生成")
            return {'success': False, 'message': '无基线数据'}
        
        print(f"📈 加载了 {len(baselines)} 个用户的基线数据")
        
        score_count = 0
        features = list(FEATURE_RANGES.keys())
        
        for feature in features:
            print(f"🎯 处理特征评分: {feature}")
            
            # 获取当天的健康数据
            range_config = FEATURE_RANGES[feature]
            cursor.execute(f"""
                SELECT 
                    user_id, org_id, device_sn, {feature}
                FROM t_user_health_data
                WHERE DATE(timestamp) = %s
                AND user_id IS NOT NULL
                AND {feature} IS NOT NULL
                AND {feature} BETWEEN %s AND %s
            """, (target_date, range_config['min'], range_config['max']))
            
            health_data = cursor.fetchall()
            
            if not health_data:
                print(f"  ⚠️ 特征 {feature} 无有效数据")
                continue
            
            # 按用户分组计算评分
            user_data = {}
            for row in health_data:
                user_id, org_id, device_sn, value = row
                key = (user_id, org_id, device_sn)
                if key not in user_data:
                    user_data[key] = []
                user_data[key].append(float(value))
            
            # 为每个用户生成评分
            for (user_id, org_id, device_sn), values in user_data.items():
                if len(values) >= 3 and device_sn in baselines and feature in baselines[device_sn]:
                    baseline = baselines[device_sn][feature]
                    avg_value = statistics.mean(values)
                    
                    # 计算Z分数，限制在[-10, 10]范围内
                    if baseline['std'] > 0:
                        z_score = (avg_value - baseline['mean']) / baseline['std']
                        z_score = max(-10, min(10, z_score))  # 限制Z分数范围
                    else:
                        z_score = 0
                    
                    # 基于Z分数计算评分
                    score_value = max(0, min(100, 100 - abs(z_score) * 10))
                    
                    # 计算惩罚值
                    max_val = max(values)
                    min_val = min(values)
                    penalty_value = 0
                    
                    if max_val > baseline['max'] * 1.2:
                        penalty_value = min(20, (max_val - baseline['max'] * 1.2) / baseline['max'] * 100)
                    elif min_val < baseline['min'] * 0.8:
                        penalty_value = min(20, (baseline['min'] * 0.8 - min_val) / baseline['min'] * 100)
                    
                    try:
                        cursor.execute("""
                            INSERT INTO t_health_score
                            (user_id, org_id, device_sn, feature_name, avg_value, z_score, 
                             score_value, penalty_value, score_date, baseline_time, 
                             create_time, update_time)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        """, (user_id, org_id, device_sn, feature, avg_value, z_score,
                             score_value, penalty_value, target_date, target_date))
                        score_count += 1
                    except Exception as e:
                        print(f"  ⚠️ 插入评分失败 {device_sn}-{feature}: {e}")
            
            print(f"  ✅ 特征 {feature} 评分生成完成")
        
        # 生成组织级别评分
        org_score_count = 0
        for feature in features:
            cursor.execute("""
                SELECT org_id, score_value, penalty_value
                FROM t_health_score
                WHERE score_date = %s AND feature_name = %s
            """, (target_date, feature))
            
            score_data = cursor.fetchall()
            
            if score_data:
                org_groups = {}
                for row in score_data:
                    org_id, score_value, penalty_value = row
                    if org_id not in org_groups:
                        org_groups[org_id] = []
                    final_score = float(score_value) - float(penalty_value)
                    org_groups[org_id].append(final_score)
                
                for org_id, scores in org_groups.items():
                    if len(scores) >= 2:
                        mean_score = statistics.mean(scores)
                        std_score = statistics.stdev(scores) if len(scores) > 1 else 0
                        min_score = min(scores)
                        max_score = max(scores)
                        user_count = len(scores)
                        
                        try:
                            cursor.execute("""
                                INSERT INTO t_org_health_score
                                (org_id, feature_name, score_date, mean_score, std_score,
                                 min_score, max_score, user_count, create_time, update_time)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                                ON DUPLICATE KEY UPDATE
                                mean_score = VALUES(mean_score),
                                std_score = VALUES(std_score),
                                min_score = VALUES(min_score),
                                max_score = VALUES(max_score),
                                user_count = VALUES(user_count)
                            """, (org_id, feature, target_date, mean_score, std_score,
                                 min_score, max_score, user_count))
                            org_score_count += 1
                        except Exception as e:
                            print(f"  ⚠️ 插入组织评分失败 {org_id}-{feature}: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 优化后评分生成完成:")
        print(f"   用户评分: {score_count} 条")
        print(f"   组织评分: {org_score_count} 条")
        
        return {
            'success': True,
            'user_scores': score_count,
            'org_scores': org_score_count,
            'date': str(target_date)
        }
        
    except Exception as e:
        print(f"❌ 优化评分生成失败: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def detect_anomalies(target_date):
    """异常值检测"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"🔍 开始异常值检测 - {target_date}")
        
        # 检测基线异常
        cursor.execute("""
            SELECT device_sn, feature_name, mean_value, std_value, sample_count
            FROM t_health_baseline 
            WHERE baseline_date = %s
            AND (std_value <= 0 OR sample_count < 10)
        """, (target_date,))
        
        baseline_anomalies = cursor.fetchall()
        if baseline_anomalies:
            print(f"⚠️ 发现 {len(baseline_anomalies)} 条基线异常:")
            for row in baseline_anomalies:
                device_sn, feature, mean_val, std_val, samples = row
                print(f"  {device_sn} | {feature} | 标准差: {std_val} | 样本数: {samples}")
        
        # 检测评分异常
        cursor.execute("""
            SELECT device_sn, feature_name, score_value, z_score, penalty_value
            FROM t_health_score 
            WHERE score_date = %s
            AND (ABS(z_score) > 5 OR score_value < 0 OR score_value > 100)
        """, (target_date,))
        
        score_anomalies = cursor.fetchall()
        if score_anomalies:
            print(f"⚠️ 发现 {len(score_anomalies)} 条评分异常:")
            for row in score_anomalies:
                device_sn, feature, score, z_score, penalty = row
                print(f"  {device_sn} | {feature} | 评分: {score} | Z分数: {z_score}")
        
        cursor.close()
        conn.close()
        
        if not baseline_anomalies and not score_anomalies:
            print("✅ 未发现异常数据")
        
        return {
            'baseline_anomalies': len(baseline_anomalies),
            'score_anomalies': len(score_anomalies)
        }
        
    except Exception as e:
        print(f"❌ 异常值检测失败: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    today = date.today()
    
    print("=" * 80)
    print("🚀 优化后的健康基线和评分生成工具")
    print("=" * 80)
    
    # 生成优化后的基线
    baseline_result = generate_enhanced_baseline(today)
    print()
    
    # 生成优化后的评分
    if baseline_result.get('success'):
        score_result = generate_enhanced_scores(today)
        print()
        
        # 异常值检测
        anomaly_result = detect_anomalies(today)
        
        print("\n" + "=" * 80)
        print("📊 优化结果汇总:")
        print(f"基线生成: {baseline_result}")
        print(f"评分生成: {score_result}")
        print(f"异常检测: {anomaly_result}")
        print("=" * 80)
    else:
        print(f"\n❌ 基线生成失败: {baseline_result}")