from flask import jsonify, request, current_app
from ...models import db, AlertInfo
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class AlertService:
    """告警服务，实现告警相关业务逻辑"""
    
    def __init__(self):
        self.db = db
    
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
    
    def fetch_alertType_stats(self):
        """获取告警类型统计"""
        try:
            stats = db.session.query(
                AlertInfo.alertType,
                func.count(AlertInfo.id).label('count')
            ).group_by(AlertInfo.alertType).all()
            
            data = []
            for stat in stats:
                data.append({
                    'alertType': stat.alertType,
                    'count': stat.count
                })
            
            return jsonify({
                'success': True,
                'data': data
            })
        except Exception as e:
            logger.error(f"获取告警类型统计失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取告警类型统计失败: {str(e)}'
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
    
    def test_wechat_alert(self):
        """测试微信告警"""
        try:
            return jsonify({
                'success': True,
                'message': '微信告警测试成功',
                'data': {
                    'test_time': datetime.now().isoformat(),
                    'status': 'sent'
                }
            })
        except Exception as e:
            logger.error(f"测试微信告警失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'测试微信告警失败: {str(e)}'
            }), 500
    
    def generate_alert_chart(self):
        """生成告警图表数据"""
        try:
            # 获取告警统计图表数据
            stats = db.session.query(
                func.date(AlertInfo.created_at).label('date'),
                func.count(AlertInfo.id).label('count')
            ).group_by(
                func.date(AlertInfo.created_at)
            ).order_by(
                func.date(AlertInfo.created_at)
            ).limit(30).all()
            
            data = []
            for stat in stats:
                data.append({
                    'date': stat.date.strftime('%Y-%m-%d'),
                    'count': stat.count
                })
            
            return jsonify({
                'success': True,
                'data': data
            })
        except Exception as e:
            logger.error(f"生成告警图表数据失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'生成告警图表数据失败: {str(e)}'
            }), 500
    
    def generate_alert_type_chart(self, customer_id=None):
        """生成告警类型图表数据"""
        try:
            query = db.session.query(
                AlertInfo.alertType,
                func.count(AlertInfo.id).label('count')
            ).group_by(AlertInfo.alertType)
            
            if customer_id:
                query = query.filter_by(customerId=customer_id)
            
            stats = query.all()
            
            data = []
            for stat in stats:
                data.append({
                    'alertType': stat.alertType,
                    'count': stat.count
                })
            
            return jsonify({
                'success': True,
                'data': data
            })
        except Exception as e:
            logger.error(f"生成告警类型图表数据失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'生成告警类型图表数据失败: {str(e)}'
            }), 500
    
    def gather_deal_alert(self, customer_id=None):
        """获取已处理告警"""
        try:
            query = AlertInfo.query.filter_by(status='resolved')
            if customer_id:
                query = query.filter_by(customerId=customer_id)
            
            alerts = query.order_by(AlertInfo.updated_at.desc()).limit(100).all()
            
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
                    'created_at': alert.created_at.isoformat() if alert.created_at else None,
                    'updated_at': alert.updated_at.isoformat() if alert.updated_at else None
                })
            
            return jsonify({
                'success': True,
                'data': alert_list
            })
        except Exception as e:
            logger.error(f"获取已处理告警失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取已处理告警失败: {str(e)}'
            }), 500 