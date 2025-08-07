#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watch端服务层
实现5个核心接口的业务逻辑
"""

from flask import jsonify, current_app
from datetime import datetime
from ...models import db, UserHealthData, UserHealthData, DeviceInfo, DeviceInfoHistory, DeviceMessage, HealthDataConfig
from ...models import AlertInfo, SystemEventRule, EventAlarmQueue
import json

class WatchService:
    """Watch端服务类"""
    
    def __init__(self):
        self.logger = current_app.logger if current_app else None
    
    def upload_health_data(self, health_data, device_sn=None):
        """上传健康数据"""
        try:
            # 提取数据字段
            data_field = health_data.get('data', {})
            
            # 处理数组或对象格式的数据
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
                    item_device_sn = data_item.get('deviceSn') or data_item.get('id') or device_sn
                    if not item_device_sn:
                        error_count += 1
                        continue
                    
                    # 创建健康数据记录
                    health_record = UserHealthData(
                        upload_method=health_data.get('upload_method', 'wifi'),
                        heart_rate=data_item.get('heartRate'),
                        pressure_high=data_item.get('pressureHigh'),
                        pressure_low=data_item.get('pressureLow'),
                        blood_oxygen=data_item.get('bloodOxygen'),
                        temperature=data_item.get('temperature'),
                        stress=data_item.get('stress'),
                        step=data_item.get('step'),
                        timestamp=datetime.fromisoformat(data_item.get('timestamp')) if data_item.get('timestamp') else datetime.utcnow(),
                        latitude=data_item.get('latitude'),
                        longitude=data_item.get('longitude'),
                        altitude=data_item.get('altitude'),
                        device_sn=item_device_sn,
                        distance=data_item.get('distance'),
                        calorie=data_item.get('calorie'),
                        sleep=data_item.get('sleep'),
                        user_id=data_item.get('userId'),
                        org_id=data_item.get('orgId')
                    )
                    
                    db.session.add(health_record)
                    success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"处理健康数据项失败: {str(e)}")
                    error_count += 1
                    continue
            
            # 提交事务
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": f"健康数据上传成功，成功{success_count}条，失败{error_count}条",
                "success_count": success_count,
                "error_count": error_count
            })
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"健康数据上传失败: {str(e)}")
            return jsonify({"status": "error", "message": f"上传失败: {str(e)}"}), 500
    
    def upload_device_info(self, device_info, device_sn=None):
        """上传设备信息"""
        try:
            # 提取设备SN
            if not device_sn:
                device_sn = device_info.get('SerialNumber') or device_info.get('serial_number') or device_info.get('deviceSn')
            
            if not device_sn:
                return jsonify({"status": "error", "message": "设备序列号不能为空"}), 400
            
            # 创建设备信息记录
            device_record = DeviceInfo(
                serial_number=device_sn,
                system_software_version=device_info.get('systemSoftwareVersion', ''),
                wifi_address=device_info.get('wifiAddress'),
                bluetooth_address=device_info.get('bluetoothAddress'),
                ip_address=device_info.get('ipAddress'),
                network_access_mode=device_info.get('networkAccessMode'),
                device_name=device_info.get('deviceName'),
                imei=device_info.get('imei'),
                battery_level=str(device_info.get('batteryLevel', '0')),
                voltage=str(device_info.get('voltage', '0')),
                model=device_info.get('model'),
                status=device_info.get('status', 'ACTIVE'),
                wearable_status=device_info.get('wearableStatus', 'NOT_WORN'),
                charging_status=device_info.get('chargingStatus', 'NOT_CHARGING'),
                user_id=device_info.get('userId'),
                org_id=device_info.get('orgId'),
                timestamp=datetime.utcnow()
            )
            
            # 同时创建历史记录
            history_record = DeviceInfoHistory(
                serial_number=device_sn,
                timestamp=datetime.utcnow(),
                system_software_version=device_info.get('systemSoftwareVersion'),
                battery_level=device_info.get('batteryLevel'),
                wearable_status=device_info.get('wearableStatus'),
                charging_status=device_info.get('chargingStatus'),
                voltage=device_info.get('voltage'),
                ip_address=device_info.get('ipAddress'),
                network_access_mode=device_info.get('networkAccessMode'),
                status=device_info.get('status')
            )
            
            db.session.add(device_record)
            db.session.add(history_record)
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": "设备信息上传成功",
                "device_sn": device_sn
            })
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"设备信息上传失败: {str(e)}")
            return jsonify({"status": "error", "message": f"上传失败: {str(e)}"}), 500
    
    def upload_common_event(self, event_data):
        """上传通用事件"""
        try:
            # 提取事件信息
            event_type = event_data.get('eventType')
            device_sn = event_data.get('deviceSn')
            event_value = event_data.get('eventValue')
            
            if not event_type or not device_sn:
                return jsonify({"status": "error", "message": "事件类型和设备序列号不能为空"}), 400
            
            # 创建事件队列记录
            event_queue = EventAlarmQueue(
                event_type=event_type,
                device_sn=device_sn,
                event_value=event_value,
                event_data=event_data,
                processing_status='pending'
            )
            
            db.session.add(event_queue)
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": "事件上传成功",
                "event_type": event_type,
                "device_sn": device_sn
            })
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"通用事件上传失败: {str(e)}")
            return jsonify({"status": "error", "message": f"上传失败: {str(e)}"}), 500
    
    def save_device_message(self, data):
        """保存设备消息"""
        try:
            # 创建新的消息记录
            new_message = DeviceMessage(
                device_sn=data.get('deviceSn'),
                message=data.get('message'),
                message_type=data.get('message_type'),
                sender_type=data.get('sender_type'),
                receiver_type=data.get('receiver_type'),
                message_status=data.get('message_status', 'pending'),
                department_info=data.get('department_info'),
                user_id=data.get('user_id'),
                sent_time=datetime.utcnow()
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
            self.logger.error(f"设备消息保存失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'保存消息失败: {str(e)}'
            }), 500
    
    def send_device_message(self, data):
        """发送设备消息"""
        try:
            # 这里可以添加消息发送的具体逻辑
            # 目前返回成功响应
            return jsonify({
                'success': True,
                'message': '消息发送成功',
                'data': data
            })
            
        except Exception as e:
            self.logger.error(f"设备消息发送失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'发送消息失败: {str(e)}'
            }), 500
    
    def received_messages(self, device_sn):
        """接收设备消息"""
        try:
            if not device_sn:
                return jsonify({
                    'success': False,
                    'message': '设备序列号不能为空'
                }), 400
            
            # 查询设备消息
            messages = DeviceMessage.query.filter_by(
                device_sn=device_sn,
                is_deleted=False
            ).order_by(DeviceMessage.sent_time.desc()).limit(50).all()
            
            # 转换为字典格式
            message_list = []
            for msg in messages:
                message_list.append({
                    'id': msg.id,
                    'device_sn': msg.device_sn,
                    'message': msg.message,
                    'message_type': msg.message_type,
                    'sender_type': msg.sender_type,
                    'receiver_type': msg.receiver_type,
                    'message_status': msg.message_status,
                    'sent_time': msg.sent_time.isoformat() if msg.sent_time else None,
                    'received_time': msg.received_time.isoformat() if msg.received_time else None
                })
            
            return jsonify({
                'success': True,
                'message': '消息查询成功',
                'data': message_list,
                'count': len(message_list)
            })
            
        except Exception as e:
            self.logger.error(f"设备消息查询失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'查询消息失败: {str(e)}'
            }), 500
    
    def fetch_health_data_config(self, customer_id, device_sn):
        """获取健康数据配置"""
        try:
            # 查询健康数据配置
            configs = HealthDataConfig.query.filter_by(
                customer_id=customer_id,
                is_deleted=False
            ).all()
            
            # 转换为字典格式
            config_list = []
            for config in configs:
                config_list.append({
                    'id': config.id,
                    'customer_id': config.customer_id,
                    'data_type': config.data_type,
                    'frequency_interval': config.frequency_interval,
                    'is_realtime': config.is_realtime,
                    'is_enabled': config.is_enabled,
                    'is_default': config.is_default,
                    'warning_high': float(config.warning_high) if config.warning_high else None,
                    'warning_low': float(config.warning_low) if config.warning_low else None,
                    'warning_cnt': config.warning_cnt,
                    'weight': float(config.weight) if config.weight else None
                })
            
            return jsonify({
                'success': True,
                'message': '配置查询成功',
                'data': config_list,
                'count': len(config_list)
            })
            
        except Exception as e:
            self.logger.error(f"健康数据配置查询失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'查询配置失败: {str(e)}'
            }), 500 