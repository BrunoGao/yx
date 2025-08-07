from flask import jsonify, current_app
from ..models import db, UserHealthData, DeviceInfo, DeviceMessage, AlertInfo
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class WatchService:
    """Watch端服务层，实现五个核心接口业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def upload_health_data(self, health_data):
        """上传健康数据 - 核心接口1"""
        try:
            if not health_data:
                return jsonify({"status": "error", "message": "请求体不能为空"}), 400
            
            data_field = health_data.get('data', {})
            logger.info(f"健康数据上传开始，data类型: {type(data_field)}")
            
            # 处理数组或对象格式
            if isinstance(data_field, list):
                data_list = data_field
            elif isinstance(data_field, dict):
                data_list = [data_field]
            else:
                return jsonify({"status": "error", "message": "数据格式错误"}), 400
            
            success_count = 0
            error_count = 0
            
            for data_item in data_list:
                try:
                    # 提取设备SN
                    device_sn = data_item.get('deviceSn') or data_item.get('id')
                    if not device_sn:
                        error_count += 1
                        continue
                    
                    # 创建健康数据记录
                    health_record = UserHealthData(
                        deviceSn=device_sn,
                        userId=data_item.get('userId'),
                        orgId=data_item.get('orgId'),
                        heartRate=data_item.get('heartRate'),
                        systolicPressure=data_item.get('pressureHigh'),
                        diastolicPressure=data_item.get('pressureLow'),
                        bloodOxygen=data_item.get('bloodOxygen'),
                        bodyTemperature=data_item.get('temperature'),
                        latitude=data_item.get('latitude'),
                        longitude=data_item.get('longitude'),
                        created_at=datetime.fromisoformat(data_item.get('timestamp')) if data_item.get('timestamp') else datetime.now()
                    )
                    
                    db.session.add(health_record)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"处理健康数据项失败: {str(e)}")
                    error_count += 1
                    continue
            
            db.session.commit()
            logger.info(f"健康数据上传完成，成功{success_count}条，失败{error_count}条")
            
            return jsonify({
                "status": "success",
                "message": f"健康数据上传成功，成功{success_count}条，失败{error_count}条",
                "success_count": success_count,
                "error_count": error_count
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"健康数据上传失败: {str(e)}")
            return jsonify({"status": "error", "message": f"上传失败: {str(e)}"}), 500
    
    def upload_device_info(self, device_info):
        """上传设备信息 - 核心接口2"""
        try:
            device_sn = device_info.get('SerialNumber') or device_info.get('serial_number') or device_info.get('deviceSn')
            
            if not device_sn:
                return jsonify({"status": "error", "message": "设备序列号不能为空"}), 400
            
            # 检查设备是否已存在
            existing_device = DeviceInfo.query.filter_by(deviceSn=device_sn).first()
            
            if existing_device:
                # 更新现有设备信息
                existing_device.deviceName = device_info.get('deviceName', existing_device.deviceName)
                existing_device.status = device_info.get('status', existing_device.status)
                existing_device.updated_at = datetime.now()
            else:
                # 创建新设备信息
                device_record = DeviceInfo(
                    deviceSn=device_sn,
                    deviceName=device_info.get('deviceName', ''),
                    customerId=device_info.get('customerId'),
                    status=device_info.get('status', 'online'),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.add(device_record)
            
            db.session.commit()
            logger.info(f"设备信息上传成功: {device_sn}")
            
            return jsonify({
                "status": "success",
                "message": "设备信息上传成功",
                "device_sn": device_sn
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"设备信息上传失败: {str(e)}")
            return jsonify({"status": "error", "message": f"上传失败: {str(e)}"}), 500
    
    def upload_common_event(self, event_data):
        """上传通用事件 - 核心接口3"""
        try:
            event_type = event_data.get('eventType')
            device_sn = event_data.get('deviceSn')
            event_value = event_data.get('eventValue')
            
            if not event_type or not device_sn:
                return jsonify({"status": "error", "message": "事件类型和设备序列号不能为空"}), 400
            
            # 创建告警记录
            alert_record = AlertInfo(
                deviceSn=device_sn,
                customerId=event_data.get('customerId'),
                userId=event_data.get('userId'),
                orgId=event_data.get('orgId'),
                alertType=event_type,
                severityLevel=event_data.get('severityLevel', 'info'),
                message=f"{event_type}: {event_value}",
                status='pending',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.session.add(alert_record)
            db.session.commit()
            
            logger.info(f"通用事件上传成功: {event_type}, 设备: {device_sn}")
            
            return jsonify({
                "status": "success",
                "message": "事件上传成功",
                "event_type": event_type,
                "device_sn": device_sn
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"通用事件上传失败: {str(e)}")
            return jsonify({"status": "error", "message": f"上传失败: {str(e)}"}), 500
    
    def send_device_message(self, data):
        """发送设备消息 - 核心接口4"""
        try:
            # 创建新的消息记录
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
            
            logger.info(f"设备消息发送成功: {data.get('deviceSn')}")
            
            return jsonify({
                'success': True,
                'message': '消息发送成功',
                'message_id': new_message.id
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"设备消息发送失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'发送消息失败: {str(e)}'
            }), 500
    
    def receive_device_messages(self, device_sn):
        """接收设备消息 - 核心接口4"""
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
            
            logger.info(f"设备消息查询成功: {device_sn}, 消息数量: {len(message_list)}")
            
            return jsonify({
                'success': True,
                'data': message_list
            })
            
        except Exception as e:
            logger.error(f"设备消息查询失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'查询消息失败: {str(e)}'
            }), 500
    
    def fetch_health_data_config(self, customer_id=None, device_sn=None):
        """获取健康数据配置 - 核心接口5"""
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
            
            # 根据客户ID和设备SN可以返回不同的配置
            if customer_id:
                # 这里可以查询数据库获取客户特定配置
                pass
            
            if device_sn:
                # 这里可以查询数据库获取设备特定配置
                pass
            
            logger.info(f"健康数据配置查询成功: customer_id={customer_id}, device_sn={device_sn}")
            
            return jsonify({
                'success': True,
                'data': default_config
            })
            
        except Exception as e:
            logger.error(f"健康数据配置查询失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'查询配置失败: {str(e)}'
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