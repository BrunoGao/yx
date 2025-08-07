from flask import current_app
from ..models import db, DeviceMessage
from sqlalchemy import and_, func
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class MessageService:
    """消息服务层，处理消息相关的业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def get_messages(self, deviceSn=None, messageType=None, customerId=None):
        """获取消息列表"""
        try:
            query = DeviceMessage.query
            
            if deviceSn:
                query = query.filter_by(deviceSn=deviceSn)
            
            if messageType:
                query = query.filter_by(message_type=messageType)
            
            if customerId:
                query = query.filter_by(customerId=customerId)
            
            messages = query.order_by(DeviceMessage.sent_time.desc()).all()
            
            return {
                'success': True,
                'data': [message.to_dict() for message in messages]
            }
        except Exception as e:
            logger.error(f"获取消息列表失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def send_message(self, data):
        """发送消息"""
        try:
            message = DeviceMessage(
                message=data.get('message'),
                message_type=data.get('message_type'),
                sender_type=data.get('sender_type'),
                receiver_type=data.get('receiver_type'),
                message_status=data.get('message_status', 'sent'),
                department_info=data.get('department_info'),
                user_id=data.get('user_id'),
                deviceSn=data.get('deviceSn'),
                customerId=data.get('customerId'),
                sent_time=datetime.now()
            )
            
            db.session.add(message)
            db.session.commit()
            
            return {
                'success': True,
                'message': '消息发送成功',
                'data': {
                    'message_id': message.id
                }
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"发送消息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def receive_messages(self, deviceSn):
        """接收消息"""
        try:
            messages = DeviceMessage.query.filter_by(
                deviceSn=deviceSn
            ).order_by(DeviceMessage.sent_time.desc()).all()
            
            return {
                'success': True,
                'data': [message.to_dict() for message in messages]
            }
        except Exception as e:
            logger.error(f"接收消息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_message_stats(self):
        """获取消息统计"""
        try:
            # 按类型统计消息
            type_stats = db.session.query(
                DeviceMessage.message_type,
                func.count(DeviceMessage.id)
            ).group_by(DeviceMessage.message_type).all()
            
            # 按状态统计消息
            status_stats = db.session.query(
                DeviceMessage.message_status,
                func.count(DeviceMessage.id)
            ).group_by(DeviceMessage.message_status).all()
            
            # 最近7天消息数量
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            daily_stats = db.session.query(
                func.date(DeviceMessage.sent_time).label('date'),
                func.count(DeviceMessage.id).label('count')
            ).filter(
                and_(
                    DeviceMessage.sent_time >= start_date,
                    DeviceMessage.sent_time <= end_date
                )
            ).group_by(func.date(DeviceMessage.sent_time)).all()
            
            return {
                'success': True,
                'data': {
                    'type_stats': [{'type': t[0], 'count': t[1]} for t in type_stats],
                    'status_stats': [{'status': s[0], 'count': s[1]} for s in status_stats],
                    'daily_stats': [{'date': str(s.date), 'count': s.count} for s in daily_stats]
                }
            }
        except Exception as e:
            logger.error(f"获取消息统计失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_messages_by_orgIdAndUserId(self, orgId, userId, messageType=None):
        """根据组织ID和用户ID获取消息"""
        try:
            query = DeviceMessage.query.filter(
                and_(
                    DeviceMessage.orgId == orgId,
                    DeviceMessage.userId == userId
                )
            )
            
            if messageType:
                query = query.filter_by(message_type=messageType)
            
            messages = query.order_by(DeviceMessage.sent_time.desc()).all()
            
            return {
                'success': True,
                'data': [message.to_dict() for message in messages]
            }
        except Exception as e:
            logger.error(f"根据组织ID和用户ID获取消息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def save_message(self, data):
        """保存消息"""
        try:
            message = DeviceMessage(
                message=data.get('message'),
                message_type=data.get('message_type'),
                sender_type=data.get('sender_type'),
                receiver_type=data.get('receiver_type'),
                message_status=data.get('message_status', 'draft'),
                department_info=data.get('department_info'),
                user_id=data.get('user_id'),
                deviceSn=data.get('deviceSn'),
                customerId=data.get('customerId'),
                sent_time=datetime.now()
            )
            
            db.session.add(message)
            db.session.commit()
            
            return {
                'success': True,
                'message': '消息保存成功',
                'data': {
                    'message_id': message.id
                }
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存消息失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def update_message_status(self, message_id, status):
        """更新消息状态"""
        try:
            message = DeviceMessage.query.get(message_id)
            if not message:
                return {
                    'success': False,
                    'message': '消息不存在'
                }
            
            message.message_status = status
            if status == 'read':
                message.read_time = datetime.now()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '消息状态更新成功'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新消息状态失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def delete_message(self, message_id):
        """删除消息"""
        try:
            message = DeviceMessage.query.get(message_id)
            if not message:
                return {
                    'success': False,
                    'message': '消息不存在'
                }
            
            db.session.delete(message)
            db.session.commit()
            
            return {
                'success': True,
                'message': '消息删除成功'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除消息失败: {e}")
            return {'success': False, 'message': str(e)} 