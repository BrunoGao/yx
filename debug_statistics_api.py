#!/usr/bin/env python3
"""
调试统计API的专用脚本
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

def debug_statistics_query():
    """调试统计查询"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        orgId = '1939964806110937090'
        today = date.today()
        
        print(f"🔍 调试统计查询: orgId={orgId}, today={today}")
        print("=" * 60)
        
        # 第一步：测试用户设备查询
        print("📋 第一步：查询组织用户设备关系")
        cursor.execute("""
            SELECT 
                u.id as user_id,
                u.device_sn,
                u.real_name,
                uo.org_id
            FROM sys_user u
            LEFT JOIN sys_user_org uo ON u.id = uo.user_id  
            WHERE uo.org_id = %s
            AND u.is_deleted = 0
            AND uo.is_deleted = 0
            AND u.device_sn IS NOT NULL
            AND u.device_sn != ''
        """, (orgId,))
        
        user_devices = cursor.fetchall()
        print(f"   找到 {len(user_devices)} 个用户设备:")
        for user_id, device_sn, real_name, org_id in user_devices:
            print(f"   - 用户ID: {user_id}, 设备: {device_sn}, 姓名: {real_name}")
        
        if not user_devices:
            print("   ❌ 未找到任何用户设备，查询结束")
            return
        
        # 提取设备列表
        device_sns = [row[1] for row in user_devices if row[1]]
        user_ids = [row[0] for row in user_devices if row[0]]
        
        print(f"\n📱 提取到的设备列表: {device_sns}")
        print(f"👥 提取到的用户列表: {user_ids}")
        
        # 第二步：测试健康数据统计
        print(f"\n📊 第二步：统计今天的健康数据")
        device_sns_str = "','".join(device_sns)
        query = f"""
            SELECT COUNT(*) FROM t_user_health_data
            WHERE device_sn IN ('{device_sns_str}')
            AND DATE(timestamp) = %s
        """
        print(f"   SQL: {query}")
        cursor.execute(query, (today,))
        health_count = cursor.fetchone()[0]
        print(f"   健康数据条数: {health_count}")
        
        # 第三步：测试活跃设备统计
        print(f"\n🔥 第三步：统计今天的活跃设备")
        query = f"""
            SELECT COUNT(DISTINCT device_sn) FROM t_user_health_data
            WHERE device_sn IN ('{device_sns_str}')
            AND DATE(timestamp) = %s
        """
        cursor.execute(query, (today,))
        active_devices = cursor.fetchone()[0]
        print(f"   活跃设备数: {active_devices}")
        
        # 第四步：测试在线用户统计
        print(f"\n👤 第四步：统计今天的在线用户")
        query = f"""
            SELECT COUNT(DISTINCT user_id) FROM t_user_health_data
            WHERE device_sn IN ('{device_sns_str}')
            AND DATE(timestamp) = %s
        """
        cursor.execute(query, (today,))
        online_users = cursor.fetchone()[0]
        print(f"   在线用户数: {online_users}")
        
        # 第五步：测试告警统计  
        print(f"\n🚨 第五步：统计今天的告警")
        query = f"""
            SELECT COUNT(*) FROM t_alert_info
            WHERE device_sn IN ('{device_sns_str}')
            AND DATE(alert_timestamp) = %s
            AND alert_status != 'resolved'
        """
        cursor.execute(query, (today,))
        alert_count = cursor.fetchone()[0]
        print(f"   告警数: {alert_count}")
        
        # 第六步：测试消息统计
        print(f"\n📧 第六步：统计今天的消息")
        query = f"""
            SELECT COUNT(*) FROM t_device_message
            WHERE device_sn IN ('{device_sns_str}')
            AND DATE(create_time) = %s
            AND message_status = 'unread'
        """
        cursor.execute(query, (today,))
        message_count = cursor.fetchone()[0]
        print(f"   消息数: {message_count}")
        
        print("\n" + "=" * 60)
        print("📈 最终统计结果:")
        print(f"   健康数据: {health_count}")
        print(f"   活跃设备: {active_devices}")  
        print(f"   在线用户: {online_users}")
        print(f"   告警数量: {alert_count}")
        print(f"   消息数量: {message_count}")
        print(f"   设备总数: {len(device_sns)}")
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'data': {
                'health_count': health_count,
                'active_devices': active_devices,
                'online_users': online_users,
                'alert_count': alert_count,
                'message_count': message_count,
                'device_count': len(device_sns)
            }
        }
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    print("🔧 统计API调试工具")
    print("=" * 60)
    result = debug_statistics_query()
    print("\n" + "=" * 60)
    print(f"🎯 调试结果: {result}")