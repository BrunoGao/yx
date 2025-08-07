#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统相关模型
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Boolean, Text, JSON, TIMESTAMP, func
from ..extensions import db

class Interface(db.Model):
    """接口配置表"""
    __tablename__ = 't_interface'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    call_interval = db.Column(db.Integer, nullable=False)
    method = db.Column(db.Enum('upload', 'fetch'), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    is_enabled = db.Column(db.Boolean, nullable=True)
    customer_id = db.Column(db.BigInteger, nullable=True)
    api_id = db.Column(db.String(50), nullable=True)
    api_auth = db.Column(db.String(200), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=True)
    create_user = db.Column(db.String(255), nullable=True)
    create_user_id = db.Column(db.BigInteger, nullable=True)
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), nullable=True)
    update_user = db.Column(db.String(255), nullable=True)
    update_user_id = db.Column(db.BigInteger, nullable=True)
    update_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=True)

class CustomerConfig(db.Model):
    """客户配置表"""
    __tablename__ = 't_customer_config'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    upload_method = db.Column(db.Enum('wifi', 'bluetooth'), default='wifi', nullable=True)
    license_key = db.Column(db.Integer, nullable=False)
    is_support_license = db.Column(db.Boolean, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=True)
    create_user = db.Column(db.String(255), nullable=True)
    create_user_id = db.Column(db.BigInteger, nullable=True)
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), nullable=True)
    update_user = db.Column(db.String(255), nullable=True)
    update_user_id = db.Column(db.BigInteger, nullable=True)
    update_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=True)
    os_version = db.Column(db.String(200), nullable=True)
    enable_resume = db.Column(db.Boolean, default=False, nullable=True)
    upload_retry_count = db.Column(db.Integer, default=3, nullable=True)
    cache_max_count = db.Column(db.Integer, default=100, nullable=True)
    upload_retry_interval = db.Column(db.Integer, default=5, nullable=True)

class SystemEventRule(db.Model):
    """系统事件规则表"""
    __tablename__ = 't_system_event_rules'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    rule_name = db.Column(db.String(100), nullable=False, comment='规则名称')
    event_type = db.Column(db.String(50), nullable=False, comment='事件类型')
    trigger_condition = db.Column(db.Text, nullable=True, comment='触发条件')
    alert_message = db.Column(db.Text, nullable=False, comment='告警消息')
    notification_type = db.Column(db.String(50), default='message', comment='通知类型')
    severity_level = db.Column(db.String(50), default='medium', comment='严重程度')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    create_user = db.Column(db.String(255), comment='创建用户')
    create_user_id = db.Column(db.BigInteger, comment='创建用户ID')
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), comment='创建时间')
    update_user = db.Column(db.String(255), comment='更新用户')
    update_user_id = db.Column(db.BigInteger, comment='更新用户ID')
    update_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp(), comment='更新时间')

class EventAlarmQueue(db.Model):
    """事件告警队列表"""
    __tablename__ = 't_event_alarm_queue'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String(50), nullable=False, comment='事件类型')
    device_sn = db.Column(db.String(50), nullable=False, comment='设备序列号')
    event_value = db.Column(db.String(500), nullable=True, comment='事件值')
    event_data = db.Column(db.JSON, nullable=True, comment='事件数据')
    processing_status = db.Column(db.String(20), default='pending', comment='处理状态')
    processing_time = db.Column(db.DateTime, nullable=True, comment='处理时间')
    error_message = db.Column(db.Text, nullable=True, comment='错误信息')
    retry_count = db.Column(db.Integer, default=0, comment='重试次数')
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), comment='创建时间')
    update_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp(), comment='更新时间')

class WechatAlarmConfig(db.Model):
    """微信告警配置表"""
    __tablename__ = 't_wechat_alarm_config'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    config_name = db.Column(db.String(100), nullable=False, comment='配置名称')
    config_type = db.Column(db.String(50), nullable=False, comment='配置类型')
    config_data = db.Column(db.JSON, nullable=True, comment='配置数据')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    create_user = db.Column(db.String(255), comment='创建用户')
    create_user_id = db.Column(db.BigInteger, comment='创建用户ID')
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), comment='创建时间')
    update_user = db.Column(db.String(255), comment='更新用户')
    update_user_id = db.Column(db.BigInteger, comment='更新用户ID')
    update_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp(), comment='更新时间')

class SystemLog(db.Model):
    """系统日志表"""
    __tablename__ = 't_system_logs'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    log_level = db.Column(db.String(20), nullable=False, comment='日志级别')
    log_message = db.Column(db.Text, nullable=False, comment='日志消息')
    log_source = db.Column(db.String(100), nullable=True, comment='日志来源')
    user_id = db.Column(db.BigInteger, nullable=True, comment='用户ID')
    device_sn = db.Column(db.String(50), nullable=True, comment='设备序列号')
    ip_address = db.Column(db.String(50), nullable=True, comment='IP地址')
    user_agent = db.Column(db.String(500), nullable=True, comment='用户代理')
    request_data = db.Column(db.JSON, nullable=True, comment='请求数据')
    response_data = db.Column(db.JSON, nullable=True, comment='响应数据')
    execution_time = db.Column(db.Float, nullable=True, comment='执行时间(毫秒)')
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp(), comment='创建时间')

def datetime_to_str(dt):
    """Convert a datetime object to a string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None 