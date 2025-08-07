#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信相关模型
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from ..extensions import db

class WeChatAlarmConfig(db.Model):
    """微信告警配置表(租户维度)"""
    __tablename__ = 't_wechat_alarm_config'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.BigInteger, nullable=False, comment='租户ID')
    type = db.Column(db.String(20), nullable=False, comment='微信类型: enterprise/official')
    corp_id = db.Column(db.String(100), nullable=True, comment='企业微信企业ID')
    agent_id = db.Column(db.String(50), nullable=True, comment='企业微信应用ID')
    secret = db.Column(db.String(100), nullable=True, comment='企业微信应用Secret')
    appid = db.Column(db.String(100), nullable=True, comment='微信公众号AppID')
    appsecret = db.Column(db.String(100), nullable=True, comment='微信公众号AppSecret')
    template_id = db.Column(db.String(100), nullable=True, comment='微信模板ID')
    enabled = db.Column(db.Boolean, default=True, nullable=False, comment='是否启用')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.Index('idx_tenant_type', 'tenant_id', 'type'),
        db.Index('idx_enabled', 'enabled'),
    ) 