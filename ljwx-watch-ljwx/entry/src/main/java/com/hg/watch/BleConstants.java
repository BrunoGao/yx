package com.hg.watch;

import java.util.UUID;

public interface BleConstants {
    // UUID常量
    UUID SERVICE_UUID = UUID.fromString("00001887-0000-1000-8000-00805f9b34fb");
    UUID DATA_CHAR_UUID = UUID.fromString("0000FD10-0000-1000-8000-00805F9B34FB");
    UUID CMD_CHAR_UUID = UUID.fromString("0000FD11-0000-1000-8000-00805F9B34FB");
    UUID CCCD_UUID = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");
    
    // 权限和属性常量
    int GATT_PERM = 16;
    int PROP_NOTIFY = 0x10;
    
    // 重试相关常量
    int MAX_RETRIES = 3;
    long RETRY_DELAY_MS = 100;
    
    // 数据类型常量
    String TYPE_HEALTH = "health";
    String TYPE_DEVICE = "device";
    String TYPE_COMMON_EVENT = "commonEvent";
    String TYPE_MESSAGE_RESPONSE = "message_response";
    String TYPE_MTU_NOTIFICATION = "mtu_notification";
    
    // 命令类型常量
    String CMD_MESSAGE = "message";
    String CMD_CONFIG = "config";
    String CMD_DISCONNECT = "disconnect";
    String CMD_MTU = "mtu";
    
    // 默认MTU大小
    int DEFAULT_MTU = 512;
    int MTU_OVERHEAD = 3;
} 