#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
告警相关模型
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Boolean, Numeric, Text, ForeignKey, func
from ..extensions import db

class AlertInfo(db.Model):
    """告警信息表"""
    __tablename__ = 't_alert_info'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    rule_id = db.Column(db.BigInteger, db.ForeignKey('t_alert_rules.id'), nullable=False)
    alert_type = db.Column(db.String(100), nullable=False)
    device_sn = db.Column(db.String(20), nullable=False)
    alert_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    responded_time = db.Column(db.DateTime, nullable=True)
    alert_desc = db.Column(db.String(2000), nullable=True)
    severity_level = db.Column(db.String(50), default='medium', nullable=False)
    alert_status = db.Column(db.String(50), default='pending', nullable=True)
    assigned_user = db.Column(db.String(255), nullable=True)
    assigned_user_id = db.Column(db.BigInteger, nullable=True)
    org_id = db.Column(db.BigInteger, nullable=True, comment='组织ID')
    user_id = db.Column(db.BigInteger, nullable=True, comment='用户ID')
    is_deleted = db.Column(db.Boolean, default=False, nullable=True)
    create_user = db.Column(db.String(255), nullable=True)
    create_user_id = db.Column(db.BigInteger, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    update_user = db.Column(db.String(255), nullable=True)
    update_user_id = db.Column(db.BigInteger, nullable=True)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    latitude = db.Column(db.Numeric(12, 8), default=114.01508952, nullable=True)
    longitude = db.Column(db.Numeric(12, 8), default=22.54036796, nullable=True)
    altitude = db.Column(db.Numeric(10, 2), default=0.00, nullable=True)
    health_id = db.Column(db.BigInteger, nullable=True)

class AlertLog(db.Model):
    """告警操作日志表"""
    __tablename__ = 't_alert_action_log'
    __table_args__ = {'extend_existing': True}
    
    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, nullable=True)
    alert_id = db.Column(db.BigInteger, db.ForeignKey('t_alert_info.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    action_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    action_user = db.Column(db.String(255), nullable=True)
    action_user_id = db.Column(db.BigInteger, nullable=True)
    details = db.Column(db.Text, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=True)
    create_user = db.Column(db.String(255), nullable=True)
    create_user_id = db.Column(db.BigInteger, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    update_user = db.Column(db.String(255), nullable=True)
    update_user_id = db.Column(db.BigInteger, nullable=True)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    handled_via = db.Column(db.String(50), nullable=True, comment='处理途径（如微信、消息等）')
    result = db.Column(db.String(50), nullable=True, comment='处理结果（如成功、失败等）')

class AlertRules(db.Model):
    """告警规则表"""
    __tablename__ = 't_alert_rules'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    rule_type = db.Column(db.String(50), nullable=False)
    physical_sign = db.Column(db.String(50), nullable=True)
    threshold_min = db.Column(db.Numeric(10, 2), nullable=True)
    threshold_max = db.Column(db.Numeric(10, 2), nullable=True)
    deviation_percentage = db.Column(db.Numeric(5, 2), nullable=True)
    trend_duration = db.Column(db.Integer, nullable=True)
    parameters = db.Column(db.JSON, nullable=True)
    trigger_condition = db.Column(db.Text, nullable=True)
    alert_message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='message', nullable=True)
    severity_level = db.Column(db.String(50), default='medium', nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=True)
    create_user = db.Column(db.String(255), nullable=True)
    create_user_id = db.Column(db.BigInteger, nullable=True)
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), nullable=True)
    update_user = db.Column(db.String(255), nullable=True)
    update_user_id = db.Column(db.BigInteger, nullable=True)
    update_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "rule_type": self.rule_type,
            "physical_sign": self.physical_sign,
            "threshold_min": float(self.threshold_min) if self.threshold_min else None,
            "threshold_max": float(self.threshold_max) if self.threshold_max else None,
            "deviation_percentage": float(self.deviation_percentage) if self.deviation_percentage else None,
            "trend_duration": self.trend_duration,
            "parameters": self.parameters,
            "trigger_condition": self.trigger_condition,
            "alert_message": self.alert_message,
            "notification_type": self.notification_type,
            "severity_level": self.severity_level,
            "create_time": datetime_to_str(self.create_time),
            "update_time": datetime_to_str(self.update_time)
        }

class UserAlert(db.Model):
    """用户告警表"""
    __tablename__ = 't_user_alerts'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(64), nullable=False)
    phoneNumber = db.Column(db.String(20), nullable=False)
    alertType = db.Column(db.String(64), nullable=False)
    latitude = db.Column(db.Float, nullable=False, default=0.0)
    longitude = db.Column(db.Float, nullable=False, default=0.0)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deviceSn = db.Column(db.String(255), nullable=False)
    severityLevel = db.Column(db.String(255), nullable=False)
    alertStatus = db.Column(db.String(255), nullable=False)
    
    def __init__(self, userName, phoneNumber, alertType, latitude, longitude, timestamp, deviceSn, severityLevel, alertStatus):
        self.userName = userName
        self.phoneNumber = phoneNumber
        self.alertType = alertType
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.deviceSn = deviceSn
        self.severityLevel = severityLevel
        self.alertStatus = alertStatus

def datetime_to_str(dt):
    """Convert a datetime object to a string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None 