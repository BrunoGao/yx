from flask import current_app
from ..models import db, UserHealthData
from sqlalchemy import and_, func
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class HealthService:
    """健康数据服务层，处理健康数据相关的业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def get_health_data(self, deviceSn, date=None):
        """获取健康数据"""
        try:
            query = UserHealthData.query.filter_by(deviceSn=deviceSn)
            
            if date:
                query = query.filter(func.date(UserHealthData.created_at) == date)
            
            health_data = query.order_by(UserHealthData.created_at.desc()).all()
            
            return {
                'success': True,
                'data': [data.to_dict() for data in health_data]
            }
        except Exception as e:
            logger.error(f"获取健康数据失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_health_data_by_id(self, id):
        """根据ID获取健康数据"""
        try:
            health_data = UserHealthData.query.get(id)
            if health_data:
                return {
                    'success': True,
                    'data': health_data.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': '健康数据不存在'
                }
        except Exception as e:
            logger.error(f"根据ID获取健康数据失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_user_locations(self, deviceSn, date_str=None):
        """获取用户位置信息"""
        try:
            query = UserHealthData.query.filter_by(deviceSn=deviceSn)
            
            if date_str:
                query = query.filter(func.date(UserHealthData.created_at) == date_str)
            
            # 获取有位置信息的数据
            location_data = query.filter(
                and_(
                    UserHealthData.latitude.isnot(None),
                    UserHealthData.longitude.isnot(None)
                )
            ).order_by(UserHealthData.created_at.desc()).all()
            
            locations = []
            for data in location_data:
                if data.latitude and data.longitude:
                    locations.append({
                        'latitude': float(data.latitude),
                        'longitude': float(data.longitude),
                        'timestamp': data.created_at.isoformat() if data.created_at else None
                    })
            
            return {
                'success': True,
                'data': locations
            }
        except Exception as e:
            logger.error(f"获取用户位置信息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_health_data_score(self, deviceSn):
        """获取健康评分"""
        try:
            # 获取最新的健康数据
            latest_health = UserHealthData.query.filter_by(
                deviceSn=deviceSn
            ).order_by(UserHealthData.created_at.desc()).first()
            
            if not latest_health:
                return {
                    'success': False,
                    'message': '没有健康数据'
                }
            
            # 简单的健康评分算法
            score = 0
            total_metrics = 0
            
            # 心率评分 (正常范围60-100)
            if latest_health.heartRate:
                total_metrics += 1
                if 60 <= latest_health.heartRate <= 100:
                    score += 100
                elif 50 <= latest_health.heartRate <= 110:
                    score += 80
                elif 40 <= latest_health.heartRate <= 120:
                    score += 60
                else:
                    score += 40
            
            # 血压评分 (收缩压正常范围90-140)
            if latest_health.systolicPressure:
                total_metrics += 1
                if 90 <= latest_health.systolicPressure <= 140:
                    score += 100
                elif 80 <= latest_health.systolicPressure <= 150:
                    score += 80
                elif 70 <= latest_health.systolicPressure <= 160:
                    score += 60
                else:
                    score += 40
            
            # 血氧评分 (正常范围95-100)
            if latest_health.bloodOxygen:
                total_metrics += 1
                if 95 <= latest_health.bloodOxygen <= 100:
                    score += 100
                elif 90 <= latest_health.bloodOxygen <= 94:
                    score += 80
                elif 85 <= latest_health.bloodOxygen <= 89:
                    score += 60
                else:
                    score += 40
            
            # 体温评分 (正常范围36-37.5)
            if latest_health.bodyTemperature:
                total_metrics += 1
                if 36 <= latest_health.bodyTemperature <= 37.5:
                    score += 100
                elif 35.5 <= latest_health.bodyTemperature <= 38:
                    score += 80
                elif 35 <= latest_health.bodyTemperature <= 38.5:
                    score += 60
                else:
                    score += 40
            
            final_score = round(score / total_metrics, 1) if total_metrics > 0 else 0
            
            return {
                'success': True,
                'data': {
                    'score': final_score,
                    'health_data': latest_health.to_dict()
                }
            }
        except Exception as e:
            logger.error(f"获取健康评分失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_health_data_trends(self, deviceSn):
        """获取健康趋势"""
        try:
            # 获取最近7天的健康数据
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            health_data = UserHealthData.query.filter(
                and_(
                    UserHealthData.deviceSn == deviceSn,
                    UserHealthData.created_at >= start_date,
                    UserHealthData.created_at <= end_date
                )
            ).order_by(UserHealthData.created_at.asc()).all()
            
            # 按日期分组数据
            trends = {}
            for data in health_data:
                date_str = data.created_at.date().isoformat()
                if date_str not in trends:
                    trends[date_str] = {
                        'heartRate': [],
                        'systolicPressure': [],
                        'diastolicPressure': [],
                        'bloodOxygen': [],
                        'bodyTemperature': []
                    }
                
                if data.heartRate:
                    trends[date_str]['heartRate'].append(data.heartRate)
                if data.systolicPressure:
                    trends[date_str]['systolicPressure'].append(data.systolicPressure)
                if data.diastolicPressure:
                    trends[date_str]['diastolicPressure'].append(data.diastolicPressure)
                if data.bloodOxygen:
                    trends[date_str]['bloodOxygen'].append(data.bloodOxygen)
                if data.bodyTemperature:
                    trends[date_str]['bodyTemperature'].append(data.bodyTemperature)
            
            # 计算每日平均值
            trend_data = []
            for date_str, metrics in trends.items():
                daily_avg = {
                    'date': date_str,
                    'heartRate': round(sum(metrics['heartRate']) / len(metrics['heartRate']), 1) if metrics['heartRate'] else None,
                    'systolicPressure': round(sum(metrics['systolicPressure']) / len(metrics['systolicPressure']), 1) if metrics['systolicPressure'] else None,
                    'diastolicPressure': round(sum(metrics['diastolicPressure']) / len(metrics['diastolicPressure']), 1) if metrics['diastolicPressure'] else None,
                    'bloodOxygen': round(sum(metrics['bloodOxygen']) / len(metrics['bloodOxygen']), 1) if metrics['bloodOxygen'] else None,
                    'bodyTemperature': round(sum(metrics['bodyTemperature']) / len(metrics['bodyTemperature']), 1) if metrics['bodyTemperature'] else None
                }
                trend_data.append(daily_avg)
            
            return {
                'success': True,
                'data': trend_data
            }
        except Exception as e:
            logger.error(f"获取健康趋势失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_health_data_chart_baseline(self, deviceSn):
        """获取健康基线图表"""
        try:
            # 获取最近30天的健康数据
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            health_data = UserHealthData.query.filter(
                and_(
                    UserHealthData.deviceSn == deviceSn,
                    UserHealthData.created_at >= start_date,
                    UserHealthData.created_at <= end_date
                )
            ).order_by(UserHealthData.created_at.asc()).all()
            
            # 计算基线数据
            baseline = {
                'heartRate': {
                    'avg': 0,
                    'min': 0,
                    'max': 0,
                    'count': 0
                },
                'systolicPressure': {
                    'avg': 0,
                    'min': 0,
                    'max': 0,
                    'count': 0
                },
                'diastolicPressure': {
                    'avg': 0,
                    'min': 0,
                    'max': 0,
                    'count': 0
                },
                'bloodOxygen': {
                    'avg': 0,
                    'min': 0,
                    'max': 0,
                    'count': 0
                },
                'bodyTemperature': {
                    'avg': 0,
                    'min': 0,
                    'max': 0,
                    'count': 0
                }
            }
            
            # 收集数据
            for data in health_data:
                if data.heartRate:
                    baseline['heartRate']['count'] += 1
                    baseline['heartRate']['avg'] += data.heartRate
                    if baseline['heartRate']['min'] == 0 or data.heartRate < baseline['heartRate']['min']:
                        baseline['heartRate']['min'] = data.heartRate
                    if data.heartRate > baseline['heartRate']['max']:
                        baseline['heartRate']['max'] = data.heartRate
                
                if data.systolicPressure:
                    baseline['systolicPressure']['count'] += 1
                    baseline['systolicPressure']['avg'] += data.systolicPressure
                    if baseline['systolicPressure']['min'] == 0 or data.systolicPressure < baseline['systolicPressure']['min']:
                        baseline['systolicPressure']['min'] = data.systolicPressure
                    if data.systolicPressure > baseline['systolicPressure']['max']:
                        baseline['systolicPressure']['max'] = data.systolicPressure
                
                if data.diastolicPressure:
                    baseline['diastolicPressure']['count'] += 1
                    baseline['diastolicPressure']['avg'] += data.diastolicPressure
                    if baseline['diastolicPressure']['min'] == 0 or data.diastolicPressure < baseline['diastolicPressure']['min']:
                        baseline['diastolicPressure']['min'] = data.diastolicPressure
                    if data.diastolicPressure > baseline['diastolicPressure']['max']:
                        baseline['diastolicPressure']['max'] = data.diastolicPressure
                
                if data.bloodOxygen:
                    baseline['bloodOxygen']['count'] += 1
                    baseline['bloodOxygen']['avg'] += data.bloodOxygen
                    if baseline['bloodOxygen']['min'] == 0 or data.bloodOxygen < baseline['bloodOxygen']['min']:
                        baseline['bloodOxygen']['min'] = data.bloodOxygen
                    if data.bloodOxygen > baseline['bloodOxygen']['max']:
                        baseline['bloodOxygen']['max'] = data.bloodOxygen
                
                if data.bodyTemperature:
                    baseline['bodyTemperature']['count'] += 1
                    baseline['bodyTemperature']['avg'] += data.bodyTemperature
                    if baseline['bodyTemperature']['min'] == 0 or data.bodyTemperature < baseline['bodyTemperature']['min']:
                        baseline['bodyTemperature']['min'] = data.bodyTemperature
                    if data.bodyTemperature > baseline['bodyTemperature']['max']:
                        baseline['bodyTemperature']['max'] = data.bodyTemperature
            
            # 计算平均值
            for metric in baseline.values():
                if metric['count'] > 0:
                    metric['avg'] = round(metric['avg'] / metric['count'], 1)
            
            return {
                'success': True,
                'data': baseline
            }
        except Exception as e:
            logger.error(f"获取健康基线图表失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_health_data_page(self, deviceSn, page=1, per_page=10):
        """获取健康数据分页"""
        try:
            pagination = UserHealthData.query.filter_by(
                deviceSn=deviceSn
            ).order_by(UserHealthData.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'success': True,
                'data': {
                    'items': [data.to_dict() for data in pagination.items],
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page,
                    'per_page': per_page
                }
            }
        except Exception as e:
            logger.error(f"获取健康数据分页失败: {e}")
            return {'success': False, 'message': str(e)} 