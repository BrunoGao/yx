#!/usr/bin/env python3
"""
深度验证健康基线和评分数据的计算正确性
通过重新计算来验证生成的数据是否准确
"""
import mysql.connector
from datetime import date
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

def validate_calculations():
    """验证基线和评分计算的正确性"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        today = date.today()
        print("=" * 80)
        print(f"🧮 健康数据计算验证报告 - {today}")
        print("=" * 80)
        
        # 1. 验证基线计算
        print("\n🔍 1. 验证健康基线计算")
        print("-" * 60)
        
        # 选择一个用户和特征进行详细验证
        cursor.execute("""
            SELECT device_sn, feature_name, mean_value, sample_count
            FROM t_health_baseline 
            WHERE baseline_date = %s
            ORDER BY device_sn, feature_name
            LIMIT 1
        """, (today,))
        
        baseline_sample = cursor.fetchone()
        if baseline_sample:
            device_sn, feature_name, stored_mean, stored_count = baseline_sample
            print(f"验证用户: {device_sn}, 特征: {feature_name}")
            
            # 重新计算该用户该特征的基线
            cursor.execute(f"""
                SELECT {feature_name}
                FROM t_user_health_data
                WHERE device_sn = %s 
                AND DATE(timestamp) = %s 
                AND {feature_name} IS NOT NULL 
                AND {feature_name} > 0
            """, (device_sn, today))
            
            raw_values = [row[0] for row in cursor.fetchall()]
            
            if raw_values:
                calculated_mean = statistics.mean(raw_values)
                calculated_count = len(raw_values)
                
                # 转换数据类型以避免Decimal和float运算错误
                stored_mean_float = float(stored_mean)
                
                print(f"  存储的均值: {stored_mean_float:.4f}")
                print(f"  计算的均值: {calculated_mean:.4f}")
                print(f"  均值差异: {abs(stored_mean_float - calculated_mean):.6f}")
                print(f"  存储样本数: {stored_count}")
                print(f"  实际样本数: {calculated_count}")
                
                # 验证误差范围
                mean_error = abs(stored_mean_float - calculated_mean)
                count_match = stored_count == calculated_count
                
                if mean_error < 0.01 and count_match:
                    print("  ✅ 基线计算正确")
                else:
                    print("  ❌ 基线计算有误差")
                    if mean_error >= 0.01:
                        print(f"    均值误差过大: {mean_error:.6f}")
                    if not count_match:
                        print(f"    样本数不匹配")
        
        # 2. 验证评分计算
        print("\n🎯 2. 验证健康评分计算")
        print("-" * 60)
        
        # 选择同一用户的评分进行验证
        cursor.execute("""
            SELECT s.device_sn, s.feature_name, s.avg_value, s.z_score, 
                   s.score_value, s.penalty_value, b.mean_value, b.std_value
            FROM t_health_score s
            JOIN t_health_baseline b ON s.device_sn = b.device_sn 
                AND s.feature_name = b.feature_name 
                AND s.score_date = b.baseline_date
            WHERE s.score_date = %s
            ORDER BY s.device_sn, s.feature_name
            LIMIT 1
        """, (today,))
        
        score_sample = cursor.fetchone()
        if score_sample:
            device_sn, feature_name, avg_value, stored_z, stored_score, stored_penalty, baseline_mean, baseline_std = score_sample
            print(f"验证用户: {device_sn}, 特征: {feature_name}")
            
            # 重新计算Z分数
            if baseline_std and baseline_std > 0:
                calculated_z = (float(avg_value) - float(baseline_mean)) / float(baseline_std)
            else:
                calculated_z = 0
            
            print(f"  平均值: {float(avg_value):.4f}")
            print(f"  基线均值: {float(baseline_mean):.4f}")
            print(f"  基线标准差: {float(baseline_std):.4f}")
            print(f"  存储Z分数: {float(stored_z):.4f}")
            print(f"  计算Z分数: {calculated_z:.4f}")
            print(f"  Z分数差异: {abs(float(stored_z) - calculated_z):.6f}")
            
            # 重新计算评分 (基于正常范围)
            normal_ranges = {
                'heart_rate': {'min': 60, 'max': 100},
                'blood_oxygen': {'min': 95, 'max': 100},
                'temperature': {'min': 36.0, 'max': 37.5},
                'pressure_high': {'min': 90, 'max': 140},
                'pressure_low': {'min': 60, 'max': 90},
                'stress': {'min': 20, 'max': 60},
                'sleep': {'min': 6, 'max': 9}
            }
            
            if feature_name in normal_ranges:
                range_info = normal_ranges[feature_name]
                current_value = float(avg_value)
                
                if range_info['min'] <= current_value <= range_info['max']:
                    calculated_score = 100
                    calculated_penalty = 0
                else:
                    if current_value < range_info['min']:
                        deviation = abs(current_value - range_info['min']) / range_info['min']
                    else:
                        deviation = abs(current_value - range_info['max']) / range_info['max']
                    
                    calculated_score = max(20, 100 - deviation * 100)
                    calculated_penalty = min(80, deviation * 100)
                
                print(f"  正常范围: {range_info['min']}-{range_info['max']}")
                print(f"  存储评分: {float(stored_score):.2f}")
                print(f"  计算评分: {calculated_score:.2f}")
                print(f"  评分差异: {abs(float(stored_score) - calculated_score):.4f}")
                print(f"  存储惩罚: {float(stored_penalty):.2f}")
                print(f"  计算惩罚: {calculated_penalty:.2f}")
                
                # 验证误差范围
                z_error = abs(float(stored_z) - calculated_z)
                score_error = abs(float(stored_score) - calculated_score)
                penalty_error = abs(float(stored_penalty) - calculated_penalty)
                
                if z_error < 0.01 and score_error < 0.1 and penalty_error < 0.1:
                    print("  ✅ 评分计算正确")
                else:
                    print("  ❌ 评分计算有误差")
                    if z_error >= 0.01:
                        print(f"    Z分数误差: {z_error:.6f}")
                    if score_error >= 0.1:
                        print(f"    评分误差: {score_error:.4f}")
                    if penalty_error >= 0.1:
                        print(f"    惩罚误差: {penalty_error:.4f}")
        
        # 3. 验证组织级别聚合计算
        print("\n🏢 3. 验证组织级别聚合计算")
        print("-" * 60)
        
        # 选择一个组织和特征进行验证
        cursor.execute("""
            SELECT org_id, feature_name, mean_value, user_count, sample_count
            FROM t_org_health_baseline 
            WHERE baseline_date = %s
            ORDER BY org_id, feature_name
            LIMIT 1
        """, (today,))
        
        org_baseline_sample = cursor.fetchone()
        if org_baseline_sample:
            org_id, feature_name, stored_org_mean, stored_user_count, stored_sample_count = org_baseline_sample
            print(f"验证组织: {org_id}, 特征: {feature_name}")
            
            # 重新计算组织基线
            cursor.execute("""
                SELECT mean_value, sample_count
                FROM t_health_baseline 
                WHERE org_id = %s 
                AND feature_name = %s 
                AND baseline_date = %s
            """, (org_id, feature_name, today))
            
            user_baselines = cursor.fetchall()
            
            if user_baselines:
                user_means = [float(row[0]) for row in user_baselines]
                total_samples = sum(row[1] for row in user_baselines)
                calculated_org_mean = statistics.mean(user_means)
                calculated_user_count = len(user_means)
                
                print(f"  存储组织均值: {float(stored_org_mean):.4f}")
                print(f"  计算组织均值: {calculated_org_mean:.4f}")
                print(f"  均值差异: {abs(float(stored_org_mean) - calculated_org_mean):.6f}")
                print(f"  存储用户数: {stored_user_count}")
                print(f"  实际用户数: {calculated_user_count}")
                print(f"  存储样本总数: {stored_sample_count}")
                print(f"  计算样本总数: {total_samples}")
                
                # 验证误差
                org_mean_error = abs(float(stored_org_mean) - calculated_org_mean)
                user_count_match = stored_user_count == calculated_user_count
                sample_count_match = stored_sample_count == total_samples
                
                if org_mean_error < 0.01 and user_count_match and sample_count_match:
                    print("  ✅ 组织基线计算正确")
                else:
                    print("  ❌ 组织基线计算有误差")
        
        # 4. 数据分布统计
        print("\n📊 4. 数据分布统计")
        print("-" * 60)
        
        # 各特征的基线分布
        features = ['heart_rate', 'blood_oxygen', 'temperature', 'pressure_high', 'pressure_low', 'stress', 'sleep']
        
        for feature in features:
            cursor.execute("""
                SELECT AVG(mean_value) as avg_mean, 
                       MIN(mean_value) as min_mean, 
                       MAX(mean_value) as max_mean,
                       AVG(sample_count) as avg_samples
                FROM t_health_baseline 
                WHERE feature_name = %s AND baseline_date = %s
            """, (feature, today))
            
            stats = cursor.fetchone()
            if stats and stats[0] is not None:
                avg_mean, min_mean, max_mean, avg_samples = stats
                print(f"  {feature:15} | 均值: {float(avg_mean):7.2f} | 范围: {float(min_mean):7.2f}-{float(max_mean):7.2f} | 样本: {float(avg_samples):6.1f}")
        
        # 5. 异常值检测
        print("\n⚠️  5. 异常值检测")
        print("-" * 60)
        
        # 检查基线异常值
        cursor.execute("""
            SELECT device_sn, feature_name, mean_value
            FROM t_health_baseline 
            WHERE baseline_date = %s
            AND (mean_value < 0 OR mean_value > 1000)
        """, (today,))
        
        abnormal_baselines = cursor.fetchall()
        if abnormal_baselines:
            print("  发现异常基线值:")
            for device_sn, feature, value in abnormal_baselines:
                print(f"    {device_sn} | {feature} | {value}")
        else:
            print("  ✅ 未发现基线异常值")
        
        # 检查评分异常值
        cursor.execute("""
            SELECT device_sn, feature_name, score_value, z_score
            FROM t_health_score 
            WHERE score_date = %s
            AND (score_value < 0 OR score_value > 100 OR ABS(z_score) > 10)
        """, (today,))
        
        abnormal_scores = cursor.fetchall()
        if abnormal_scores:
            print("  发现异常评分值:")
            for device_sn, feature, score, z_score in abnormal_scores:
                print(f"    {device_sn} | {feature} | 评分: {score} | Z分数: {z_score}")
        else:
            print("  ✅ 未发现评分异常值")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ 计算验证完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    validate_calculations()