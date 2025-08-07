from flask import jsonify, request, current_app
from ...models import db, UserInfo, DeviceInfo, UserHealthData, AlertInfo, DeviceMessage
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class OrgService:
    """组织服务，实现组织相关业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def get_total_info(self, customer_id=None):
        """获取总览信息"""
        try:
            # 获取各种统计数据
            total_users = UserInfo.query.count()
            total_devices = DeviceInfo.query.count()
            total_health_records = UserHealthData.query.count()
            total_alerts = AlertInfo.query.count()
            total_messages = DeviceMessage.query.count()
            
            # 获取最近24小时的数据
            yesterday = datetime.now() - timedelta(days=1)
            recent_health_records = UserHealthData.query.filter(
                UserHealthData.created_at >= yesterday
            ).count()
            
            recent_alerts = AlertInfo.query.filter(
                AlertInfo.created_at >= yesterday
            ).count()
            
            recent_messages = DeviceMessage.query.filter(
                DeviceMessage.sent_time >= yesterday
            ).count()
            
            data = {
                'overview': {
                    'total_users': total_users,
                    'total_devices': total_devices,
                    'total_health_records': total_health_records,
                    'total_alerts': total_alerts,
                    'total_messages': total_messages
                },
                'recent': {
                    'recent_health_records': recent_health_records,
                    'recent_alerts': recent_alerts,
                    'recent_messages': recent_messages
                }
            }
            
            return jsonify({
                'success': True,
                'data': data
            })
        except Exception as e:
            logger.error(f"获取总览信息失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取总览信息失败: {str(e)}'
            }), 500
    
    def get_health_stats(self):
        """获取健康统计"""
        try:
            # 获取健康数据统计
            total_health_data = UserHealthData.query.count()
            total_alerts = AlertInfo.query.count()
            total_messages = DeviceMessage.query.count()
            total_devices = DeviceInfo.query.count()
            
            # 获取最近24小时的数据
            yesterday = datetime.now() - timedelta(days=1)
            recent_health_data = UserHealthData.query.filter(
                UserHealthData.created_at >= yesterday
            ).count()
            
            recent_alerts = AlertInfo.query.filter(
                AlertInfo.created_at >= yesterday
            ).count()
            
            return jsonify({
                'success': True,
                'data': {
                    'total_health_data': total_health_data,
                    'total_alerts': total_alerts,
                    'total_messages': total_messages,
                    'total_devices': total_devices,
                    'recent_health_data': recent_health_data,
                    'recent_alerts': recent_alerts
                }
            })
        except Exception as e:
            logger.error(f"获取健康统计失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取健康统计失败: {str(e)}'
            }), 500 