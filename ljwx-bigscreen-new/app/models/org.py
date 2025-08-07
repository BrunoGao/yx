#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组织相关模型
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Boolean, SmallInteger
from ..extensions import db

class OrgInfo(db.Model):
    """组织信息表"""
    __tablename__ = 'sys_org_units'
    __table_args__ = {'comment': '组织/部门/子部门管理'}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键')
    parent_id = db.Column(db.BigInteger, nullable=True, comment='父组织/部门/子部门ID')
    name = db.Column(db.String(200), nullable=False, comment='组织/部门/子部门名称')
    code = db.Column(db.String(100), nullable=True, comment='组织/部门/子部门编码')
    abbr = db.Column(db.String(50), nullable=True, comment='组织/部门/子部门名称简写')
    level = db.Column(db.Integer, default=0, nullable=False, comment='组织/部门/子部门层级')
    ancestors = db.Column(db.String(500), nullable=False, comment='祖先节点')
    description = db.Column(db.String(500), nullable=True, comment='组织/部门/子部门描述')
    sort = db.Column(db.Integer, default=999, nullable=True, comment='排序值')
    create_user = db.Column(db.String(64), nullable=False, comment='创建用户')
    create_user_id = db.Column(db.BigInteger, nullable=False, comment='创建用户ID')
    create_time = db.Column(db.DateTime, nullable=False, comment='创建时间')
    update_user = db.Column(db.String(64), nullable=True, comment='修改用户')
    update_user_id = db.Column(db.BigInteger, nullable=True, comment='修改用户ID')
    update_time = db.Column(db.DateTime, nullable=True, comment='修改时间')
    status = db.Column(db.String(2), default='1', nullable=True, comment='是否启用(0:禁用,1:启用)')
    is_deleted = db.Column(db.Boolean, default=False, nullable=True, comment='是否删除(0:否,1:是)')

class Position(db.Model):
    """岗位信息表"""
    __tablename__ = 'sys_position'
    __table_args__ = {'schema': 'lj-06', 'comment': '岗位管理'}

    id = db.Column(db.BigInteger, primary_key=True, comment='主键')
    name = db.Column(db.String(200), nullable=False, comment='岗位名称')
    code = db.Column(db.String(100), comment='岗位编码')
    abbr = db.Column(db.String(50), comment='岗位名称简写')
    description = db.Column(db.String(500), comment='岗位描述')
    sort = db.Column(db.Integer, default=999, comment='排序值')
    status = db.Column(db.String(2), default='1', comment='是否启用(0:禁用,1:启用)')
    org_id = db.Column(db.BigInteger, comment='组织ID')
    risk_level = db.Column(db.String(20), default='normal', comment='岗位风险等级')
    is_deleted = db.Column(db.SmallInteger, default=0, comment='是否删除(0:否,1:是)')
    create_user = db.Column(db.String(64), nullable=False, comment='创建用户')
    create_user_id = db.Column(db.BigInteger, nullable=False, comment='创建用户ID')
    create_time = db.Column(db.DateTime, nullable=False, comment='创建时间')
    update_user = db.Column(db.String(64), comment='修改用户')
    update_user_id = db.Column(db.BigInteger, comment='修改用户ID')
    update_time = db.Column(db.DateTime, comment='修改时间') 