#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型模块
统一导入所有数据模型
"""

from ..extensions import db

# 导入所有模型类
from .user import UserInfo, UserOrg, UserPosition
from .device import DeviceInfo, DeviceInfoHistory, DeviceMessage, DeviceMessageDetail, DeviceUser, DeviceBindRequest
from .health import UserHealthData, UserHealthData, UserHealthDataDaily, UserHealthDataWeekly, HealthDataConfig
from .health import HealthBaseline, OrgHealthBaseline, HealthAnomaly, HealthSummaryDaily
from .alert import AlertInfo, AlertLog, AlertRules, UserAlert
from .system import SystemEventRule, EventAlarmQueue, WechatAlarmConfig, SystemLog

# 导出所有模型
__all__ = [
    'db',
    # 用户相关
    'UserInfo', 'UserOrg', 'UserPosition',
    # 设备相关
    'DeviceInfo', 'DeviceInfoHistory', 'DeviceMessage', 'DeviceMessageDetail', 'DeviceUser', 'DeviceBindRequest',
    # 健康数据相关
    'UserHealthData', 'UserHealthData', 'UserHealthDataDaily', 'UserHealthDataWeekly', 'HealthDataConfig',
    'HealthBaseline', 'OrgHealthBaseline', 'HealthAnomaly', 'HealthSummaryDaily',
    # 告警相关
    'AlertInfo', 'AlertLog', 'AlertRules', 'UserAlert',
    # 系统相关
    'SystemEventRule', 'EventAlarmQueue', 'WechatAlarmConfig', 'SystemLog'
] 