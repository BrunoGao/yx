from flask import jsonify, request, current_app
from ...models import db, UserHealthData
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class HealthDataCleanService:
    """健康数据清理服务"""
    
    def __init__(self):
        self.db = db
    
    def clean_old_health_data(self, days=30):
        """清理旧健康数据"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = UserHealthData.query.filter(
                UserHealthData.created_at < cutoff_date
            ).delete()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'成功清理{days}天前的健康数据，删除{deleted_count}条记录'
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"清理健康数据失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'清理失败: {str(e)}'
            }), 500
    
    def fetch_user_locations(self, device_sn=None, date_str=None):
        """获取用户位置信息"""
        try:
            query = UserHealthData.query
            if device_sn:
                query = query.filter_by(deviceSn=device_sn)
            if date_str:
                query = query.filter(func.date(UserHealthData.created_at) == date_str)
            
            locations = query.filter(
                UserHealthData.latitude.isnot(None),
                UserHealthData.longitude.isnot(None)
            ).order_by(UserHealthData.created_at.desc()).limit(100).all()
            
            location_list = []
            for location in locations:
                location_list.append({
                    'id': location.id,
                    'deviceSn': location.deviceSn,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'created_at': location.created_at.isoformat() if location.created_at else None
                })
            
            return jsonify({
                'success': True,
                'data': location_list
            })
        except Exception as e:
            logger.error(f"获取用户位置信息失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取用户位置信息失败: {str(e)}'
            }), 500 