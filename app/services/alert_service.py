from flask import current_app
from ..models import db, AlertInfo
from sqlalchemy import and_, func
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AlertService:
    """告警服务层，处理告警相关的业务逻辑"""
    
    def __init__(self):
        self.db = db
    
    def get_alerts(self, deviceSn=None, customerId=None):
        """获取告警列表"""
        try:
            query = AlertInfo.query
            
            if deviceSn:
                query = query.filter_by(deviceSn=deviceSn)
            
            if customerId:
                query = query.filter_by(customerId=customerId)
            
            alerts = query.order_by(AlertInfo.created_at.desc()).all()
            
            return {
                'success': True,
                'data': [alert.to_dict() for alert in alerts]
            }
        except Exception as e:
            logger.error(f"获取告警列表失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def upload_alerts(self, data):
        """上传告警数据"""
        try:
            if isinstance(data, list):
                alerts = []
                for alert_data in data:
                    alert = AlertInfo(
                        deviceSn=alert_data.get('deviceSn'),
                        customerId=alert_data.get('customerId'),
                        alertType=alert_data.get('alertType'),
                        severityLevel=alert_data.get('severityLevel'),
                        message=alert_data.get('message'),
                        status=alert_data.get('status', 'pending')
                    )
                    alerts.append(alert)
                
                db.session.add_all(alerts)
                db.session.commit()
                
                return {
                    'success': True,
                    'message': f'成功上传 {len(alerts)} 条告警数据'
                }
            else:
                # 单条告警数据
                alert = AlertInfo(
                    deviceSn=data.get('deviceSn'),
                    customerId=data.get('customerId'),
                    alertType=data.get('alertType'),
                    severityLevel=data.get('severityLevel'),
                    message=data.get('message'),
                    status=data.get('status', 'pending')
                )
                
                db.session.add(alert)
                db.session.commit()
                
                return {
                    'success': True,
                    'message': '告警数据上传成功'
                }
        except Exception as e:
            db.session.rollback()
            logger.error(f"上传告警数据失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def deal_alert(self, alertId):
        """处理告警"""
        try:
            alert = AlertInfo.query.get(alertId)
            if not alert:
                return {
                    'success': False,
                    'message': '告警不存在'
                }
            
            alert.status = 'resolved'
            alert.resolved_at = datetime.now()
            db.session.commit()
            
            return {
                'success': True,
                'message': '告警处理成功'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"处理告警失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def batch_deal_alert(self, data):
        """批量处理告警"""
        try:
            alert_ids = data.get('alertIds', [])
            if not alert_ids:
                return {
                    'success': False,
                    'message': '没有提供告警ID'
                }
            
            # 批量更新告警状态
            AlertInfo.query.filter(AlertInfo.id.in_(alert_ids)).update({
                'status': 'resolved',
                'resolved_at': datetime.now()
            }, synchronize_session=False)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'成功处理 {len(alert_ids)} 条告警'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"批量处理告警失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def generate_alert_chart(self):
        """生成告警图表数据"""
        try:
            # 获取最近7天的告警统计
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            # 按日期统计告警数量
            daily_stats = db.session.query(
                func.date(AlertInfo.created_at).label('date'),
                func.count(AlertInfo.id).label('count')
            ).filter(
                and_(
                    AlertInfo.created_at >= start_date,
                    AlertInfo.created_at <= end_date
                )
            ).group_by(func.date(AlertInfo.created_at)).all()
            
            # 按严重程度统计
            severity_stats = db.session.query(
                AlertInfo.severityLevel,
                func.count(AlertInfo.id)
            ).group_by(AlertInfo.severityLevel).all()
            
            # 按类型统计
            type_stats = db.session.query(
                AlertInfo.alertType,
                func.count(AlertInfo.id)
            ).group_by(AlertInfo.alertType).all()
            
            return {
                'success': True,
                'data': {
                    'daily_stats': [{'date': str(s.date), 'count': s.count} for s in daily_stats],
                    'severity_stats': [{'level': s[0], 'count': s[1]} for s in severity_stats],
                    'type_stats': [{'type': t[0], 'count': t[1]} for t in type_stats]
                }
            }
        except Exception as e:
            logger.error(f"生成告警图表失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def generate_alert_json(self, customerId=None, userId=None, severityLevel=None):
        """生成告警JSON数据"""
        try:
            query = AlertInfo.query
            
            if customerId:
                query = query.filter_by(customerId=customerId)
            
            if userId:
                query = query.filter_by(userId=userId)
            
            if severityLevel:
                query = query.filter_by(severityLevel=severityLevel)
            
            alerts = query.order_by(AlertInfo.created_at.desc()).all()
            
            return {
                'success': True,
                'data': [alert.to_dict() for alert in alerts]
            }
        except Exception as e:
            logger.error(f"生成告警JSON数据失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_alerts_by_orgIdAndUserId(self, orgId, userId, severityLevel=None):
        """根据组织ID和用户ID获取告警"""
        try:
            query = AlertInfo.query.filter(
                and_(
                    AlertInfo.orgId == orgId,
                    AlertInfo.userId == userId
                )
            )
            
            if severityLevel:
                query = query.filter_by(severityLevel=severityLevel)
            
            alerts = query.order_by(AlertInfo.created_at.desc()).all()
            
            return {
                'success': True,
                'data': [alert.to_dict() for alert in alerts]
            }
        except Exception as e:
            logger.error(f"根据组织ID和用户ID获取告警失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_alert_stats_by_dimension(self, customerId, dimension='type'):
        """按维度获取告警统计"""
        try:
            if dimension == 'type':
                stats = db.session.query(
                    AlertInfo.alertType,
                    func.count(AlertInfo.id)
                ).filter_by(customerId=customerId).group_by(AlertInfo.alertType).all()
            elif dimension == 'severity':
                stats = db.session.query(
                    AlertInfo.severityLevel,
                    func.count(AlertInfo.id)
                ).filter_by(customerId=customerId).group_by(AlertInfo.severityLevel).all()
            elif dimension == 'status':
                stats = db.session.query(
                    AlertInfo.status,
                    func.count(AlertInfo.id)
                ).filter_by(customerId=customerId).group_by(AlertInfo.status).all()
            else:
                return {
                    'success': False,
                    'message': '不支持的统计维度'
                }
            
            return {
                'success': True,
                'data': [{'name': s[0], 'count': s[1]} for s in stats]
            }
        except Exception as e:
            logger.error(f"按维度获取告警统计失败: {e}")
            return {'success': False, 'message': str(e)} 