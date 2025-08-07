#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户相关模型
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Boolean, SmallInteger, ForeignKey, func
from ..extensions import db
from .base import BaseModel

class UserInfo(db.Model):
    """用户信息表"""
    __tablename__ = 'sys_user'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_card_number = db.Column(db.String(40), nullable=False, comment='用户卡号')
    working_years = db.Column(db.Integer, nullable=True, comment='工作年限')
    avatar = db.Column(db.String(200), nullable=True, comment='头像')
    user_name = db.Column(db.String(40), nullable=False, comment='用户名称')
    password = db.Column(db.String(100), nullable=False, comment='密码')
    nick_name = db.Column(db.String(20), nullable=True, comment='昵称')
    real_name = db.Column(db.String(20), nullable=False, comment='真实姓名')
    email = db.Column(db.String(45), nullable=False, comment='邮箱')
    phone = db.Column(db.String(45), nullable=True, comment='手机')
    gender = db.Column(db.String(2), default='0', comment='性别 0保密 1男 2女')
    create_user = db.Column(db.String(40), nullable=False, comment='创建用户')
    create_user_id = db.Column(db.BigInteger, nullable=False, comment='创建用户ID')
    create_time = db.Column(db.DateTime, nullable=False, comment='创建时间')
    update_user = db.Column(db.String(40), nullable=True, comment='修改用户')
    update_user_id = db.Column(db.BigInteger, nullable=True, comment='修改用户ID')
    update_time = db.Column(db.DateTime, nullable=True, comment='修改时间')
    salt = db.Column(db.String(6), nullable=True, comment='MD5的盐值')
    last_login_time = db.Column(db.DateTime, nullable=True, comment='最后登录时间')
    update_password_time = db.Column(db.DateTime, nullable=True, comment='修改密码时间')
    status = db.Column(db.String(2), default='1', comment='是否启用(0:禁用,1:启用)')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除(0:否,1:是)')
    device_sn = db.Column(db.String(50), nullable=True)
    customer_id = db.Column(db.BigInteger, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_card_number": self.user_card_number,
            "working_years": self.working_years,
            "avatar": self.avatar,
            "user_name": self.user_name,
            "nick_name": self.nick_name,
            "real_name": self.real_name,
            "email": self.email,
            "phone": self.phone,
            "gender": self.gender,
            "status": self.status,
            "device_sn": self.device_sn,
            "customer_id": self.customer_id,
            "create_time": datetime_to_str(self.create_time),
            "update_time": datetime_to_str(self.update_time),
            "last_login_time": datetime_to_str(self.last_login_time)
        }

    @staticmethod
    def generate_password():
        """生成随机密码"""
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    def verify_password(self, password):
        """验证密码"""
        import hashlib
        if self.salt:
            salted_password = password + self.salt
            return hashlib.md5(salted_password.encode()).hexdigest() == self.password
        return password == self.password

class UserOrg(db.Model):
    """用户组织关联表"""
    __tablename__ = 'sys_user_org'
    __table_args__ = {'comment': '用户组织/部门/子部门管理', 'extend_existing': True}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键')
    user_id = db.Column(db.BigInteger, nullable=True, comment='用户ID')
    org_id = db.Column(db.BigInteger, nullable=True, comment='组织/部门/子部门ID')
    principal = db.Column(db.String(2), default='0', nullable=True, comment='组织/部门/子部门负责人(0:否,1:是)')
    create_user = db.Column(db.String(64), nullable=False, comment='创建用户')
    create_user_id = db.Column(db.BigInteger, nullable=False, comment='创建用户ID')
    create_time = db.Column(db.DateTime, nullable=False, comment='创建时间')
    update_user = db.Column(db.String(64), nullable=True, comment='修改用户')
    update_user_id = db.Column(db.BigInteger, nullable=True, comment='修改用户ID')
    update_time = db.Column(db.DateTime, nullable=True, comment='修改时间')
    is_deleted = db.Column(db.Boolean, default=False, nullable=True, comment='是否删除(0:否,1:是)')

class UserPosition(db.Model):
    """用户岗位关联表"""
    __tablename__ = 'sys_user_position'
    __table_args__ = {'schema': 'lj-06', 'comment': '用户岗位管理', 'extend_existing': True}

    id = db.Column(db.BigInteger, primary_key=True, comment='主键')
    user_id = db.Column(db.BigInteger, ForeignKey('`lj-06`.sys_user.id'), comment='用户ID')
    position_id = db.Column(db.BigInteger, ForeignKey('`lj-06`.sys_position.id'), comment='岗位ID')
    is_deleted = db.Column(db.SmallInteger, default=0, comment='是否删除(0:否,1:是)')
    create_user = db.Column(db.String(64), nullable=False, comment='创建用户')
    create_user_id = db.Column(db.BigInteger, nullable=False, comment='创建用户ID')
    create_time = db.Column(db.DateTime, nullable=False, comment='创建时间')
    update_user = db.Column(db.String(64), comment='修改用户')
    update_user_id = db.Column(db.BigInteger, comment='修改用户ID')
    update_time = db.Column(db.DateTime, comment='修改时间')

def datetime_to_str(dt):
    """Convert a datetime object to a string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None 