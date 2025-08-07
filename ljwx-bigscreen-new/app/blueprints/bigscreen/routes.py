#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大屏功能路由
使用模块化服务架构
"""

from flask import render_template, request, jsonify, current_app
from . import bigscreen_bp
from ...services import (
    UserService, AuthService,
    HealthDataUploadService, HealthDataAnalysisService, HealthDataCleanService,
    AlertService, DeviceService, MessageService, OrgService
)
from ...models import db, UserHealthData, DeviceInfo, DeviceMessage, AlertInfo, UserInfo
from datetime import datetime, timedelta
from sqlalchemy import func
import logging
import random

# 创建服务实例
user_service = UserService()
auth_service = AuthService()
health_upload_service = HealthDataUploadService()
health_analysis_service = HealthDataAnalysisService()
health_clean_service = HealthDataCleanService()
alert_service = AlertService()
device_service = DeviceService()
message_service = MessageService()
org_service = OrgService()

logger = logging.getLogger(__name__)

# 页面路由
@bigscreen_bp.route('/')
def index():
    """大屏首页"""
    return render_template('bigscreen/index.html')

@bigscreen_bp.route('/test')
def test():
    """测试页面"""
    return render_template('bigscreen/test.html')

@bigscreen_bp.route('/bigscreen_main')
def bigscreen_main():
    """大屏主页面"""
    return render_template('bigscreen/bigscreen_main.html')

@bigscreen_bp.route('/optimized')
def optimized():
    """优化页面"""
    return render_template('bigscreen/optimized.html')

@bigscreen_bp.route('/main')
def main():
    """主页面"""
    return render_template('bigscreen/main.html')

@bigscreen_bp.route('/personal')
def personal():
    """个人页面"""
    return render_template('bigscreen/personal.html')

@bigscreen_bp.route('/track_view')
def track_view():
    """轨迹视图页面"""
    return render_template('bigscreen/track_view.html')

@bigscreen_bp.route('/alert')
def alert_index():
    """告警页面"""
    return render_template('bigscreen/alert.html')

@bigscreen_bp.route('/message')
def message_index():
    """消息页面"""
    return render_template('bigscreen/message.html')

@bigscreen_bp.route('/chart')
def chart_index():
    """图表页面"""
    return render_template('bigscreen/chart.html')

@bigscreen_bp.route('/map')
def map_index():
    """地图页面"""
    return render_template('bigscreen/map.html')

@bigscreen_bp.route('/health_table')
def health_table():
    """健康数据表格页面"""
    return render_template('bigscreen/health_table.html')

@bigscreen_bp.route('/health_trends')
def health_trends():
    """健康趋势页面"""
    return render_template('bigscreen/health_trends.html')

@bigscreen_bp.route('/health_main')
def health_main():
    """健康主页面"""
    return render_template('bigscreen/health_main.html')

@bigscreen_bp.route('/health_baseline')
def health_baseline():
    """健康基线页面"""
    return render_template('bigscreen/health_baseline.html')

@bigscreen_bp.route('/user_health_data_analysis')
def user_health_data_analysis():
    """健康数据分析页面"""
    return render_template('bigscreen/user_health_data_analysis.html')

@bigscreen_bp.route('/health_profile')
def health_profile():
    """健康画像页面"""
    return render_template('bigscreen/health_profile.html')

@bigscreen_bp.route('/config_management')
def config_management():
    """配置管理页面"""
    return render_template('bigscreen/config_management.html')

@bigscreen_bp.route('/device_bind')
def device_bind():
    """设备绑定页面"""
    return render_template('bigscreen/device_bind.html')

@bigscreen_bp.route('/device_analysis')
def device_analysis():
    """设备分析页面"""
    return render_template('bigscreen/device_analysis.html')

@bigscreen_bp.route('/device_dashboard')
def device_dashboard():
    """设备监控大屏页面"""
    return render_template('bigscreen/device_dashboard.html')

@bigscreen_bp.route('/device_detailed_analysis')
def device_detailed_analysis():
    """设备详细分析页面"""
    return render_template('bigscreen/device_detailed_analysis.html')

@bigscreen_bp.route('/personal_3d')
def personal_3d():
    """3D人体模型页面"""
    return render_template('bigscreen/personal_3d.html')

@bigscreen_bp.route('/personal_advanced')
def personal_advanced():
    """高级3D人体模型页面"""
    return render_template('bigscreen/personal_advanced.html')

@bigscreen_bp.route('/system_event_alert')
def system_event_alert_page():
    """系统事件告警页面"""
    return render_template('bigscreen/system_event_alert.html')

# View页面路由
@bigscreen_bp.route('/alert_view')
def alert_view():
    """告警视图页面"""
    return render_template('bigscreen/alert_view.html')

@bigscreen_bp.route('/message_view')
def message_view():
    """消息视图页面"""
    return render_template('bigscreen/message_view.html')

@bigscreen_bp.route('/device_view')
def device_view():
    """设备视图页面"""
    return render_template('bigscreen/device_view.html')

@bigscreen_bp.route('/user_view')
def user_view():
    """用户视图页面"""
    return render_template('bigscreen/user_view.html')

@bigscreen_bp.route('/user_profile')
def user_profile():
    """用户画像页面"""
    return render_template('bigscreen/user_profile.html')

@bigscreen_bp.route('/health_view')
def health_view():
    """健康视图页面"""
    return render_template('bigscreen/health_view.html')

# API路由 - 用户相关
@bigscreen_bp.route('/getUserInfo', methods=['GET'])
def get_user_info():
    """获取用户信息"""
    device_sn = request.args.get('deviceSn')
    return user_service.get_user_info(device_sn)

@bigscreen_bp.route('/get_all_users', methods=['GET'])
def get_all_users():
    """获取所有用户"""
    return user_service.get_all_users()

@bigscreen_bp.route('/getUserDeviceSn', methods=['GET'])
def get_user_deviceSn():
    """根据手机号获取设备SN"""
    phone = request.args.get('phone')
    return user_service.get_user_device_sn(phone)

@bigscreen_bp.route('/getUserId', methods=['GET'])
def get_user_id():
    """根据手机号获取用户ID"""
    phone = request.args.get('phone')
    return user_service.get_user_id(phone)

@bigscreen_bp.route('/get_personal_info', methods=['GET'])
def get_personal_info():
    """获取个人信息"""
    device_sn = request.args.get('deviceSn')
    return user_service.get_personal_info(device_sn)

# API路由 - 认证相关
@bigscreen_bp.route('/checkLicense', methods=['GET'])
def check_license():
    """检查许可证"""
    return auth_service.check_license()

# API路由 - 健康数据相关
@bigscreen_bp.route('/fetch_health_data', methods=['GET'])
def fetch_health_data():
    """获取健康数据"""
    device_sn = request.args.get('deviceSn')
    return health_upload_service.fetch_health_data(device_sn)

@bigscreen_bp.route('/upload_health_data', methods=['POST'])
def handle_health_data():
    """处理健康数据上传"""
    try:
        data = request.get_json()
        return health_upload_service.upload_health_data(data)
    except Exception as e:
        logger.error(f"处理健康数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理健康数据失败: {str(e)}'
        }), 500

@bigscreen_bp.route('/generateHealthJson')
def generate_health_json():
    """生成健康数据JSON"""
    return health_analysis_service.generate_health_json()

@bigscreen_bp.route('/get_health_data', methods=['GET'])
def get_health_data():
    """获取健康数据"""
    device_sn = request.args.get('deviceSn')
    date = request.args.get('date')
    return health_upload_service.get_health_data(device_sn, date)

@bigscreen_bp.route('/fetch_health_data_config', methods=['GET'])
def fetch_health_data_config():
    """获取健康数据配置"""
    customer_id = request.args.get('customer_id')
    device_sn = request.args.get('deviceSn')
    return health_analysis_service.fetch_health_data_config(customer_id, device_sn)

@bigscreen_bp.route('/fetch_health_metrics', methods=['GET'])
def fetch_health_metrics():
    """获取健康指标"""
    return health_analysis_service.fetch_health_metrics()

@bigscreen_bp.route('/fetch_user_locations', methods=['GET'])
def fetch_user_locations():
    """获取用户位置信息"""
    device_sn = request.args.get('deviceSn')
    date_str = request.args.get('date_str')
    return health_clean_service.fetch_user_locations(device_sn, date_str)

# API路由 - 告警相关
@bigscreen_bp.route('/fetch_alerts', methods=['GET'])
def fetch_alerts():
    """获取告警数据"""
    device_sn = request.args.get('deviceSn')
    customer_id = request.args.get('customerId')
    return alert_service.fetch_alerts(device_sn, customer_id)

@bigscreen_bp.route('/generateAlertJson', methods=['GET'])
def generate_alert_json():
    """生成告警数据JSON"""
    customer_id = request.args.get('customerId')
    user_id = request.args.get('userId')
    severity_level = request.args.get('severityLevel')
    return alert_service.generate_alert_json(customer_id, user_id, severity_level)

@bigscreen_bp.route('/fetch_alertType_stats', methods=['GET'])
def fetch_alertType_stats():
    """获取告警类型统计"""
    return alert_service.fetch_alertType_stats()

@bigscreen_bp.route('/upload_alerts', methods=['POST'])
def upload_alerts():
    """上传告警数据"""
    try:
        data = request.get_json()
        return alert_service.upload_alerts(data)
    except Exception as e:
        logger.error(f"上传告警数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'上传告警数据失败: {str(e)}'
        }), 500

@bigscreen_bp.route('/upload_common_event', methods=['POST'])
def upload_common_event():
    """上传通用事件"""
    try:
        data = request.get_json()
        return alert_service.upload_common_event(data)
    except Exception as e:
        logger.error(f"上传通用事件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'上传通用事件失败: {str(e)}'
        }), 500

@bigscreen_bp.route('/test_wechat_alert', methods=['GET'])
def test_wechat_alert():
    """测试微信告警"""
    return alert_service.test_wechat_alert()

@bigscreen_bp.route('/generateAlertChart', methods=['GET'])
def generate_alert_chart():
    """生成告警图表数据"""
    return alert_service.generate_alert_chart()

@bigscreen_bp.route('/generateAlertTypeChart', methods=['GET'])
def generate_alert_type_chart():
    """生成告警类型图表数据"""
    customer_id = request.args.get('customerId')
    return alert_service.generate_alert_type_chart(customer_id)

@bigscreen_bp.route('/gatherDealAlert', methods=['GET'])
def gather_deal_alert():
    """获取已处理告警"""
    customer_id = request.args.get('customerId')
    return alert_service.gather_deal_alert(customer_id)

# API路由 - 设备相关
@bigscreen_bp.route('/fetch_device_info', methods=['GET'])
def fetch_device_info():
    """获取设备信息"""
    serial_number = request.args.get('serial_number')
    return device_service.fetch_device_info(serial_number)

@bigscreen_bp.route('/upload_device_info', methods=['POST'])
def handle_device_info():
    """处理设备信息上传"""
    try:
        data = request.get_json()
        return device_service.upload_device_info(data)
    except Exception as e:
        logger.error(f"处理设备信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理设备信息失败: {str(e)}'
        }), 500

@bigscreen_bp.route('/get_customer_id_by_deviceSn', methods=['GET'])
def get_customer_id_by_deviceSn():
    """根据设备SN获取客户ID"""
    device_sn = request.args.get('deviceSn')
    return device_service.get_customer_id_by_deviceSn(device_sn)

@bigscreen_bp.route('/gather_device_info', methods=['GET'])
def gather_device_info():
    """获取设备信息汇总"""
    customer_id = request.args.get('customer_id')
    return device_service.gather_device_info(customer_id)

# API路由 - 消息相关
@bigscreen_bp.route('/fetch_messages', methods=['GET'])
def fetch_messages():
    """获取消息数据"""
    device_sn = request.args.get('deviceSn')
    message_type = request.args.get('messageType')
    customer_id = request.args.get('customerId')
    return message_service.fetch_messages(device_sn, message_type, customer_id)

@bigscreen_bp.route('/DeviceMessage/save_message', methods=['POST'])
def save_message():
    """保存设备消息"""
    try:
        data = request.get_json()
        return message_service.save_device_message(data)
    except Exception as e:
        logger.error(f"保存设备消息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'保存设备消息失败: {str(e)}'
        }), 500

@bigscreen_bp.route('/DeviceMessage/send', methods=['POST'])
def send_device_message():
    """发送设备消息"""
    try:
        data = request.get_json()
        return message_service.send_device_message(data)
    except Exception as e:
        logger.error(f"发送设备消息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'发送设备消息失败: {str(e)}'
        }), 500

@bigscreen_bp.route('/DeviceMessage/receive', methods=['GET'])
def received_messages():
    """接收设备消息"""
    device_sn = request.args.get('deviceSn')
    return message_service.receive_device_messages(device_sn)

# API路由 - 组织相关
@bigscreen_bp.route('/get_total_info', methods=['GET'])
def get_total_info():
    """获取总览信息"""
    customer_id = request.args.get('customer_id')
    return org_service.get_total_info(customer_id)

@bigscreen_bp.route('/get_health_stats')
def get_health_stats():
    """获取健康统计"""
    return org_service.get_health_stats()

# API路由 - 轨迹相关
@bigscreen_bp.route('/api/tracks')
def get_tracks():
    """获取轨迹数据"""
    tracks = [
        {
            'name': '轨迹1',
            'color': '#00ff00',
            'coordinates': [
                [114.025246, 22.543721],
                [114.028293, 22.545632],
                [114.031876, 22.547891],
                [114.035234, 22.549012],
                [114.038765, 22.551234]
            ],
            'stats': {
                'distance': 5.2,
                'time': 45,
                'speed': 6.9
            }
        },
        {
            'name': '轨迹2',
            'color': '#ff00ff',
            'coordinates': [
                [114.027246, 22.541721],
                [114.029293, 22.543632],
                [114.032876, 22.545891],
                [114.036234, 22.547012],
                [114.039765, 22.549234]
            ],
            'stats': {
                'distance': 3.8,
                'time': 30,
                'speed': 7.6
            }
        }
    ]
    return jsonify(tracks)

@bigscreen_bp.route('/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'BigScreen服务运行正常'}) 