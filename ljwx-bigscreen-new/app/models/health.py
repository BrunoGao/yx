#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康数据相关模型
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Boolean, Numeric, Float, JSON, Date, DECIMAL, func
from ..extensions import db

class UserHealthData(db.Model):
    """用户健康数据表(旧版)"""
    __tablename__ = 't_user_health_data1'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    phone_number = db.Column(db.String(20), nullable=True)
    heart_rate = db.Column(db.Integer, nullable=True)
    pressure_high = db.Column(db.Integer, nullable=True)
    pressure_low = db.Column(db.Integer, nullable=True)
    blood_oxygen = db.Column(db.Integer, nullable=True)
    temperature = db.Column(db.Numeric(5, 2), nullable=True)
    step = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    user_name = db.Column(db.String(255), nullable=False, default='heguang')
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    device_sn = db.Column(db.String(255), nullable=False)
    distance = db.Column(db.Float, nullable=True)
    calorie = db.Column(db.Float, nullable=True)
    sleep_data = db.Column(db.String(2000), nullable=True)
    exercise_daily_data = db.Column(db.String(2000), nullable=True)
    exercise_week_data = db.Column(db.String(2000), nullable=True)
    scientific_sleep_data = db.Column(db.String(2000), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=True)
    create_user = db.Column(db.String(255), nullable=True)
    create_user_id = db.Column(db.BigInteger, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    update_user = db.Column(db.String(255), nullable=True)
    update_user_id = db.Column(db.BigInteger, nullable=True)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

class UserHealthData(db.Model):
    """用户健康数据表(新版)"""
    __tablename__ = 't_user_health_data'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    upload_method = db.Column(db.String(20), nullable=True)
    heart_rate = db.Column(db.Integer, nullable=True)
    pressure_high = db.Column(db.Integer, nullable=True)
    pressure_low = db.Column(db.Integer, nullable=True)
    blood_oxygen = db.Column(db.Integer, nullable=True)
    temperature = db.Column(db.Numeric(5, 2), nullable=True)
    stress = db.Column(db.Integer, nullable=True)
    step = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    latitude = db.Column(db.Numeric(10, 6), nullable=True)
    longitude = db.Column(db.Numeric(10, 6), nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    device_sn = db.Column(db.String(255), nullable=False)
    distance = db.Column(db.Float, nullable=True)
    calorie = db.Column(db.Float, nullable=True)
    sleep = db.Column(db.Float, nullable=True, comment='睡眠时长(小时)，由sleepData计算得出')
    user_id = db.Column(db.BigInteger, nullable=True)
    org_id = db.Column(db.BigInteger, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    create_user = db.Column(db.String(255), nullable=True)
    create_user_id = db.Column(db.BigInteger, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_user = db.Column(db.String(255), nullable=True)
    update_user_id = db.Column(db.BigInteger, nullable=True)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 添加唯一约束防止重复插入
    __table_args__ = (
        db.Index('idx_device_timestamp', 'device_sn', 'timestamp'),
        db.Index('idx_user_timestamp', 'user_id', 'timestamp'),
        db.Index('idx_org_timestamp', 'org_id', 'timestamp'),
    )

class HealthDataConfig(db.Model):
    """健康数据配置表"""
    __tablename__ = 't_health_data_config'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.BigInteger, nullable=False)
    data_type = db.Column(db.String(50), nullable=False)
    frequency_interval = db.Column(db.Integer, nullable=True)
    is_realtime = db.Column(db.Boolean, default=True, nullable=True)
    is_enabled = db.Column(db.Boolean, default=True, nullable=True)
    is_default = db.Column(db.Boolean, default=False, nullable=True)
    warning_high = db.Column(db.Numeric(5, 1), nullable=True)
    warning_low = db.Column(db.Numeric(5, 1), nullable=True)
    warning_cnt = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Numeric(5, 4), nullable=True)

class HealthBaseline(db.Model):
    """健康基线表"""
    __tablename__ = 't_health_baseline'
    __table_args__ = {'extend_existing': True}
    
    baseline_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='基线记录主键')
    device_sn = db.Column(db.String(50), nullable=False, comment='设备序列号')
    user_id = db.Column(db.BigInteger, nullable=True, comment='用户ID')
    feature_name = db.Column(db.String(50), nullable=False, comment='体征名称，如 heart_rate/blood_oxygen')
    baseline_date = db.Column(db.Date, nullable=False, comment='基线日期')
    mean_value = db.Column(db.Float, comment='该期平均值')
    std_value = db.Column(db.Float, comment='该期标准差')
    min_value = db.Column(db.Float, comment='该期最小值')
    max_value = db.Column(db.Float, comment='该期最大值')
    sample_count = db.Column(db.Integer, default=0, comment='样本数量')
    is_current = db.Column(db.Boolean, nullable=False, comment='是否当前有效基线(1=是,0=否)')
    create_user = db.Column(db.String(255), comment='创建人')
    create_user_id = db.Column(db.BigInteger, comment='创建人ID')
    create_time = db.Column(db.DateTime, nullable=False, server_default=func.now(), comment='记录创建时间')
    update_user = db.Column(db.String(255), comment='最后修改人')
    update_user_id = db.Column(db.BigInteger, comment='最后修改人ID')
    update_time = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='记录更新时间')
    baseline_time = db.Column(db.DateTime, nullable=False, comment='基线生成时戳')
    
    __table_args__ = (
        db.Index('idx_device_feature_date', 'device_sn', 'feature_name', 'baseline_date'),
        db.Index('idx_user_feature_date', 'user_id', 'feature_name', 'baseline_date'),
        db.Index('idx_current_baseline', 'device_sn', 'feature_name', 'is_current'),
    )
    
    def to_dict(self):
        return {
            "baseline_id": self.baseline_id,
            "device_sn": self.device_sn,
            "user_id": self.user_id,
            "feature_name": self.feature_name,
            "baseline_date": self.baseline_date.strftime("%Y-%m-%d") if self.baseline_date else None,
            "mean_value": float(self.mean_value) if self.mean_value else None,
            "std_value": float(self.std_value) if self.std_value else None,
            "min_value": float(self.min_value) if self.min_value else None,
            "max_value": float(self.max_value) if self.max_value else None,
            "sample_count": self.sample_count,
            "is_current": self.is_current,
            "baseline_time": datetime_to_str(self.baseline_time),
            "create_time": datetime_to_str(self.create_time),
            "update_time": datetime_to_str(self.update_time)
        }

