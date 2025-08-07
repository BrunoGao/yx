#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备相关模型
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Boolean, Enum, Text, ForeignKey, func
from ..extensions import db

class DeviceInfo(db.Model):
    """设备信息表"""
    __tablename__ = 't_device_info'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    device_sn = db.Column(db.String(50), nullable=False, unique=True, comment='设备序列号')
    device_name = db.Column(db.String(100), nullable=True, comment='设备名称')
    device_type = db.Column(db.String(50), nullable=True, comment='设备类型')
    customer_id = db.Column(db.BigInteger, nullable=True, comment='客户ID')
    user_id = db.Column(db.BigInteger, nullable=True, comment='用户ID')
    org_id = db.Column(db.BigInteger, nullable=True, comment='组织ID')
    status = db.Column(db.String(20), default='online', comment='设备状态')
    battery_level = db.Column(db.Integer, nullable=True, comment='电池电量')
    firmware_version = db.Column(db.String(50), nullable=True, comment='固件版本')
    last_heartbeat = db.Column(db.DateTime, nullable=True, comment='最后心跳时间')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    create_user = db.Column(db.String(255), comment='创建用户')
    create_user_id = db.Column(db.BigInteger, comment='创建用户ID')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    update_user = db.Column(db.String(255), comment='更新用户')
    update_user_id = db.Column(db.BigInteger, comment='更新用户ID')
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        return {
            "id": self.id,
            "device_sn": self.device_sn,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "customer_id": self.customer_id,
            "user_id": self.user_id,
            "org_id": self.org_id,
            "status": self.status,
            "battery_level": self.battery_level,
            "firmware_version": self.firmware_version,
            "last_heartbeat": datetime_to_str(self.last_heartbeat),
            "is_deleted": self.is_deleted,
            "create_time": datetime_to_str(self.create_time),
            "update_time": datetime_to_str(self.update_time)
        }

class DeviceInfoHistory(db.Model):
    """设备信息历史表"""
    __tablename__ = 't_device_info_history'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    device_sn = db.Column(db.String(50), nullable=False, comment='设备序列号')
    timestamp = db.Column(db.DateTime, nullable=False, comment='记录时间')
    system_software_version = db.Column(db.String(50), nullable=True, comment='系统软件版本')
    battery_level = db.Column(db.Integer, nullable=True, comment='电池电量')
    wearable_status = db.Column(db.String(20), nullable=True, comment='佩戴状态')
    charging_status = db.Column(db.String(20), nullable=True, comment='充电状态')
    voltage = db.Column(db.Float, nullable=True, comment='电压')
    ip_address = db.Column(db.String(50), nullable=True, comment='IP地址')
    network_access_mode = db.Column(db.String(20), nullable=True, comment='网络接入模式')
    status = db.Column(db.String(20), nullable=True, comment='设备状态')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

class DeviceMessage(db.Model):
    """设备消息表"""
    __tablename__ = 't_device_message'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    device_sn = db.Column(db.String(50), nullable=False, comment='设备序列号')
    customer_id = db.Column(db.BigInteger, nullable=True, comment='客户ID')
    user_id = db.Column(db.BigInteger, nullable=True, comment='用户ID')
    org_id = db.Column(db.BigInteger, nullable=True, comment='组织ID')
    message = db.Column(db.Text, nullable=False, comment='消息内容')
    message_type = db.Column(db.String(50), nullable=True, comment='消息类型')
    sender_type = db.Column(db.String(50), nullable=True, comment='发送者类型')
    receiver_type = db.Column(db.String(50), nullable=True, comment='接收者类型')
    message_status = db.Column(db.String(20), default='pending', comment='消息状态')
    department_info = db.Column(db.String(500), nullable=True, comment='部门信息')
    sent_time = db.Column(db.DateTime, nullable=True, comment='发送时间')
    read_time = db.Column(db.DateTime, nullable=True, comment='阅读时间')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    create_user = db.Column(db.String(255), comment='创建用户')
    create_user_id = db.Column(db.BigInteger, comment='创建用户ID')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    update_user = db.Column(db.String(255), comment='更新用户')
    update_user_id = db.Column(db.BigInteger, comment='更新用户ID')
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

class DeviceMessageDetail(db.Model):
    """设备消息详情表"""
    __tablename__ = 't_device_message_detail'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    message_id = db.Column(db.BigInteger, nullable=False)
    device_sn = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), nullable=False)
    sender_type = db.Column(db.String(50), nullable=False)
    receiver_type = db.Column(db.String(50), nullable=False)
    message_status = db.Column(db.String(50), default='pending', nullable=False)
    sent_time = db.Column(db.DateTime, default=datetime.utcnow)
    received_time = db.Column(db.DateTime, nullable=True)
    create_user = db.Column(db.String(255), nullable=True)
    create_user_id = db.Column(db.BigInteger, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_user = db.Column(db.String(255), nullable=True)
    update_user_id = db.Column(db.BigInteger, nullable=True)
    update_time = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)

class DeviceUser(db.Model):
    """设备用户关联表"""
    __tablename__ = 't_device_user'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    device_sn = db.Column(db.String(200), nullable=False, comment='设备ID')
    user_id = db.Column(db.BigInteger, nullable=False, comment='用户ID')
    user_name = db.Column(db.String(50), nullable=True)
    operate_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True, comment='绑定时间')
    status = db.Column(db.Enum('BIND','UNBIND'), default='BIND', nullable=True, comment='绑定状态')
    is_deleted = db.Column(db.Boolean, default=False, nullable=True, comment='是否删除')
    create_user = db.Column(db.String(255), nullable=True, comment='创建用户')
    create_user_id = db.Column(db.BigInteger, nullable=True, comment='创建用户ID')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True, comment='创建时间')
    update_user = db.Column(db.String(255), nullable=True, comment='最后修改用户')
    update_user_id = db.Column(db.BigInteger, nullable=True, comment='最后修改用户ID')
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment='最后修改时间')
    
    __table_args__ = (
        db.Index('idx_device_user', 'device_sn', 'user_id'),
    )
    
    def save(self):
        """保存到数据库"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

class DeviceBindRequest(db.Model):
    """设备绑定申请表"""
    __tablename__ = 't_device_bind_request'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    device_sn = db.Column(db.String(100), nullable=False, comment='设备序列号')
    user_id = db.Column(db.BigInteger, nullable=False, comment='申请用户ID')
    org_id = db.Column(db.BigInteger, nullable=False, comment='申请组织ID')
    status = db.Column(db.Enum('PENDING', 'APPROVED', 'REJECTED'), default='PENDING', nullable=False, comment='申请状态')
    apply_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='申请时间')
    approve_time = db.Column(db.DateTime, nullable=True, comment='审批时间')
    approver_id = db.Column(db.BigInteger, nullable=True, comment='审批人ID')
    comment = db.Column(db.String(255), nullable=True, comment='审批备注')
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, comment='是否删除')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    
    __table_args__ = (
        db.Index('idx_device_bind_request', 'device_sn', 'user_id', 'status'),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "device_sn": self.device_sn,
            "user_id": self.user_id,
            "org_id": self.org_id,
            "status": self.status,
            "apply_time": datetime_to_str(self.apply_time),
            "approve_time": datetime_to_str(self.approve_time),
            "approver_id": self.approver_id,
            "comment": self.comment,
            "create_time": datetime_to_str(self.create_time),
            "update_time": datetime_to_str(self.update_time)
        }

def datetime_to_str(dt):
    """Convert a datetime object to a string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None 