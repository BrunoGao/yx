#!/usr/bin/env python3
"""
检查健康基线和评分数据生成结果
验证数据的正确性和完整性
"""
import mysql.connector
from datetime import date, datetime
import pandas as pd

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '123456',
    'database': 'test',
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
        
        # 1. 检查健康基线表数据
        print("\n📊 1. 健康基线数据检查 (t_health_baseline)")
        print("-" * 60)
        
        # 基线数据总数
        cursor.execute("SELECT COUNT(*) FROM t_health_baseline WHERE baseline_date = %s", (today,))
        baseline_count = cursor.fetchone()[0]
        print(f"✅ 今日基线记录总数: {baseline_count}")
        
        # 按特征分组统计
        cursor.execute("""
            SELECT feature_name, COUNT(*) as count, 
                   AVG(mean_value) as avg_mean, 
                   AVG(sample_count) as avg_samples
            FROM t_health_baseline 
            WHERE baseline_date = %s 
            GROUP BY feature_name
            ORDER BY feature_name
        """, (today,))
        
        baseline_features = cursor.fetchall()
        for row in baseline_features:
            feature, count, avg_mean, avg_samples = row
            print(f"  {feature:15} | 记录数: {count:3} | 平均值: {avg_mean:8.2f} | 平均样本数: {avg_samples:6.1f}")
        
        # 用户分布统计
        cursor.execute("""
            SELECT COUNT(DISTINCT device_sn) as unique_users,
                   COUNT(DISTINCT org_id) as unique_orgs
            FROM t_health_baseline 
            WHERE baseline_date = %s
        """, (today,))
        
        user_stats = cursor.fetchone()
        print(f"  📈 涉及用户数: {user_stats[0]}, 涉及组织数: {user_stats[1]}")
        
        # 2. 检查健康评分表数据
        print("\n🎯 2. 健康评分数据检查 (t_health_score)")
        print("-" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM t_health_score WHERE score_date = %s", (today,))
        score_count = cursor.fetchone()[0]
        print(f"✅ 今日评分记录总数: {score_count}")
        
        # 按特征分组统计评分
        cursor.execute("""
            SELECT feature_name, COUNT(*) as count,
                   AVG(score_value) as avg_score,
                   AVG(z_score) as avg_z_score,
                   AVG(penalty_value) as avg_penalty
            FROM t_health_score 
            WHERE score_date = %s 
            GROUP BY feature_name
            ORDER BY feature_name
        """, (today,))
        
        score_features = cursor.fetchall()
        for row in score_features:
            feature, count, avg_score, avg_z, avg_penalty = row
            print(f"  {feature:15} | 记录数: {count:5} | 平均分: {avg_score:6.2f} | Z分数: {avg_z:6.3f} | 惩罚: {avg_penalty:5.2f}")
        
        # 评分分布统计
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN score_value >= 90 THEN '优秀(>=90)'
                    WHEN score_value >= 80 THEN '良好(80-89)'
                    WHEN score_value >= 70 THEN '一般(70-79)'
                    WHEN score_value >= 60 THEN '较差(60-69)'
                    ELSE '很差(<60)'
                END as score_range,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM t_health_score WHERE score_date = %s), 2) as percentage
            FROM t_health_score 
            WHERE score_date = %s
            GROUP BY 
                CASE 
                    WHEN score_value >= 90 THEN '优秀(>=90)'
                    WHEN score_value >= 80 THEN '良好(80-89)'
                    WHEN score_value >= 70 THEN '一般(70-79)'
                    WHEN score_value >= 60 THEN '较差(60-69)'
                    ELSE '很差(<60)'
                END
            ORDER BY score_range DESC
        """, (today, today))
        
        score_distribution = cursor.fetchall()
        print(f"\n  📊 评分分布:")
        for range_name, count, percentage in score_distribution:
            print(f"    {range_name:12} | {count:6} 条 ({percentage:5.1f}%)")
        
        # 3. 检查组织级别基线数据
        print("\n🏢 3. 组织健康基线数据检查 (t_org_health_baseline)")
        print("-" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM t_org_health_baseline WHERE baseline_date = %s", (today,))
        org_baseline_count = cursor.fetchone()[0]
        print(f"✅ 今日组织基线记录总数: {org_baseline_count}")
        
        if org_baseline_count > 0:
            cursor.execute("""
                SELECT org_id, feature_name, mean_value, user_count, sample_count
                FROM t_org_health_baseline 
                WHERE baseline_date = %s
                ORDER BY org_id, feature_name
            """, (today,))
            
            org_baselines = cursor.fetchall()
            for row in org_baselines:
                org_id, feature, mean_val, user_count, sample_count = row
                print(f"  组织{org_id} | {feature:15} | 均值: {mean_val:8.2f} | 用户数: {user_count:3} | 样本数: {sample_count:5}")
        
        # 4. 检查组织级别评分数据
        print("\n🏢 4. 组织健康评分数据检查 (t_org_health_score)")
        print("-" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM t_org_health_score WHERE score_date = %s", (today,))
        org_score_count = cursor.fetchone()[0]
        print(f"✅ 今日组织评分记录总数: {org_score_count}")
        
        if org_score_count > 0:
            cursor.execute("""
                SELECT org_id, feature_name, mean_score, user_count
                FROM t_org_health_score 
                WHERE score_date = %s
                ORDER BY org_id, feature_name
            """, (today,))
            
            org_scores = cursor.fetchall()
            for row in org_scores:
                org_id, feature, mean_score, user_count = row
                print(f"  组织{org_id} | {feature:15} | 平均分: {mean_score:6.2f} | 用户数: {user_count:3}")
        
        # 5. 数据完整性验证
        print("\n🔍 5. 数据完整性验证")
        print("-" * 60)
        
        # 检查基线和评分数据的一致性
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT b.device_sn) as baseline_users,
                COUNT(DISTINCT s.device_sn) as score_users
            FROM t_health_baseline b
            LEFT JOIN t_health_score s ON b.device_sn = s.device_sn 
                AND b.feature_name = s.feature_name 
                AND b.baseline_date = s.score_date
            WHERE b.baseline_date = %s
        """, (today,))
        
        consistency = cursor.fetchone()
        print(f"  📊 基线用户数: {consistency[0]}, 评分用户数: {consistency[1]}")
        
        # 检查是否有异常数据
        cursor.execute("""
            SELECT COUNT(*) as negative_scores
            FROM t_health_score 
            WHERE score_date = %s AND score_value < 0
        """, (today,))
        
        negative_scores = cursor.fetchone()[0]
        if negative_scores > 0:
            print(f"  ⚠️  发现 {negative_scores} 条负评分数据")
        else:
            print(f"  ✅ 未发现负评分数据")
        
        # 检查空值数据
        cursor.execute("""
            SELECT COUNT(*) as null_means
            FROM t_health_baseline 
            WHERE baseline_date = %s AND mean_value IS NULL
        """, (today,))
        
        null_means = cursor.fetchone()[0]
        if null_means > 0:
            print(f"  ⚠️  发现 {null_means} 条基线均值为空的数据")
        else:
            print(f"  ✅ 基线数据完整，无空值")
        
        # 6. 生成数据样本
        print("\n📋 6. 数据样本展示")
        print("-" * 60)
        
        print("  健康基线样本 (前5条):")
        cursor.execute("""
            SELECT device_sn, feature_name, mean_value, sample_count, baseline_time
            FROM t_health_baseline 
            WHERE baseline_date = %s
            ORDER BY create_time DESC
            LIMIT 5
        """, (today,))
        
        baseline_samples = cursor.fetchall()
        for row in baseline_samples:
            device_sn, feature, mean_val, samples, baseline_time = row
            print(f"    {device_sn} | {feature:12} | 均值: {mean_val:8.2f} | 样本: {samples:3} | 时间: {baseline_time}")
        
        print("\n  健康评分样本 (前5条):")
        cursor.execute("""
            SELECT device_sn, feature_name, score_value, z_score, penalty_value
            FROM t_health_score 
            WHERE score_date = %s
            ORDER BY create_time DESC
            LIMIT 5
        """, (today,))
        
        score_samples = cursor.fetchall()
        for row in score_samples:
            device_sn, feature, score, z_score, penalty = row
            print(f"    {device_sn} | {feature:12} | 评分: {score:6.2f} | Z分数: {z_score:6.3f} | 惩罚: {penalty:5.2f}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ 数据检查完成")
        print("=" * 80)
        
        return {
            'baseline_count': baseline_count,
            'score_count': score_count,
            'org_baseline_count': org_baseline_count,
            'org_score_count': org_score_count,
            'baseline_users': consistency[0],
            'score_users': consistency[1]
        }
        
    except Exception as e:
        print(f"❌ 数据检查失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = check_health_data()
    
    if result:
        print(f"\n📈 总结:")
        print(f"  基线记录: {result['baseline_count']} 条")
        print(f"  评分记录: {result['score_count']} 条") 
        print(f"  组织基线: {result['org_baseline_count']} 条")
        print(f"  组织评分: {result['org_score_count']} 条")
        print(f"  基线用户: {result['baseline_users']} 个")
        print(f"  评分用户: {result['score_users']} 个")