class OrgHealthBaseline(db.Model):
    """组织级健康基线模型"""
    __tablename__ = 't_org_health_baseline'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键')
    org_id = db.Column(db.BigInteger, nullable=False, comment='组织ID')
    feature_name = db.Column(db.String(50), nullable=False, comment='体征名称')
    baseline_date = db.Column(db.Date, nullable=False, comment='基线日期')
    mean_value = db.Column(db.Float, comment='组织平均值')
    std_value = db.Column(db.Float, comment='组织标准差')
    min_value = db.Column(db.Float, comment='组织最小值')
    max_value = db.Column(db.Float, comment='组织最大值')
    user_count = db.Column(db.Integer, default=0, comment='参与用户数')
    sample_count = db.Column(db.Integer, default=0, comment='总样本数')
    create_time = db.Column(db.DateTime, nullable=False, server_default=func.now())
    update_time = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        db.Index('idx_org_feature_date', 'org_id', 'feature_name', 'baseline_date'),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "org_id": self.org_id,
            "feature_name": self.feature_name,
            "baseline_date": self.baseline_date.strftime("%Y-%m-%d") if self.baseline_date else None,
            "mean_value": float(self.mean_value) if self.mean_value else None,
            "std_value": float(self.std_value) if self.std_value else None,
            "min_value": float(self.min_value) if self.min_value else None,
            "max_value": float(self.max_value) if self.max_value else None,
            "user_count": self.user_count,
            "sample_count": self.sample_count,
            "create_time": datetime_to_str(self.create_time),
            "update_time": datetime_to_str(self.update_time)
        }

class HealthAnomaly(db.Model):
    """健康异常表"""
    __tablename__ = 't_health_anomaly'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    device_sn = db.Column(db.String(50), nullable=False)  # 工人编号
    timestamp = db.Column(db.DateTime, nullable=False)  # 数据上传时间
    feature_name = db.Column(db.String(50), nullable=False)  # 异常特征
    value = db.Column(db.Numeric(10, 2), nullable=True)  # 异常值
    anomaly_type = db.Column(db.String(50), nullable=True)  # 异常类型 (高于范围/低于范围/其他)
    created_at = db.Column(db.TIMESTAMP, default=func.current_timestamp(), nullable=False)

