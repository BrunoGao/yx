#!/usr/bin/env python3
"""
测试SQL查询 - 独立验证数据库查询
"""
import mysql.connector
from datetime import datetime, date

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root', 
    'password': '123456',
    'database': 'test',
    'port': 3306
}

def test_queries():
    """测试统计查询"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        orgId = '1939964806110937090'
        today = date.today()
        
        print(f"🔍 测试组织ID: {orgId}")
        print(f"📅 查询日期: {today}")
        print("=" * 50)
        
        # 测试1：健康数据统计
        cursor.execute("""
            SELECT COUNT(*) FROM t_user_health_data
            WHERE org_id = %s
            AND DATE(timestamp) = %s
        """, (orgId, today))
        health_count = cursor.fetchone()[0]
        print(f"✅ 健康数据条数: {health_count}")
        
        # 测试2：活跃设备统计
        cursor.execute("""
            SELECT COUNT(DISTINCT device_sn) FROM t_user_health_data
            WHERE org_id = %s
            AND DATE(timestamp) = %s
        """, (orgId, today))
        active_devices = cursor.fetchone()[0]
        print(f"✅ 活跃设备数: {active_devices}")
        
        # 测试3：在线用户统计
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM t_user_health_data
            WHERE org_id = %s
            AND DATE(timestamp) = %s
        """, (orgId, today))
        online_users = cursor.fetchone()[0]
        print(f"✅ 在线用户数: {online_users}")
        
        # 测试4：设备总数
        cursor.execute("""
            SELECT COUNT(*) FROM t_device_info
            WHERE org_id = %s
        """, (orgId,))
        total_devices = cursor.fetchone()[0]
        print(f"✅ 设备总数: {total_devices}")
        
        # 测试5：告警统计
        cursor.execute("""
            SELECT COUNT(*) FROM t_alert_info
            WHERE org_id = %s
            AND DATE(alert_timestamp) = %s
            AND alert_status != 'resolved'
        """, (orgId, today))
        alert_count = cursor.fetchone()[0]
        print(f"✅ 待处理告警: {alert_count}")
        
        print("=" * 50)
        print("📊 汇总统计:")
        print(f"   健康数据: {health_count}")
        print(f"   活跃设备: {active_devices}")
        print(f"   在线用户: {online_users}")
        print(f"   设备总数: {total_devices}")
        print(f"   待处理告警: {alert_count}")
        
        cursor.close()
        conn.close()
        
        return {
            'health_count': health_count,
            'active_devices': active_devices,
            'online_users': online_users,
            'device_count': total_devices,
            'alert_count': alert_count
        }
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return None

if __name__ == "__main__":
    test_queries()