from flask import jsonify, request, current_app
from ...models import db, UserHealthData
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class HealthDataAnalysisService:
    """健康数据分析服务"""
    
    def __init__(self):
        self.db = db
    
    def generate_health_json(self):
        """生成健康数据JSON"""
        try:
            # 获取最近7天的健康数据统计
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            health_stats = db.session.query(
                func.date(UserHealthData.created_at).label('date'),
                func.avg(UserHealthData.heartRate).label('avg_heart_rate'),
                func.avg(UserHealthData.systolicPressure).label('avg_systolic'),
                func.avg(UserHealthData.diastolicPressure).label('avg_diastolic'),
                func.avg(UserHealthData.bloodOxygen).label('avg_blood_oxygen'),
                func.avg(UserHealthData.bodyTemperature).label('avg_temperature'),
                func.count(UserHealthData.id).label('count')
            ).filter(
                UserHealthData.created_at >= start_date,
                UserHealthData.created_at <= end_date
            ).group_by(
                func.date(UserHealthData.created_at)
            ).all()
            
            data = []
            for stat in health_stats:
                data.append({
                    'date': stat.date.strftime('%Y-%m-%d'),
                    'avg_heart_rate': float(stat.avg_heart_rate) if stat.avg_heart_rate else 0,
                    'avg_systolic': float(stat.avg_systolic) if stat.avg_systolic else 0,
                    'avg_diastolic': float(stat.avg_diastolic) if stat.avg_diastolic else 0,
                    'avg_blood_oxygen': float(stat.avg_blood_oxygen) if stat.avg_blood_oxygen else 0,
                    'avg_temperature': float(stat.avg_temperature) if stat.avg_temperature else 0,
                    'count': stat.count
                })
            
            return jsonify({
                'success': True,
                'data': data
            })
        except Exception as e:
            logger.error(f"生成健康数据JSON失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'生成健康数据JSON失败: {str(e)}'
            }), 500
    
    def get_health_stats(self):
        """获取健康统计"""
        try:
            # 获取健康数据统计
            total_health_data = UserHealthData.query.count()
            
            # 获取最近24小时的数据
            yesterday = datetime.now() - timedelta(days=1)
            recent_health_data = UserHealthData.query.filter(
                UserHealthData.created_at >= yesterday
            ).count()
            
            return jsonify({
                'success': True,
                'data': {
                    'total_health_data': total_health_data,
                    'recent_health_data': recent_health_data
                }
            })
        except Exception as e:
            logger.error(f"获取健康统计失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取健康统计失败: {str(e)}'
            }), 500
    
    def fetch_health_metrics(self):
        """获取健康指标"""
        try:
            # 获取健康指标统计
            total_health_records = UserHealthData.query.count()
            
            # 获取最近24小时的数据
            yesterday = datetime.now() - timedelta(days=1)
            recent_health_records = UserHealthData.query.filter(
                UserHealthData.created_at >= yesterday
            ).count()
            
            return jsonify({
                'success': True,
                'data': {
                    'total_health_records': total_health_records,
                    'recent_health_records': recent_health_records
                }
            })
        except Exception as e:
            logger.error(f"获取健康指标失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取健康指标失败: {str(e)}'
            }), 500
    
    def fetch_health_data_config(self, customer_id=None, device_sn=None):
        """获取健康数据配置"""
        try:
            # 默认配置
            default_config = {
                'heartRate': {
                    'enabled': True,
                    'interval': 300,  # 5分钟
                    'threshold': {'min': 60, 'max': 100}
                },
                'bloodPressure': {
                    'enabled': True,
                    'interval': 600,  # 10分钟
                    'threshold': {'systolic': {'min': 90, 'max': 140}, 'diastolic': {'min': 60, 'max': 90}}
                },
                'bloodOxygen': {
                    'enabled': True,
                    'interval': 300,  # 5分钟
                    'threshold': {'min': 95, 'max': 100}
                },
                'bodyTemperature': {
                    'enabled': True,
                    'interval': 1800,  # 30分钟
                    'threshold': {'min': 36, 'max': 37.5}
                },
                'location': {
                    'enabled': True,
                    'interval': 600  # 10分钟
                }
            }
            
            return jsonify({
                'success': True,
                'data': default_config
            })
            
        except Exception as e:
            logger.error(f"获取健康数据配置失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取配置失败: {str(e)}'
            }), 500 