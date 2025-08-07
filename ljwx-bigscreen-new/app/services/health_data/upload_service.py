from flask import jsonify, request, current_app
from ...models import db, UserHealthData
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HealthDataUploadService:
    """健康数据上传服务"""
    
    def __init__(self):
        self.db = db
    
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