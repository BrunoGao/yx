from flask import request, jsonify
from . import api_bp
from ..services.bigscreen_service import BigscreenService
from ..services.user_service import UserService
from ..services.device_service import DeviceService
from ..services.health_service import HealthService
from ..services.alert_service import AlertService
from ..services.message_service import MessageService
import logging

logger = logging.getLogger(__name__)

# 初始化服务
bigscreen_service = BigscreenService()
user_service = UserService()
device_service = DeviceService()
health_service = HealthService()
alert_service = AlertService()
message_service = MessageService()

# 大屏数据API接口
@api_bp.route('/tracks', methods=['GET'])
def get_tracks():
    """获取轨迹数据"""
    try:
        result = bigscreen_service.get_tracks_data()
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取轨迹数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/devices', methods=['GET'])
def get_devices():
    """获取设备列表"""
    try:
        customer_id = request.args.get('customerId')
        result = device_service.get_devices_by_customer_id(customer_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取设备列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/devices/analysis', methods=['GET'])
def get_device_analysis():
    """获取设备分析数据"""
    try:
        customer_id = request.args.get('customerId')
        time_range = request.args.get('timeRange', '7d')
        result = bigscreen_service.get_device_analysis(customer_id, time_range)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取设备分析数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/statistics/overview', methods=['GET'])
def get_statistics_overview():
    """获取统计概览"""
    try:
        customer_id = request.args.get('customerId')
        result = bigscreen_service.get_total_info(customer_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取统计概览失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/health/stats', methods=['GET'])
def get_health_stats():
    """获取健康数据统计"""
    try:
        result = bigscreen_service.get_health_stats()
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取健康数据统计失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/alert/stats', methods=['GET'])
def get_alert_stats():
    """获取告警统计"""
    try:
        customer_id = request.args.get('customerId')
        result = bigscreen_service.get_alert_stats(customer_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取告警统计失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/message/stats', methods=['GET'])
def get_message_stats():
    """获取消息统计"""
    try:
        customer_id = request.args.get('customerId')
        result = bigscreen_service.get_message_stats(customer_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取消息统计失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 用户相关API
@api_bp.route('/user/info', methods=['GET'])
def get_user_info():
    """获取用户信息"""
    try:
        deviceSn = request.args.get('deviceSn')
        result = user_service.get_user_info(deviceSn)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/user/deviceSn', methods=['GET'])
def get_user_deviceSn():
    """根据手机号获取设备序列号"""
    try:
        phone = request.args.get('phone')
        result = user_service.get_user_deviceSn(phone)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取用户设备序列号失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/user/id', methods=['GET'])
def get_user_id():
    """根据手机号获取用户ID"""
    try:
        phone = request.args.get('phone')
        result = user_service.get_user_id(phone)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取用户ID失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/users/all', methods=['GET'])
def get_all_users():
    """获取所有用户"""
    try:
        result = user_service.get_all_users()
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取所有用户失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/user/personal/info', methods=['GET'])
def get_personal_user_info():
    """获取个人用户信息"""
    try:
        deviceSn = request.args.get('deviceSn')
        result = user_service.get_personal_user_info(deviceSn)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取个人用户信息失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 设备相关API
@api_bp.route('/device/info', methods=['GET'])
def get_device_info():
    """获取设备信息"""
    try:
        serial_number = request.args.get('serial_number')
        result = device_service.get_device_info(serial_number)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取设备信息失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/device/gather', methods=['GET'])
def gather_device_info():
    """收集设备信息"""
    try:
        customer_id = request.args.get('customer_id')
        result = device_service.gather_device_info(customer_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"收集设备信息失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/device/customer_id', methods=['GET'])
def get_customer_id_by_deviceSn():
    """根据设备序列号获取客户ID"""
    try:
        deviceSn = request.args.get('deviceSn')
        result = device_service.get_customer_id_by_deviceSn(deviceSn)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取客户ID失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 健康数据相关API
@api_bp.route('/health/data', methods=['GET'])
def get_health_data():
    """获取健康数据"""
    try:
        deviceSn = request.args.get('deviceSn')
        date = request.args.get('date')
        result = health_service.get_health_data(deviceSn, date)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取健康数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/health/data/by_id', methods=['GET'])
def get_health_data_by_id():
    """根据ID获取健康数据"""
    try:
        id = request.args.get('id')
        result = health_service.get_health_data_by_id(id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"根据ID获取健康数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/health/data/locations', methods=['GET'])
def get_user_locations():
    """获取用户位置信息"""
    try:
        deviceSn = request.args.get('deviceSn')
        date_str = request.args.get('date_str')
        result = health_service.get_user_locations(deviceSn, date_str)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取用户位置信息失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/health/data/score', methods=['GET'])
def get_health_data_score():
    """获取健康评分"""
    try:
        deviceSn = request.args.get('deviceSn')
        result = health_service.get_health_data_score(deviceSn)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取健康评分失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/health/data/trends', methods=['GET'])
def get_health_data_trends():
    """获取健康趋势"""
    try:
        deviceSn = request.args.get('deviceSn')
        result = health_service.get_health_data_trends(deviceSn)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取健康趋势失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/health/data/chart/baseline', methods=['GET'])
def get_health_data_chart_baseline():
    """获取健康基线图表"""
    try:
        deviceSn = request.args.get('deviceSn')
        result = health_service.get_health_data_chart_baseline(deviceSn)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取健康基线图表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/health/data/page', methods=['GET'])
def get_health_data_page():
    """获取健康数据分页"""
    try:
        deviceSn = request.args.get('deviceSn')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        result = health_service.get_health_data_page(deviceSn, page, per_page)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取健康数据分页失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 告警相关API
@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """获取告警列表"""
    try:
        deviceSn = request.args.get('deviceSn')
        customerId = request.args.get('customerId')
        result = alert_service.get_alerts(deviceSn, customerId)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取告警列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/alerts/upload', methods=['POST'])
def upload_alerts():
    """上传告警数据"""
    try:
        data = request.get_json()
        result = alert_service.upload_alerts(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"上传告警数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/alerts/deal', methods=['GET'])
def deal_alert():
    """处理告警"""
    try:
        alertId = request.args.get('alertId')
        result = alert_service.deal_alert(alertId)
        return jsonify(result)
    except Exception as e:
        logger.error(f"处理告警失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/alerts/batch_deal', methods=['POST'])
def batch_deal_alert():
    """批量处理告警"""
    try:
        data = request.get_json()
        result = alert_service.batch_deal_alert(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"批量处理告警失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/alerts/chart', methods=['GET'])
def generate_alert_chart():
    """生成告警图表"""
    try:
        result = alert_service.generate_alert_chart()
        return jsonify(result)
    except Exception as e:
        logger.error(f"生成告警图表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/alerts/json', methods=['GET'])
def generate_alert_json():
    """生成告警JSON数据"""
    try:
        customerId = request.args.get('customerId')
        userId = request.args.get('userId')
        severityLevel = request.args.get('severityLevel')
        result = alert_service.generate_alert_json(customerId, userId, severityLevel)
        return jsonify(result)
    except Exception as e:
        logger.error(f"生成告警JSON数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 消息相关API
@api_bp.route('/messages', methods=['GET'])
def get_messages():
    """获取消息列表"""
    try:
        deviceSn = request.args.get('deviceSn')
        messageType = request.args.get('messageType')
        customerId = request.args.get('customerId')
        result = message_service.get_messages(deviceSn, messageType, customerId)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取消息列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/messages/send', methods=['POST'])
def send_message():
    """发送消息"""
    try:
        data = request.get_json()
        result = message_service.send_message(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/messages/receive', methods=['GET'])
def receive_messages():
    """接收消息"""
    try:
        deviceSn = request.args.get('deviceSn')
        result = message_service.receive_messages(deviceSn)
        return jsonify(result)
    except Exception as e:
        logger.error(f"接收消息失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/messages/stats', methods=['GET'])
def get_message_stats():
    """获取消息统计"""
    try:
        result = message_service.get_message_stats()
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取消息统计失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 缓存状态API
@api_bp.route('/cache/status', methods=['GET'])
def get_cache_status():
    """获取缓存状态"""
    try:
        # 这里可以添加缓存状态检查逻辑
        return jsonify({
            'success': True,
            'data': {
                'redis_connected': True,
                'cache_hits': 0,
                'cache_misses': 0
            }
        })
    except Exception as e:
        logger.error(f"获取缓存状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 许可证检查API
@api_bp.route('/license/check', methods=['GET'])
def check_license():
    """检查许可证"""
    try:
        # 这里可以添加许可证检查逻辑
        return jsonify({
            'success': True,
            'data': {
                'valid': True,
                'expires_at': '2024-12-31'
            }
        })
    except Exception as e:
        logger.error(f"检查许可证失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500 