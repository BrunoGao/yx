from flask import jsonify, current_app, request
from ..models import db, UserHealthData, DeviceInfo, DeviceMessage, AlertInfo, UserInfo
from datetime import datetime, timedelta
import json
import logging
import random
from sqlalchemy import func, and_
from functools import wraps

logger = logging.getLogger(__name__)

class BigScreenService:
    """大屏服务层，实现所有大屏业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def get_tracks(self):
        """获取轨迹数据"""
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
                    'distance': 3.8,
                    'time': 30,
                    'speed': 7.6
                }
            }
        ]
        return jsonify(tracks)
    
    def generate_track_points(self):
        """生成模拟轨迹点"""
        base_lon = 114.02
        base_lat = 22.54
        points = []
        for i in range(10):
            points.append([
                base_lon + random.uniform(-0.02, 0.02),
                base_lat + random.uniform(-0.02, 0.02)
            ])
        return points
    
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
    
    def fetch_health_data(self, device_sn=None):
        """获取健康数据"""
        try:
            if device_sn:
                health_data = UserHealthData.query.filter_by(deviceSn=device_sn).order_by(UserHealthData.created_at.desc()).limit(100).all()
            else:
                device_sn = request.args.get('deviceSn')
                health_data = UserHealthData.query.filter_by(deviceSn=device_sn).order_by(UserHealthData.created_at.desc()).limit(100).all()
            
            data_list = []
            for data in health_data:
                data_list.append({
                    'id': data.id,
                    'deviceSn': data.deviceSn,
                    'userId': data.userId,
                    'orgId': data.orgId,
                    'heartRate': data.heartRate,
                    'systolicPressure': data.systolicPressure,
                    'diastolicPressure': data.diastolicPressure,
                    'bloodOxygen': data.bloodOxygen,
                    'bodyTemperature': data.bodyTemperature,
                    'latitude': data.latitude,
                    'longitude': data.longitude,
                    'created_at': data.created_at.isoformat() if data.created_at else None
                })
            
            return jsonify({
                'success': True,
                'data': data_list
            })
        except Exception as e:
            logger.error(f"获取健康数据失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取健康数据失败: {str(e)}'
            }), 500
    
    def fetch_alerts(self, device_sn=None, customer_id=None):
        """获取告警数据"""
        try:
            query = AlertInfo.query
            if device_sn:
                query = query.filter_by(deviceSn=device_sn)
            if customer_id:
                query = query.filter_by(customerId=customer_id)
            
            alerts = query.order_by(AlertInfo.created_at.desc()).limit(100).all()
            
            alert_list = []
            for alert in alerts:
                alert_list.append({
                    'id': alert.id,
                    'deviceSn': alert.deviceSn,
                    'customerId': alert.customerId,
                    'userId': alert.userId,
                    'orgId': alert.orgId,
                    'alertType': alert.alertType,
                    'severityLevel': alert.severityLevel,
                    'message': alert.message,
                    'status': alert.status,
                    'created_at': alert.created_at.isoformat() if alert.created_at else None
                })
            
            return jsonify({
                'success': True,
                'data': alert_list
            })
        except Exception as e:
            logger.error(f"获取告警数据失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取告警数据失败: {str(e)}'
            }), 500
    
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
    
    def fetch_device_info(self, serial_number=None):
        """获取设备信息"""
        try:
            if serial_number:
                device = DeviceInfo.query.filter_by(deviceSn=serial_number).first()
            else:
                serial_number = request.args.get('serial_number')
                device = DeviceInfo.query.filter_by(deviceSn=serial_number).first()
            
            if device:
                return jsonify({
                    'success': True,
                    'data': {
                        'id': device.id,
                        'deviceSn': device.deviceSn,
                        'deviceName': device.deviceName,
                        'customerId': device.customerId,
                        'status': device.status,
                        'created_at': device.created_at.isoformat() if device.created_at else None,
                        'updated_at': device.updated_at.isoformat() if device.updated_at else None
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '设备不存在'
                }), 404
        except Exception as e:
            logger.error(f"获取设备信息失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取设备信息失败: {str(e)}'
            }), 500
    
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
    
    def generate_alert_json(self, customer_id=None, user_id=None, severity_level=None):
        """生成告警数据JSON"""
        try:
            query = AlertInfo.query
            if customer_id:
                query = query.filter_by(customerId=customer_id)
            if user_id:
                query = query.filter_by(userId=user_id)
            if severity_level:
                query = query.filter_by(severityLevel=severity_level)
            
            alerts = query.order_by(AlertInfo.created_at.desc()).limit(100).all()
            
            alert_list = []
            for alert in alerts:
                alert_list.append({
                    'id': alert.id,
                    'deviceSn': alert.deviceSn,
                    'customerId': alert.customerId,
                    'userId': alert.userId,
                    'orgId': alert.orgId,
                    'alertType': alert.alertType,
                    'severityLevel': alert.severityLevel,
                    'message': alert.message,
                    'status': alert.status,
                    'created_at': alert.created_at.isoformat() if alert.created_at else None
                })
            
            return jsonify({
                'success': True,
                'data': alert_list
            })
        except Exception as e:
            logger.error(f"生成告警数据JSON失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'生成告警数据JSON失败: {str(e)}'
            }), 500
    
    def get_health_stats(self):
        """获取健康统计"""
        try:
            # 获取健康数据统计
            total_health_data = UserHealthData.query.count()
            total_alerts = AlertInfo.query.count()
            total_messages = DeviceMessage.query.count()
            total_devices = DeviceInfo.query.count()
            
            # 获取最近24小时的数据
            yesterday = datetime.now() - timedelta(days=1)
            recent_health_data = UserHealthData.query.filter(
                UserHealthData.created_at >= yesterday
            ).count()
            
            recent_alerts = AlertInfo.query.filter(
                AlertInfo.created_at >= yesterday
            ).count()
            
            return jsonify({
                'success': True,
                'data': {
                    'total_health_data': total_health_data,
                    'total_alerts': total_alerts,
                    'total_messages': total_messages,
                    'total_devices': total_devices,
                    'recent_health_data': recent_health_data,
                    'recent_alerts': recent_alerts
                }
            })
        except Exception as e:
            logger.error(f"获取健康统计失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取健康统计失败: {str(e)}'
            }), 500
    
    def check_license(self):
        """检查许可证"""
        try:
            # 模拟许可证检查
            return jsonify({
                'success': True,
                'data': {
                    'license_valid': True,
                    'expire_date': '2025-12-31',
                    'features': ['health_monitor', 'alert_system', 'message_system']
                }
            })
        except Exception as e:
            logger.error(f"检查许可证失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'检查许可证失败: {str(e)}'
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
    
    def upload_device_info(self, device_info):
        """上传设备信息"""
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
            
            return jsonify({
                "status": "success",
                "message": "设备信息上传成功",
                "device_sn": device_sn
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"上传设备信息失败: {str(e)}")
            return jsonify({"status": "error", "message": f"上传失败: {str(e)}"}), 500
    
    def upload_health_data(self, health_data):
        """上传健康数据"""
        try:
            if not health_data:
                return jsonify({"status": "error", "message": "请求体不能为空"}), 400
            
            data_field = health_data.get('data', {})
            
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
    
    def upload_common_event(self, event_data):
        """上传通用事件"""
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
    
    def get_health_data(self, device_sn=None, date=None):
        """获取健康数据"""
        try:
            query = UserHealthData.query
            if device_sn:
                query = query.filter_by(deviceSn=device_sn)
            if date:
                query = query.filter(func.date(UserHealthData.created_at) == date)
            
            health_data = query.order_by(UserHealthData.created_at.desc()).limit(100).all()
            
            data_list = []
            for data in health_data:
                data_list.append({
                    'id': data.id,
                    'deviceSn': data.deviceSn,
                    'userId': data.userId,
                    'orgId': data.orgId,
                    'heartRate': data.heartRate,
                    'systolicPressure': data.systolicPressure,
                    'diastolicPressure': data.diastolicPressure,
                    'bloodOxygen': data.bloodOxygen,
                    'bodyTemperature': data.bodyTemperature,
                    'latitude': data.latitude,
                    'longitude': data.longitude,
                    'created_at': data.created_at.isoformat() if data.created_at else None
                })
            
            return jsonify({
                'success': True,
                'data': data_list
            })
        except Exception as e:
            logger.error(f"获取健康数据失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取健康数据失败: {str(e)}'
            }), 500
    
    def upload_alerts(self, data):
        """上传告警数据"""
        try:
            if not data:
                return jsonify({"status": "error", "message": "请求体不能为空"}), 400
            
            alert_list = data.get('alerts', [])
            if not isinstance(alert_list, list):
                alert_list = [data]
            
            success_count = 0
            error_count = 0
            
            for alert_item in alert_list:
                try:
                    alert_record = AlertInfo(
                        deviceSn=alert_item.get('deviceSn'),
                        customerId=alert_item.get('customerId'),
                        userId=alert_item.get('userId'),
                        orgId=alert_item.get('orgId'),
                        alertType=alert_item.get('alertType'),
                        severityLevel=alert_item.get('severityLevel', 'info'),
                        message=alert_item.get('message'),
                        status=alert_item.get('status', 'pending'),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    db.session.add(alert_record)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"处理告警数据项失败: {str(e)}")
                    error_count += 1
                    continue
            
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": f"告警数据上传成功，成功{success_count}条，失败{error_count}条",
                "success_count": success_count,
                "error_count": error_count
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"告警数据上传失败: {str(e)}")
            return jsonify({"status": "error", "message": f"上传失败: {str(e)}"}), 500 