#!/usr/bin/env python3
"""
测试统计API - 独立Flask应用验证修复
"""
from flask import Flask, jsonify, request
import mysql.connector
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text

app = Flask(__name__)

# 数据库配置
DATABASE_URL = 'mysql+pymysql://root:123456@127.0.0.1:3306/test'
engine = create_engine(DATABASE_URL)

@app.route('/test_statistics')
def test_statistics():
    """测试统计接口"""
    try:
        orgId = request.args.get('orgId', '1939964806110937090')
        today = date.today()
        
        with engine.connect() as conn:
            # 健康数据统计
            result = conn.execute(text("""
                SELECT COUNT(*) FROM t_user_health_data
                WHERE org_id = :orgId
                AND DATE(timestamp) = :today
            """), {'orgId': orgId, 'today': today})
            health_count = result.scalar() or 0
            
            # 活跃设备统计
            result = conn.execute(text("""
                SELECT COUNT(DISTINCT device_sn) FROM t_user_health_data
                WHERE org_id = :orgId
                AND DATE(timestamp) = :today
            """), {'orgId': orgId, 'today': today})
            active_devices = result.scalar() or 0
            
            # 在线用户统计
            result = conn.execute(text("""
                SELECT COUNT(DISTINCT user_id) FROM t_user_health_data
                WHERE org_id = :orgId
                AND DATE(timestamp) = :today
            """), {'orgId': orgId, 'today': today})
            online_users = result.scalar() or 0
            
            # 设备总数
            result = conn.execute(text("""
                SELECT COUNT(*) FROM t_device_info
                WHERE org_id = :orgId
            """), {'orgId': orgId})
            total_devices = result.scalar() or 0
            
            # 告警统计
            result = conn.execute(text("""
                SELECT COUNT(*) FROM t_alert_info
                WHERE org_id = :orgId
                AND DATE(alert_timestamp) = :today
                AND alert_status != 'resolved'
            """), {'orgId': orgId, 'today': today})
            alert_count = result.scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'orgId': orgId,
                'date': today.strftime('%Y-%m-%d'),
                'health_count': health_count,
                'active_devices': active_devices,
                'online_users': online_users,
                'device_count': total_devices,
                'alert_count': alert_count,
                'message': 'Test API working correctly!'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)