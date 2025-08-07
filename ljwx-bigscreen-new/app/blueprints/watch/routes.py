#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watch端接口路由
实现5个核心接口：upload_health_data、upload_device_info、upload_common_event、DeviceMessage相关接口、fetch_health_data_config
"""

from flask import Blueprint, request, jsonify, current_app
from ...services.watch_service import WatchService
from ...utils.decorators import log_api_request
import json
import logging

# 创建watch蓝图，不添加URL前缀以保持路径兼容
watch_bp = Blueprint('watch', __name__, url_prefix='/watch')

# 初始化服务
watch_service = WatchService()

logger = logging.getLogger(__name__)

@watch_bp.route("/upload_health_data", methods=['POST'])
@log_api_request('/upload_health_data','POST')
def handle_health_data():
    """健康数据上传接口"""
    try:
        health_data = request.get_json()
        logger.info(f"🏥 /upload_health_data 接口收到请求")
        logger.info(f"🏥 请求头: {dict(request.headers)}")
        logger.info(f"🏥 请求体大小: {len(str(health_data)) if health_data else 0} 字符")
        logger.info(f"🏥 原始JSON数据: {json.dumps(health_data, ensure_ascii=False, indent=2) if health_data else 'None'}")
        
        if not health_data:
            logger.error(f"❌ 请求体为空")
            return jsonify({"status": "error", "message": "请求体不能为空"}), 400
        
        # 修复data字段处理-支持数组和对象格式
        data_field = health_data.get('data', {})
        logger.info(f"🔍 data字段类型: {type(data_field)}, 内容: {data_field}")
        
        if isinstance(data_field, list) and len(data_field) > 0:
            # data是数组，取第一个元素获取deviceSn
            device_sn = data_field[0].get('deviceSn') or data_field[0].get('id')
            logger.info(f"🔍 从数组第一个元素提取device_sn: {device_sn}")
        elif isinstance(data_field, dict):
            # data是对象，直接获取deviceSn
            device_sn = data_field.get('deviceSn') or data_field.get('id')
            logger.info(f"🔍 从对象提取device_sn: {device_sn}")
        else:
            device_sn = None
            logger.warning(f"⚠️ 无法从data字段提取device_sn，data类型: {type(data_field)}")
        
        logger.info(f"🏥 最终提取的设备SN: {device_sn}")
        
        # 调用服务层处理
        result = watch_service.upload_health_data(health_data, device_sn)
        logger.info(f"🏥 upload_health_data处理结果: {result}")
        return result
        
    except Exception as e:
        logger.error(f"健康数据上传失败: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"处理失败: {str(e)}"}), 500

@watch_bp.route("/upload_device_info", methods=['POST'])
@log_api_request('/upload_device_info','POST')
def handle_device_info():
    """设备信息上传接口"""
    try:
        device_info = request.get_json()
        logger.info(f"📱 /upload_device_info 接口收到请求")
        logger.info(f"📱 请求头: {dict(request.headers)}")
        logger.info(f"📱 请求体大小: {len(str(device_info)) if device_info else 0} 字符")
        logger.info(f"📱 原始JSON数据: {json.dumps(device_info, ensure_ascii=False, indent=2) if device_info else 'None'}")
        
        if not device_info:
            logger.error(f"❌ 请求体为空")
            return jsonify({"status": "error", "message": "请求体不能为空"}), 400
            
        device_sn = device_info.get('SerialNumber') or device_info.get('serial_number') or device_info.get('deviceSn')
        logger.info(f"📱 提取的设备SN: {device_sn}")
        
        # 调用服务层处理
        result = watch_service.upload_device_info(device_info, device_sn)
        logger.info(f"📱 upload_device_info处理结果: {result}")
        return result
        
    except Exception as e:
        logger.error(f"设备信息上传失败: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"处理失败: {str(e)}"}), 500

@watch_bp.route('/upload_common_event', methods=['POST'])
@log_api_request('/upload_common_event','POST')
def upload_common_event():
    """通用事件上传接口"""
    try:
        event_data = request.get_json()
        logger.info(f"📡 /upload_common_event 接口收到请求")
        logger.info(f"📡 请求体大小: {len(str(event_data)) if event_data else 0} 字符")
        
        if not event_data:
            logger.error(f"❌ 请求体为空")
            return jsonify({"status": "error", "message": "请求体不能为空"}), 400
        
        # 调用服务层处理
        result = watch_service.upload_common_event(event_data)
        logger.info(f"📡 upload_common_event处理结果: {result}")
        return result
        
    except Exception as e:
        logger.error(f"通用事件上传失败: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"处理失败: {str(e)}"}), 500

@watch_bp.route('/DeviceMessage/save_message', methods=['POST'])
def save_message():
    """设备消息保存接口"""
    try:
        data = request.get_json()
        logger.info("💬 save_message::data", data)
        
        # 调用服务层处理
        result = watch_service.save_device_message(data)
        return result
        
    except Exception as e:
        logger.error(f"设备消息保存失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'发送消息失败: {str(e)}'
        }), 500

@watch_bp.route('/DeviceMessage/send', methods=['POST'])
@log_api_request('/DeviceMessage/send','POST')
def send_device_message():
    """设备消息发送接口"""
    try:
        data = request.get_json()
        logger.info('📤 设备消息发送', extra={
            'message_type': data.get('message_type'),
            'receiver_type': data.get('receiver_type'),
            'user_id': data.get('user_id'),
            'data_count': 1
        })
        
        # 调用服务层处理
        result = watch_service.send_device_message(data)
        return result
        
    except Exception as e:
        logger.error('设备消息发送失败', extra={'error': str(e)}, exc_info=True)
        raise

@watch_bp.route('/DeviceMessage/receive', methods=['GET'])
@log_api_request('/DeviceMessage/receive','GET')
def received_messages():
    """设备消息接收接口"""
    try:
        device_sn = request.args.get('deviceSn')
        logger.info('📥 设备消息查询', extra={'device_sn': device_sn})
        
        # 调用服务层处理
        result = watch_service.received_messages(device_sn)
        
        # 记录查询结果
        if hasattr(result, 'get_json'):
            result_data = result.get_json()
            if isinstance(result_data, dict) and 'data' in result_data:
                message_count = len(result_data['data']) if isinstance(result_data['data'], list) else 1
                logger.info('设备消息查询完成', extra={'device_sn': device_sn, 'message_count': message_count})
        
        return result
        
    except Exception as e:
        logger.error('设备消息查询失败', extra={'device_sn': device_sn, 'error': str(e)}, exc_info=True)
        raise

@watch_bp.route('/fetch_health_data_config', methods=['GET'])
@log_api_request('/fetch_health_data_config','GET')
def fetch_health_data_config():
    """健康数据配置获取接口"""
    try:
        customer_id = request.args.get('customer_id')
        device_sn = request.args.get('deviceSn')
        
        # 记录配置查询日志
        logger.info('健康数据配置查询', extra={
            'customer_id': customer_id,
            'device_sn': device_sn,
            'operation': 'FETCH_CONFIG'
        })
        
        # 调用服务层处理
        result = watch_service.fetch_health_data_config(customer_id, device_sn)
        
        # 记录查询结果
        if hasattr(result, 'get_json'):
            result_data = result.get_json()
            if isinstance(result_data, dict) and 'data' in result_data:
                config_count = len(result_data['data']) if isinstance(result_data['data'], list) else 1
                logger.info('健康数据配置查询完成', extra={
                    'customer_id': customer_id,
                    'device_sn': device_sn,
                    'config_count': config_count
                })
        
        return result
        
    except Exception as e:
        logger.error('健康数据配置查询失败', extra={
            'customer_id': customer_id,
            'device_sn': device_sn,
            'error': str(e)
        }, exc_info=True)
        raise 