from flask import current_app
from ..models import db, UserInfo, DeviceInfo, UserHealthData, AlertInfo, DeviceMessage
from sqlalchemy import func, and_
import logging
from datetime import datetime, timedelta, timezone
import json

logger = logging.getLogger(__name__)

class BigscreenService:
    """大屏服务层，处理大屏相关的业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def get_personal_info(self, deviceSn):
        """获取个人大屏信息"""
        try:
            # 获取用户信息
            user_info = UserInfo.query.filter_by(deviceSn=deviceSn).first()
            if not user_info:
                return {'success': False, 'message': '用户不存在'}
            
            # 获取设备信息
            device_info = DeviceInfo.query.filter_by(deviceSn=deviceSn).first()
            
            # 获取最新健康数据
            latest_health = UserHealthData.query.filter_by(
                deviceSn=deviceSn
            ).order_by(UserHealthData.created_at.desc()).first()
            
            # 获取今日告警数量
            today = datetime.now().date()
            alert_count = AlertInfo.query.filter(
                and_(
                    AlertInfo.deviceSn == deviceSn,
                    func.date(AlertInfo.created_at) == today
                )
            ).count()
            
            return {
                'success': True,
                'data': {
                    'user_info': user_info.to_dict() if user_info else None,
                    'device_info': device_info.to_dict() if device_info else None,
                    'latest_health': latest_health.to_dict() if latest_health else None,
                    'alert_count': alert_count
                }
            }
        except Exception as e:
            logger.error(f"获取个人大屏信息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_total_info(self, customer_id):
        """获取总体统计信息 - 实时统计只查询当天数据"""
        try:
            # 获取当天日期（使用本地时区东八区）
            local_tz = timezone(timedelta(hours=8))  # 东八区
            today = datetime.now(local_tz).date()
            
            # 当天健康数据上传数（修复：添加customerId过滤）
            health_count = UserHealthData.query.filter(
                and_(
                    UserHealthData.customerId == customer_id,
                    func.date(UserHealthData.created_at) == today
                )
            ).count()
            
            # 当天待处理告警数（修复：确保时区处理正确）
            alert_count = AlertInfo.query.filter(
                and_(
                    AlertInfo.customerId == customer_id,
                    AlertInfo.status != 'resolved',  # 只统计未解决的告警
                    func.date(AlertInfo.created_at) == today
                )
            ).count()
            
            # 当天活跃设备数（有数据上传的设备）
            active_device_count = db.session.query(UserHealthData.deviceSn).filter(
                and_(
                    UserHealthData.customerId == customer_id,
                    func.date(UserHealthData.created_at) == today
                )
            ).distinct().count()
            
            # 当天未读消息数
            unread_message_count = DeviceMessage.query.filter(
                and_(
                    DeviceMessage.customerId == customer_id,
                    DeviceMessage.message_status == 'unread',
                    func.date(DeviceMessage.created_at) == today
                )
            ).count()
            
            return {
                'success': True,
                'data': {
                    'health_count': health_count,           # 健康数据条数
                    'alert_count': alert_count,             # 待处理告警数
                    'active_device_count': active_device_count,  # 活跃设备数
                    'unread_message_count': unread_message_count  # 未读消息数
                }
            }
        except Exception as e:
            logger.error(f"获取总体统计信息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_health_stats(self):
        """获取健康数据统计"""
        try:
            # 获取最近7天的健康数据统计
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            stats = []
            for i in range(7):
                date = start_date + timedelta(days=i)
                count = UserHealthData.query.filter(
                    func.date(UserHealthData.created_at) == date
                ).count()
                stats.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'count': count
                })
            
            return {
                'success': True,
                'data': stats
            }
        except Exception as e:
            logger.error(f"获取健康数据统计失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_device_analysis(self, customer_id, time_range='7d'):
        """获取设备分析数据"""
        try:
            # 根据时间范围计算开始时间
            end_time = datetime.now()
            if time_range == '7d':
                start_time = end_time - timedelta(days=7)
            elif time_range == '30d':
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=7)
            
            # 获取设备列表
            devices = DeviceInfo.query.filter_by(customerId=customer_id).all()
            
            # 生成分析数据
            analysis_data = []
            for device in devices:
                # 获取设备健康数据数量
                health_count = UserHealthData.query.filter(
                    and_(
                        UserHealthData.deviceSn == device.deviceSn,
                        UserHealthData.created_at >= start_time,
                        UserHealthData.created_at <= end_time
                    )
                ).count()
                
                # 获取设备告警数量
                alert_count = AlertInfo.query.filter(
                    and_(
                        AlertInfo.deviceSn == device.deviceSn,
                        AlertInfo.created_at >= start_time,
                        AlertInfo.created_at <= end_time
                    )
                ).count()
                
                analysis_data.append({
                    'deviceSn': device.deviceSn,
                    'deviceName': device.deviceName,
                    'health_count': health_count,
                    'alert_count': alert_count,
                    'status': device.status
                })
            
            return {
                'success': True,
                'data': analysis_data
            }
        except Exception as e:
            logger.error(f"获取设备分析数据失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_alert_stats(self, customer_id):
        """获取告警统计"""
        try:
            # 按严重程度统计告警
            severity_stats = db.session.query(
                AlertInfo.severityLevel,
                func.count(AlertInfo.id)
            ).filter(
                AlertInfo.customerId == customer_id
            ).group_by(AlertInfo.severityLevel).all()
            
            # 按类型统计告警
            type_stats = db.session.query(
                AlertInfo.alertType,
                func.count(AlertInfo.id)
            ).filter(
                AlertInfo.customerId == customer_id
            ).group_by(AlertInfo.alertType).all()
            
            return {
                'success': True,
                'data': {
                    'severity_stats': [{'level': s[0], 'count': s[1]} for s in severity_stats],
                    'type_stats': [{'type': t[0], 'count': t[1]} for t in type_stats]
                }
            }
        except Exception as e:
            logger.error(f"获取告警统计失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_message_stats(self, customer_id):
        """获取消息统计"""
        try:
            # 按类型统计消息
            type_stats = db.session.query(
                DeviceMessage.message_type,
                func.count(DeviceMessage.id)
            ).filter(
                DeviceMessage.customerId == customer_id
            ).group_by(DeviceMessage.message_type).all()
            
            # 按状态统计消息
            status_stats = db.session.query(
                DeviceMessage.message_status,
                func.count(DeviceMessage.id)
            ).filter(
                DeviceMessage.customerId == customer_id
            ).group_by(DeviceMessage.message_status).all()
            
            return {
                'success': True,
                'data': {
                    'type_stats': [{'type': t[0], 'count': t[1]} for t in type_stats],
                    'status_stats': [{'status': s[0], 'count': s[1]} for s in status_stats]
                }
            }
        except Exception as e:
            logger.error(f"获取消息统计失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_tracks_data(self):
        """获取轨迹数据"""
        try:
            # 模拟轨迹数据
            tracks = [
                {
                    'name': '轨迹1',
                    'color': '#00ff00',
                    'coordinates': [
                        [114.025246, 22.543721],
                        [114.028293, 22.545632],
                        [114.031876, 22.547891],
                        [114.035234, 22.549012],
                        [114.038765, 22.551234]
                    ],
                    'stats': {
                        'distance': 5.2,
                        'time': 45,
                        'speed': 6.9
                    }
                },
                {
                    'name': '轨迹2',
                    'color': '#ff00ff',
                    'coordinates': [
                        [114.027246, 22.541721],
                        [114.029293, 22.543632],
                        [114.032876, 22.545891],
                        [114.036234, 22.547012],
                        [114.039765, 22.549234]
                    ],
                    'stats': {
                        'distance': 4.8,
                        'time': 42,
                        'speed': 6.9
                    }
                }
            ]
            
            return {
                'success': True,
                'data': tracks
            }
        except Exception as e:
            logger.error(f"获取轨迹数据失败: {e}")
            return {'success': False, 'message': str(e)} 