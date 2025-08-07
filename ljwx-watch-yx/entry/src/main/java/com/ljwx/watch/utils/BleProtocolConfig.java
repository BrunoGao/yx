package com.ljwx.watch.utils;

public class BleProtocolConfig {//BLE协议配置管理类
    public static final String CONFIG_KEY_USE_BINARY="use_binary_protocol";//是否使用二进制协议
    public static final String CONFIG_KEY_PROTOCOL_VERSION="protocol_version";//协议版本
    public static final String CONFIG_KEY_ENABLE_COMPRESSION="enable_compression";//是否启用压缩
    public static final String CONFIG_KEY_MAX_PACKET_SIZE="max_packet_size";//最大数据包大小
    
    private static final boolean DEFAULT_USE_BINARY=true;//默认启用二进制协议
    private static final int DEFAULT_PROTOCOL_VERSION=1;//默认协议版本
    private static final boolean DEFAULT_ENABLE_COMPRESSION=false;//默认不启用压缩
    private static final int DEFAULT_MAX_PACKET_SIZE=512;//默认最大包大小
    
    public static boolean shouldUseBinaryProtocol(){//是否应该使用二进制协议
        return DataManager.getInstance().getUseBinaryProtocol();
    }
    
    public static int getProtocolVersion(){//获取协议版本
        return DEFAULT_PROTOCOL_VERSION;
    }
    
    public static boolean isCompressionEnabled(){//是否启用压缩
        return DEFAULT_ENABLE_COMPRESSION;
    }
    
    public static int getMaxPacketSize(){//获取最大数据包大小
        return DEFAULT_MAX_PACKET_SIZE;
    }
    
    public static void enableBinaryProtocol(boolean enable){//启用或禁用二进制协议
        DataManager.getInstance().setUseBinaryProtocol(enable);
    }
} 