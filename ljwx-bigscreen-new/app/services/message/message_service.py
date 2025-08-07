from flask import jsonify, request, current_app
from ...models import db, DeviceMessage
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MessageService:
    """消息服务，实现消息相关业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def fetch_messages(self, device_sn=None, message_type=None, customer_id=None):
        """获取消息数据"""
        try:
            query = DeviceMessage.query
            if device_sn:
                query = query.filter_by(deviceSn=device_sn)
            if message_type:
                query = query.filter_by(message_type=message_type)
            if customer_id:
                query = query.filter_by(customerId=customer_id)
            
            messages = query.order_by(DeviceMessage.sent_time.desc()).limit(100).all()
            
            message_list = []
            for message in messages:
                message_list.append({
                    'id': message.id,
                    'deviceSn': message.deviceSn,
                    'customerId': message.customerId,
                    'userId': message.userId,
                    'orgId': message.orgId,
                    'message': message.message,
                    'message_type': message.message_type,
                    'sender_type': message.sender_type,
                    'receiver_type': message.receiver_type,
                    'message_status': message.message_status,
                    'sent_time': message.sent_time.isoformat() if message.sent_time else None
                })
            
            return jsonify({
                'success': True,
                'data': message_list
            })
        except Exception as e:
            logger.error(f"获取消息数据失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取消息数据失败: {str(e)}'
            }), 500
    
    def save_device_message(self, data):
        """保存设备消息"""
        try:
            new_message = DeviceMessage(
                deviceSn=data.get('deviceSn'),
                customerId=data.get('customerId'),
                userId=data.get('userId'),
                orgId=data.get('orgId'),
                message=data.get('message'),
                message_type=data.get('message_type'),
                sender_type=data.get('sender_type'),
                receiver_type=data.get('receiver_type'),
                message_status=data.get('message_status', 'draft'),
                department_info=data.get('department_info'),
                sent_time=datetime.now(),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '消息保存成功',
                'message_id': new_message.id
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存设备消息失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'保存消息失败: {str(e)}'
            }), 500
    
    def send_device_message(self, data):
        """发送设备消息"""
        try:
            new_message = DeviceMessage(
                deviceSn=data.get('deviceSn'),
                customerId=data.get('customerId'),
                userId=data.get('userId'),
                orgId=data.get('orgId'),
                message=data.get('message'),
                message_type=data.get('message_type'),
                sender_type=data.get('sender_type'),
                receiver_type=data.get('receiver_type'),
                message_status=data.get('message_status', 'sent'),
                department_info=data.get('department_info'),
                sent_time=datetime.now(),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '消息发送成功',
                'message_id': new_message.id
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"发送设备消息失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'发送消息失败: {str(e)}'
            }), 500
    
    def receive_device_messages(self, device_sn):
        """接收设备消息"""
        try:
            messages = DeviceMessage.query.filter_by(
                deviceSn=device_sn
            ).order_by(DeviceMessage.sent_time.desc()).all()
            
            message_list = []
            for msg in messages:
                message_list.append({
                    'id': msg.id,
                    'message': msg.message,
                    'message_type': msg.message_type,
                    'sender_type': msg.sender_type,
                    'receiver_type': msg.receiver_type,
                    'message_status': msg.message_status,
                    'sent_time': msg.sent_time.isoformat() if msg.sent_time else None
                })
            
            return jsonify({
                'success': True,
                'data': message_list
            })
            
        except Exception as e:
            logger.error(f"接收设备消息失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'接收消息失败: {str(e)}'
            }), 500 