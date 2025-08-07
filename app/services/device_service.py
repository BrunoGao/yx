from flask import current_app
from ..models import db, DeviceInfo, UserInfo
from sqlalchemy import and_
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DeviceService:
    """设备服务层，处理设备相关的业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def get_device_info(self, serial_number):
        """根据序列号获取设备信息"""
        try:
            device_info = DeviceInfo.query.filter_by(deviceSn=serial_number).first()
            if device_info:
                return {
                    'success': True,
                    'data': device_info.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': '设备不存在'
                }
        except Exception as e:
            logger.error(f"获取设备信息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_devices_by_customer_id(self, customer_id):
        """根据客户ID获取设备列表"""
        try:
            devices = DeviceInfo.query.filter_by(customerId=customer_id).all()
            return {
                'success': True,
                'data': [device.to_dict() for device in devices]
            }
        except Exception as e:
            logger.error(f"获取设备列表失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def gather_device_info(self, customer_id):
        """收集设备信息"""
        try:
            devices = DeviceInfo.query.filter_by(customerId=customer_id).all()
            device_stats = []
            
            for device in devices:
                # 获取设备关联的用户数量
                user_count = UserInfo.query.filter_by(deviceSn=device.deviceSn).count()
                
                device_stats.append({
                    'deviceSn': device.deviceSn,
                    'deviceName': device.deviceName,
                    'status': device.status,
                    'user_count': user_count,
                    'created_at': device.created_at.isoformat() if device.created_at else None
                })
            
            return {
                'success': True,
                'data': device_stats
            }
        except Exception as e:
            logger.error(f"收集设备信息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_customer_id_by_deviceSn(self, deviceSn):
        """根据设备序列号获取客户ID"""
        try:
            device_info = DeviceInfo.query.filter_by(deviceSn=deviceSn).first()
            if device_info:
                return {
                    'success': True,
                    'data': {
                        'customerId': device_info.customerId
                    }
                }
            else:
                return {
                    'success': False,
                    'message': '设备不存在'
                }
        except Exception as e:
            logger.error(f"获取客户ID失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_devices_by_orgIdAndUserId(self, orgId, userId):
        """根据组织ID和用户ID获取设备列表"""
        try:
            # 先获取用户信息
            user_info = UserInfo.query.filter(
                and_(
                    UserInfo.orgId == orgId,
                    UserInfo.userId == userId
                )
            ).first()
            
            if not user_info:
                return {
                    'success': False,
                    'message': '用户不存在'
                }
            
            # 获取用户的设备信息
            device_info = DeviceInfo.query.filter_by(deviceSn=user_info.deviceSn).first()
            if device_info:
                return {
                    'success': True,
                    'data': [device_info.to_dict()]
                }
            else:
                return {
                    'success': True,
                    'data': []
                }
        except Exception as e:
            logger.error(f"根据组织ID和用户ID获取设备列表失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def generate_device_stats(self, customer_id):
        """生成设备统计信息"""
        try:
            # 设备总数
            total_devices = DeviceInfo.query.filter_by(customerId=customer_id).count()
            
            # 在线设备数
            online_devices = DeviceInfo.query.filter(
                and_(
                    DeviceInfo.customerId == customer_id,
                    DeviceInfo.status == 'online'
                )
            ).count()
            
            # 离线设备数
            offline_devices = DeviceInfo.query.filter(
                and_(
                    DeviceInfo.customerId == customer_id,
                    DeviceInfo.status == 'offline'
                )
            ).count()
            
            return {
                'success': True,
                'data': {
                    'total_devices': total_devices,
                    'online_devices': online_devices,
                    'offline_devices': offline_devices,
                    'online_rate': round(online_devices / total_devices * 100, 2) if total_devices > 0 else 0
                }
            }
        except Exception as e:
            logger.error(f"生成设备统计信息失败: {e}")
            return {'success': False, 'message': str(e)} 