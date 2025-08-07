#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础模型文件
包含公共字段定义和工具函数
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from ..extensions import db

Base = declarative_base()

def datetime_to_str(dt):
    """Convert a datetime object to a string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None

class BaseModel(db.Model):
    """基础模型类，包含公共字段"""
    __abstract__ = True
    
    # 公共字段
    is_deleted = db.Column(db.Boolean, default=False, nullable=True, comment='是否删除')
    create_user = db.Column(db.String(255), nullable=True, comment='创建用户')
    create_user_id = db.Column(db.BigInteger, nullable=True, comment='创建用户ID')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True, comment='创建时间')
    update_user = db.Column(db.String(255), nullable=True, comment='修改用户')
    update_user_id = db.Column(db.BigInteger, nullable=True, comment='修改用户ID')
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment='修改时间')
    
    def to_dict(self):
        """转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = datetime_to_str(value)
            else:
                result[column.name] = value
        return result
    
    def save(self):
        """保存到数据库"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """软删除"""
        self.is_deleted = True
        return self.save() 