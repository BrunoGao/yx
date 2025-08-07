from flask import jsonify, request, current_app
from ...models import db, UserInfo
import logging

logger = logging.getLogger(__name__)

class UserService:
    """用户服务，实现用户相关业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def get_user_info(self, device_sn=None):
        """获取用户信息"""
        try:
            if device_sn:
                user = UserInfo.query.filter_by(deviceSn=device_sn).first()
            else:
                device_sn = request.args.get('deviceSn')
                user = UserInfo.query.filter_by(deviceSn=device_sn).first()
            
            if user:
                return jsonify({
                    'success': True,
                    'data': {
                        'id': user.id,
                        'name': user.name,
                        'phone': user.phone,
                        'deviceSn': user.deviceSn,
                        'orgId': user.orgId,
                        'customerId': user.customerId
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '用户不存在'
                }), 404
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取用户信息失败: {str(e)}'
            }), 500
    
    def get_all_users(self):
        """获取所有用户"""
        try:
            users = UserInfo.query.all()
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.id,
                    'name': user.name,
                    'phone': user.phone,
                    'deviceSn': user.deviceSn,
                    'orgId': user.orgId,
                    'customerId': user.customerId
                })
            return jsonify({
                'success': True,
                'data': user_list
            })
        except Exception as e:
            logger.error(f"获取所有用户失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取所有用户失败: {str(e)}'
            }), 500
    
    def get_user_device_sn(self, phone=None):
        """根据手机号获取设备SN"""
        try:
            if phone:
                user = UserInfo.query.filter_by(phone=phone).first()
            else:
                phone = request.args.get('phone')
                user = UserInfo.query.filter_by(phone=phone).first()
            
            if user:
                return jsonify({
                    'success': True,
                    'data': {
                        'deviceSn': user.deviceSn
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '用户不存在'
                }), 404
        except Exception as e:
            logger.error(f"获取用户设备SN失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取用户设备SN失败: {str(e)}'
            }), 500
    
    def get_user_id(self, phone=None):
        """根据手机号获取用户ID"""
        try:
            if phone:
                user = UserInfo.query.filter_by(phone=phone).first()
            else:
                phone = request.args.get('phone')
                user = UserInfo.query.filter_by(phone=phone).first()
            
            if user:
                return jsonify({
                    'success': True,
                    'data': {
                        'userId': user.id
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '用户不存在'
                }), 404
        except Exception as e:
            logger.error(f"获取用户ID失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取用户ID失败: {str(e)}'
            }), 500
    
    def get_personal_info(self, device_sn):
        """获取个人信息"""
        try:
            user = UserInfo.query.filter_by(deviceSn=device_sn).first()
            if not user:
                return jsonify({
                    'success': False,
                    'message': '用户不存在'
                }), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'phone': user.phone,
                        'deviceSn': user.deviceSn,
                        'orgId': user.orgId,
                        'customerId': user.customerId
                    }
                }
            })
        except Exception as e:
            logger.error(f"获取个人信息失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取个人信息失败: {str(e)}'
            }), 500 