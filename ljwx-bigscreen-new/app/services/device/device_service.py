from flask import jsonify, request, current_app
from ...models import db, DeviceInfo
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DeviceService:
    """设备服务，实现设备相关业务逻辑"""
    
    def __init__(self):
        self.db = db
    
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
    
    def get_customer_id_by_deviceSn(self, device_sn):
        """根据设备SN获取客户ID"""
        try:
            device = DeviceInfo.query.filter_by(deviceSn=device_sn).first()
            if device:
                return jsonify({
                    'success': True,
                    'data': {
                        'customerId': device.customerId
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '设备不存在'
                }), 404
        except Exception as e:
            logger.error(f"获取客户ID失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取客户ID失败: {str(e)}'
            }), 500
    
    def gather_device_info(self, customer_id=None):
        """获取设备信息汇总"""
        try:
            query = DeviceInfo.query
            if customer_id:
                query = query.filter_by(customerId=customer_id)
            
            devices = query.all()
            
            device_list = []
            for device in devices:
                device_list.append({
                    'id': device.id,
                    'deviceSn': device.deviceSn,
                    'deviceName': device.deviceName,
                    'customerId': device.customerId,
                    'status': device.status,
                    'created_at': device.created_at.isoformat() if device.created_at else None,
                    'updated_at': device.updated_at.isoformat() if device.updated_at else None
                })
            
            return jsonify({
                'success': True,
                'data': device_list
            })
        except Exception as e:
            logger.error(f"获取设备信息汇总失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取设备信息汇总失败: {str(e)}'
            }), 500 