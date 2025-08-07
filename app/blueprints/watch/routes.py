from flask import request, jsonify
from . import watch_bp
from ..services.watch_service import WatchService
import logging

logger = logging.getLogger(__name__)

# 初始化Watch服务
watch_service = WatchService()

@watch_bp.route('/upload_health_data', methods=['POST'])
def upload_health_data():
    """上传健康数据 - 核心接口1"""
    try:
        health_data = request.get_json()
        logger.info(f"收到健康数据上传请求: {len(str(health_data)) if health_data else 0} 字符")
        return watch_service.upload_health_data(health_data)
    except Exception as e:
        logger.error(f"健康数据上传接口异常: {str(e)}")
        return jsonify({"status": "error", "message": f"接口异常: {str(e)}"}), 500

@watch_bp.route('/upload_device_info', methods=['POST'])
def upload_device_info():
    """上传设备信息 - 核心接口2"""
    try:
        device_info = request.get_json()
        logger.info(f"收到设备信息上传请求: {device_info.get('SerialNumber') if device_info else 'None'}")
        return watch_service.upload_device_info(device_info)
    except Exception as e:
        logger.error(f"设备信息上传接口异常: {str(e)}")
        return jsonify({"status": "error", "message": f"接口异常: {str(e)}"}), 500

@watch_bp.route('/upload_common_event', methods=['POST'])
def upload_common_event():
    """上传通用事件 - 核心接口3"""
    try:
        event_data = request.get_json()
        logger.info(f"收到通用事件上传请求: {event_data.get('eventType') if event_data else 'None'}")
        return watch_service.upload_common_event(event_data)
    except Exception as e:
        logger.error(f"通用事件上传接口异常: {str(e)}")
        return jsonify({"status": "error", "message": f"接口异常: {str(e)}"}), 500

@watch_bp.route('/DeviceMessage/send', methods=['POST'])
def send_device_message():
    """发送设备消息 - 核心接口4"""
    try:
        data = request.get_json()
        logger.info(f"收到设备消息发送请求: {data.get('deviceSn') if data else 'None'}")
        return watch_service.send_device_message(data)
    except Exception as e:
        logger.error(f"设备消息发送接口异常: {str(e)}")
        return jsonify({"success": False, "message": f"接口异常: {str(e)}"}), 500

@watch_bp.route('/DeviceMessage/receive', methods=['GET'])
def receive_device_messages():
    """接收设备消息 - 核心接口4"""
    try:
        device_sn = request.args.get('deviceSn')
        logger.info(f"收到设备消息查询请求: {device_sn}")
        return watch_service.receive_device_messages(device_sn)
    except Exception as e:
        logger.error(f"设备消息查询接口异常: {str(e)}")
        return jsonify({"success": False, "message": f"接口异常: {str(e)}"}), 500

@watch_bp.route('/DeviceMessage/save_message', methods=['POST'])
def save_device_message():
    """保存设备消息"""
    try:
        data = request.get_json()
        logger.info(f"收到设备消息保存请求: {data.get('deviceSn') if data else 'None'}")
        return watch_service.save_device_message(data)
    except Exception as e:
        logger.error(f"设备消息保存接口异常: {str(e)}")
        return jsonify({"success": False, "message": f"接口异常: {str(e)}"}), 500

@watch_bp.route('/fetch_health_data_config', methods=['GET'])
def fetch_health_data_config():
    """获取健康数据配置 - 核心接口5"""
    try:
        customer_id = request.args.get('customer_id')
        device_sn = request.args.get('deviceSn')
        logger.info(f"收到健康数据配置查询请求: customer_id={customer_id}, device_sn={device_sn}")
        return watch_service.fetch_health_data_config(customer_id, device_sn)
    except Exception as e:
        logger.error(f"健康数据配置查询接口异常: {str(e)}")
        return jsonify({"success": False, "message": f"接口异常: {str(e)}"}), 500

# 兼容性接口 - 保持原有路径
@watch_bp.route('/upload_health_data_optimized', methods=['POST'])
def upload_health_data_optimized():
    """优化版健康数据上传接口"""
    return upload_health_data()

@watch_bp.route('/optimizer_stats', methods=['GET'])
def get_optimizer_stats():
    """获取优化器统计信息"""
    try:
        return jsonify({
            "success": True,
            "data": {
                "total_uploads": 0,
                "success_rate": 100.0,
                "avg_processing_time": 0.1
            }
        })
    except Exception as e:
        logger.error(f"优化器统计接口异常: {str(e)}")
        return jsonify({"success": False, "message": f"接口异常: {str(e)}"}), 500 