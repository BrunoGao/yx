#!/usr/bin/env python3
"""
直接测试Flask应用内的统计函数
"""
import sys
import os
import traceback
from datetime import datetime, date, timedelta

# 添加Flask应用路径
sys.path.append('/Users/bg/work/codes/springboot/ljwx/flt/ljwx-bigscreen/bigscreen')

# 模拟Flask应用环境
from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1:3306/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 导入数据库和模型
from bigScreen.models import db
from sqlalchemy import text

# 初始化数据库
db.init_app(app)

def test_statistics_logic():
    """测试统计逻辑"""
    with app.app_context():
        try:
            orgId = '1939964806110937090'
            today = date.today()
            
            print(f"🔍 测试统计逻辑: orgId={orgId}, today={today}")
            print("=" * 50)
            
            # 第一步：通过组织关系一次性获取所有用户和设备信息
            print("📋 第一步：查询用户设备关系")
            result = db.session.execute(text("""
                SELECT 
                    u.id as user_id,
                    u.device_sn,
                    u.real_name,
                    uo.org_id
                FROM sys_user u
                LEFT JOIN sys_user_org uo ON u.id = uo.user_id  
                WHERE uo.org_id = :orgId
                AND u.is_deleted = 0
                AND uo.is_deleted = 0
                AND u.device_sn IS NOT NULL
                AND u.device_sn != ''
            """), {'orgId': orgId}).fetchall()
            
            print(f"   查询结果: {len(result)} 条记录")
            for row in result:
                print(f"   - {row}")
            
            if not result:
                print("   ❌ 未找到任何用户设备")
                return {'success': False, 'error': 'No user devices found'}
            
            # 提取设备和用户列表
            device_sns = [row[1] for row in result if row[1]]  # device_sn
            user_ids = [row[0] for row in result if row[0]]    # user_id
            
            print(f"\n📱 设备列表: {device_sns}")
            print(f"👥 用户列表: {user_ids}")
            
            # 第二步：使用设备列表进行高效的聚合查询
            device_sns_str = "','".join(device_sns)
            print(f"\n🔧 构造的device_sns_str: '{device_sns_str}'")
            
            # 当天健康数据统计
            print(f"\n📊 测试健康数据统计")
            health_count = 0
            if device_sns:
                sql_query = f"""
                    SELECT COUNT(*) FROM t_user_health_data
                    WHERE device_sn IN ('{device_sns_str}')
                    AND DATE(timestamp) = :today
                """
                print(f"   SQL: {sql_query}")
                result = db.session.execute(text(sql_query), {'today': today}).scalar()
                health_count = result or 0
                print(f"   健康数据条数: {health_count}")
            
            # 当天活跃设备统计
            print(f"\n🔥 测试活跃设备统计")
            active_devices = 0
            if device_sns:
                sql_query = f"""
                    SELECT COUNT(DISTINCT device_sn) FROM t_user_health_data
                    WHERE device_sn IN ('{device_sns_str}')
                    AND DATE(timestamp) = :today
                """
                print(f"   SQL: {sql_query}")
                result = db.session.execute(text(sql_query), {'today': today}).scalar()
                active_devices = result or 0
                print(f"   活跃设备数: {active_devices}")
            
            # 当天在线用户统计
            print(f"\n👤 测试在线用户统计")
            online_users = 0
            if device_sns:
                sql_query = f"""
                    SELECT COUNT(DISTINCT user_id) FROM t_user_health_data
                    WHERE device_sn IN ('{device_sns_str}')
                    AND DATE(timestamp) = :today
                """
                print(f"   SQL: {sql_query}")
                result = db.session.execute(text(sql_query), {'today': today}).scalar()
                online_users = result or 0
                print(f"   在线用户数: {online_users}")
            
            print("\n" + "=" * 50)
            print(f"📈 统计结果:")
            print(f"   健康数据: {health_count}")
            print(f"   活跃设备: {active_devices}")
            print(f"   在线用户: {online_users}")
            print(f"   设备总数: {len(device_sns)}")
            
            return {
                'success': True,
                'data': {
                    'health_count': health_count,
                    'active_devices': active_devices,
                    'online_users': online_users,
                    'device_count': len(device_sns)
                }
            }
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    result = test_statistics_logic()
    print(f"\n🎯 最终结果: {result}")