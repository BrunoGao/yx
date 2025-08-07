#!/usr/bin/env python3
"""
测试统计API SQL查询的直接脚本
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

def test_statistics_queries():
    """测试统计查询"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        orgId = '1939964806110937090'
        today = date.today()
        
        print(f"🔍 测试统计查询参数:")
        print(f"   orgId: {orgId}")
        print(f"   today: {today}")
        print()
        
        # 1. 测试健康数据统计
        cursor.execute("""
            SELECT COUNT(*) FROM t_user_health_data
            WHERE org_id = %s
            AND DATE(timestamp) = %s
        """, (orgId, today))
        health_count = cursor.fetchone()[0]
        print(f"📊 健康数据统计: {health_count}")
        
        # 2. 测试活跃设备统计
        cursor.execute("""
            SELECT COUNT(DISTINCT device_sn) FROM t_user_health_data
            WHERE org_id = %s
            AND DATE(timestamp) = %s
        """, (orgId, today))
        active_devices = cursor.fetchone()[0]
        print(f"📱 活跃设备统计: {active_devices}")
        
        # 3. 测试在线用户统计
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM t_user_health_data
            WHERE org_id = %s
            AND DATE(timestamp) = %s
        """, (orgId, today))
        online_users = cursor.fetchone()[0]
        print(f"👥 在线用户统计: {online_users}")
        
        # 4. 测试总设备数
        cursor.execute("""
            SELECT COUNT(*) FROM t_device_info
            WHERE org_id = %s
        """, (orgId,))
        total_devices = cursor.fetchone()[0]
        print(f"🔧 总设备数: {total_devices}")
        
        # 5. 测试告警统计
        cursor.execute("""
            SELECT COUNT(*) FROM t_alert_info
            WHERE org_id = %s
            AND DATE(alert_timestamp) = %s
            AND alert_status != 'resolved'
        """, (orgId, today))
        alert_count = cursor.fetchone()[0]
        print(f"🚨 告警统计: {alert_count}")
        
        # 6. 测试消息统计
        cursor.execute("""
            SELECT COUNT(*) FROM t_device_message
            WHERE org_id = %s
            AND DATE(create_time) = %s
            AND message_status = 'unread'
        """, (orgId, today))
        message_count = cursor.fetchone()[0]
        print(f"📩 消息统计: {message_count}")
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'data': {
                'health_count': health_count,
                'active_devices': active_devices,
                'online_users': online_users,
                'total_devices': total_devices,
                'alert_count': alert_count,
                'message_count': message_count
            }
        }
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 统计API SQL查询测试")
    print("=" * 50)
    
    result = test_statistics_queries()
    
    print()
    print("=" * 50)
    print(f"📊 测试结果: {result}")
    print("=" * 50)