class HealthSummaryDaily(db.Model):
    """健康数据每日汇总表"""
    __tablename__ = 't_health_summary_daily'
    __table_args__ = {'extend_existing': True}
    
    summary_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='汇总记录主键')
    device_sn = db.Column(db.String(50), nullable=False, comment='设备序列号')
    summary_date = db.Column(db.Date, nullable=False, comment='汇总日期')
    health_score = db.Column(db.DECIMAL(5,2), nullable=False, comment='综合健康得分（0–100）')
    create_time = db.Column(db.DateTime, nullable=False, default=func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment='更新时间')
    heart_rate_score = db.Column(db.DECIMAL(5,2), comment='心率得分')
    blood_oxygen_score = db.Column(db.DECIMAL(5,2), comment='血氧得分')
    temperature_score = db.Column(db.DECIMAL(5,2), comment='体温得分')
    blood_pressure_score = db.Column(db.DECIMAL(5,2), comment='血压得分')
    stress_score = db.Column(db.DECIMAL(5,2), comment='压力得分')
    sleep_data_score = db.Column(db.DECIMAL(5,2), comment='睡眠得分')
    step_score = db.Column(db.DECIMAL(5,2), comment='步数得分')
    distance_score = db.Column(db.DECIMAL(5,2), comment='距离得分')
    calorie_score = db.Column(db.DECIMAL(5,2), comment='卡路里得分')
    
    __table_args__ = (
        db.Index('idx_device_date', 'device_sn', 'summary_date'),
    )
    
    def to_dict(self):
        return {
            "summary_id": self.summary_id,
            "device_sn": self.device_sn,
            "summary_date": self.summary_date.strftime("%Y-%m-%d") if self.summary_date else None,
            "health_score": float(self.health_score) if self.health_score else None,
            "heart_rate_score": float(self.heart_rate_score) if self.heart_rate_score else None,
            "blood_oxygen_score": float(self.blood_oxygen_score) if self.blood_oxygen_score else None,
            "temperature_score": float(self.temperature_score) if self.temperature_score else None,
            "blood_pressure_score": float(self.blood_pressure_score) if self.blood_pressure_score else None,
            "stress_score": float(self.stress_score) if self.stress_score else None,
            "sleep_data_score": float(self.sleep_data_score) if self.sleep_data_score else None,
            "step_score": float(self.step_score) if self.step_score else None,
            "distance_score": float(self.distance_score) if self.distance_score else None,
            "calorie_score": float(self.calorie_score) if self.calorie_score else None,
            "create_time": datetime_to_str(self.create_time),
            "update_time": datetime_to_str(self.update_time)
        }

class UserHealthDataDaily(db.Model):
    """每日更新健康数据表"""
    __tablename__ = 't_user_health_data_daily'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    device_sn = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.BigInteger, nullable=True)
    org_id = db.Column(db.BigInteger, nullable=True)
    date = db.Column(db.Date, nullable=False)
    sleep_data = db.Column(db.JSON, nullable=True, comment='睡眠数据(每日更新)')
    exercise_daily_data = db.Column(db.JSON, nullable=True, comment='每日运动数据')
    workout_data = db.Column(db.JSON, nullable=True, comment='锻炼数据')
    scientific_sleep_data = db.Column(db.JSON, nullable=True, comment='科学睡眠数据')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.Index('idx_device_date_daily', 'device_sn', 'date'),
        db.Index('idx_user_date_daily', 'user_id', 'date'),
    )

class UserHealthDataWeekly(db.Model):
    """每周更新健康数据表"""
    __tablename__ = 't_user_health_data_weekly'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    device_sn = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.BigInteger, nullable=True)
    org_id = db.Column(db.BigInteger, nullable=True)
    week_start = db.Column(db.Date, nullable=False, comment='周开始日期(周一)')
    exercise_week_data = db.Column(db.JSON, nullable=True, comment='每周运动数据')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.Index('idx_device_week', 'device_sn', 'week_start'),
        db.Index('idx_user_week', 'user_id', 'week_start'),
    )

def datetime_to_str(dt):
    """Convert a datetime object to a string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None 