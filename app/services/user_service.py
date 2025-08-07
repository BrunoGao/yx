from flask import current_app
from ..models import db, UserInfo
from sqlalchemy import and_
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UserService:
    """用户服务层，处理用户相关的业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def get_user_info(self, deviceSn):
        """根据设备序列号获取用户信息"""
        try:
            user_info = UserInfo.query.filter_by(deviceSn=deviceSn).first()
            if user_info:
                return {
                    'success': True,
                    'data': user_info.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': '用户不存在'
                }
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_user_deviceSn(self, phone):
        """根据手机号获取设备序列号"""
        try:
            user_info = UserInfo.query.filter_by(phone=phone).first()
            if user_info:
                return {
                    'success': True,
                    'data': {
                        'deviceSn': user_info.deviceSn
                    }
                }
            else:
                return {
                    'success': False,
                    'message': '用户不存在'
                }
        except Exception as e:
            logger.error(f"获取用户设备序列号失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_user_id(self, phone):
        """根据手机号获取用户ID"""
        try:
            user_info = UserInfo.query.filter_by(phone=phone).first()
            if user_info:
                return {
                    'success': True,
                    'data': {
                        'userId': user_info.userId
                    }
                }
            else:
                return {
                    'success': False,
                    'message': '用户不存在'
                }
        except Exception as e:
            logger.error(f"获取用户ID失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_all_users(self):
        """获取所有用户"""
        try:
            users = UserInfo.query.all()
            return {
                'success': True,
                'data': [user.to_dict() for user in users]
            }
        except Exception as e:
            logger.error(f"获取所有用户失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_personal_user_info(self, deviceSn):
        """获取个人用户信息"""
        try:
            user_info = UserInfo.query.filter_by(deviceSn=deviceSn).first()
            if user_info:
                return {
                    'success': True,
                    'data': user_info.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': '用户不存在'
                }
        except Exception as e:
            logger.error(f"获取个人用户信息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_user_info_by_orgIdAndUserId(self, orgId, userId):
        """根据组织ID和用户ID获取用户信息"""
        try:
            user_info = UserInfo.query.filter(
                and_(
                    UserInfo.orgId == orgId,
                    UserInfo.userId == userId
                )
            ).first()
            if user_info:
                return {
                    'success': True,
                    'data': user_info.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': '用户不存在'
                }
        except Exception as e:
            logger.error(f"根据组织ID和用户ID获取用户信息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_device_info_by_phone(self, phone):
        """根据手机号获取设备信息"""
        try:
            user_info = UserInfo.query.filter_by(phone=phone).first()
            if user_info:
                return {
                    'success': True,
                    'data': {
                        'deviceSn': user_info.deviceSn,
                        'userId': user_info.userId,
                        'orgId': user_info.orgId
                    }
                }
            else:
                return {
                    'success': False,
                    'message': '用户不存在'
                }
        except Exception as e:
            logger.error(f"根据手机号获取设备信息失败: {e}")
            return {'success': False, 'message': str(e)} 