package com.hg.watch.utils;

import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import com.hg.watch.BleConstants;
import org.json.JSONObject;
import org.json.JSONException;
import java.util.*;
import java.util.concurrent.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

/**
 * 蓝牙数据处理器，负责数据发送和接收#高效处理设备和健康数据传输
 */
public class BleDataProcessor {
    private static final HiLogLabel LABEL = new HiLogLabel(3, 0xD001100, "ljwx");
    
    // 默认MTU大小
    private static final int DEFAULT_MTU = BleConstants.DEFAULT_MTU;
    
    // 发送延迟(毫秒)
    private static final int SEND_DELAY = 30;
    
    // 单例实例
    private static BleDataProcessor instance;
    
    // 接收缓存 - 存储分片数据
    private Map<Byte, Map<Byte, Map<Byte, byte[]>>> receiveBuffer = new ConcurrentHashMap<>();
    
    // 合并超时(毫秒)
    private static final long MERGE_TIMEOUT = 10000;
    
    // 缓存清理器
    private ScheduledExecutorService cleanupService;
    
    // 当前MTU
    private int mtu = DEFAULT_MTU;
    
    /**
     * 私有构造函数
     */
    private BleDataProcessor() {
        // 启动缓存清理定时任务
        cleanupService = Executors.newSingleThreadScheduledExecutor();
        cleanupService.scheduleAtFixedRate(this::cleanupBuffer, 30, 30, TimeUnit.SECONDS);
    }
    
    /**
     * 获取单例实例
     */
    public static synchronized BleDataProcessor getInstance() {
        if (instance == null) {
            instance = new BleDataProcessor();
        }
        return instance;
    }
    
    /**
     * 更新MTU大小
     */
    public void updateMtu(int newMtu) {
        this.mtu = Math.max(DEFAULT_MTU, newMtu);
        HiLog.info(LABEL, "BleDataProcessor MTU更新为: " + this.mtu);
    }
    
    /**
     * 发送设备信息
     * @param deviceInfo 设备信息JSON对象
     * @param sender 发送回调接口
     * @return 是否成功启动发送
     */
    public boolean sendDeviceInfo(JSONObject deviceInfo, DataSender sender) {
        try {
            if (deviceInfo == null || sender == null) {
                return false;
            }
            
            HiLog.info(LABEL, "发送设备信息: 序列号=" + deviceInfo.optString("SerialNumber", "未知"));
            
            // 编码设备信息
            List<byte[]> packets = BleDataProtocol.encodeDeviceInfo(deviceInfo, mtu);
            if (packets.isEmpty()) {
                HiLog.error(LABEL, "设备信息编码失败");
                return false;
            }
            
            HiLog.info(LABEL, "设备信息已分为" + packets.size() + "个包");
            
            // 异步发送
            new Thread(() -> {
                for (int i = 0; i < packets.size(); i++) {
                    byte[] packet = packets.get(i);
                    boolean success = sender.send(packet);
                    
                    if (!success) {
                        HiLog.error(LABEL, "设备信息包[" + (i+1) + "/" + packets.size() + "]发送失败");
                        return;
                    }
                    
                    HiLog.debug(LABEL, "设备信息包[" + (i+1) + "/" + packets.size() + "]发送成功, 大小=" + packet.length);
                    
                    try {
                        Thread.sleep(SEND_DELAY);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        return;
                    }
                }
                
                HiLog.info(LABEL, "设备信息发送完成");
            }).start();
            
            return true;
        } catch (Exception e) {
            HiLog.error(LABEL, "发送设备信息错误: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * 发送健康数据
     * @param healthData 健康数据JSON对象
     * @param sender 发送回调接口
     * @return 是否成功启动发送
     */
    public boolean sendHealthData(JSONObject healthData, DataSender sender) {
        try {
            if (healthData == null || sender == null) {
                return false;
            }
            
            HiLog.info(LABEL, "发送健康数据开始");
            
            // 编码健康数据
            Map<Byte, List<byte[]>> dataMap = BleDataProtocol.encodeHealthData(healthData, mtu);
            if (dataMap.isEmpty()) {
                HiLog.error(LABEL, "健康数据编码失败");
                return false;
            }
            
            // 计算总包数
            int totalPackets = 0;
            for (List<byte[]> packets : dataMap.values()) {
                totalPackets += packets.size();
            }
            
            HiLog.info(LABEL, "健康数据已分为" + totalPackets + "个数据包, " + dataMap.size() + "个数据类型");
            
            // 异步发送
            new Thread(() -> {
                // 先发送基础数据
                if (dataMap.containsKey(BleDataProtocol.TYPE_HEALTH_META)) {
                    sendPackets(BleDataProtocol.TYPE_HEALTH_META, dataMap.get(BleDataProtocol.TYPE_HEALTH_META), sender);
                }
                
                // 再发送其他类型
                for (Map.Entry<Byte, List<byte[]>> entry : dataMap.entrySet()) {
                    byte type = entry.getKey();
                    if (type != BleDataProtocol.TYPE_HEALTH_META) {
                        sendPackets(type, entry.getValue(), sender);
                    }
                }
                
                HiLog.info(LABEL, "健康数据发送完成");
            }).start();
            
            return true;
        } catch (Exception e) {
            HiLog.error(LABEL, "发送健康数据错误: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * 发送事件数据
     * @param eventData 事件数据JSON对象
     * @param sender 发送回调接口
     * @return 是否成功启动发送
     */
    public boolean sendEventData(JSONObject eventData, DataSender sender) {
        try {
            if (eventData == null || sender == null) {
                return false;
            }
            
            HiLog.info(LABEL, "发送事件数据: " + eventData.optString("action", "未知"));
            
            // 编码事件数据
            List<byte[]> packets = BleDataProtocol.encodeEventData(eventData, mtu);
            if (packets.isEmpty()) {
                HiLog.error(LABEL, "事件数据编码失败");
                return false;
            }
            
            HiLog.info(LABEL, "事件数据已分为" + packets.size() + "个包");
            
            // 异步发送
            new Thread(() -> {
                sendPackets(BleDataProtocol.TYPE_EVENT, packets, sender);
                HiLog.info(LABEL, "事件数据发送完成");
            }).start();
            
            return true;
        } catch (Exception e) {
            HiLog.error(LABEL, "发送事件数据错误: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * 处理接收到的数据包
     * @param rawData 接收到的原始字节数组
     * @return 如果是完整数据包返回合并后的JSONObject，否则返回null
     */
    public JSONObject processReceivedData(byte[] rawData) {
        try {
            // 解码数据包
            BleDataProtocol.DataPacket packet = BleDataProtocol.decodePacket(rawData);
            if (packet == null) {
                return null; // 无效数据包
            }
            
            HiLog.debug(LABEL, "接收数据包: " + packet);
            
            // 添加到接收缓存
            addToReceiveBuffer(packet);
            
            // 检查是否可以合并
            byte type = packet.type;
            byte total = packet.total;
            
            // 针对当前类型，检查是否所有分片都已接收
            if (isPacketComplete(type, total)) {
                // 合并数据
                byte[] mergedData = mergePacketData(type, total);
                if (mergedData != null) {
                    // 清理已处理的数据包
                    cleanPackets(type, total);
                    
                    // 处理合并后的数据
                    return processDataByType(type, mergedData);
                }
            }
            
            // 返回null表示还需要更多数据包
            return null;
        } catch (Exception e) {
            HiLog.error(LABEL, "处理接收数据包错误: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * 根据数据类型处理合并后的数据
     */
    private JSONObject processDataByType(byte type, byte[] data) {
        try {
            // 对于健康数据、设备信息和事件数据，直接解析为JSON
            String jsonStr = new String(data, StandardCharsets.UTF_8);
            
            try {
                JSONObject jsonObj = new JSONObject(jsonStr);
                
                // 增加标记字段，帮助接收端识别数据类型
                jsonObj.put("__ble_data_type", getTypeName(type));
                
                HiLog.info(LABEL, "成功处理[" + getTypeName(type) + "]数据");
                return jsonObj;
            } catch (JSONException e) {
                HiLog.error(LABEL, "JSON解析错误: " + e.getMessage() + ", 原始数据: " + jsonStr);
                return null;
            }
        } catch (Exception e) {
            HiLog.error(LABEL, "处理数据错误: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * 获取健康数据类型名称
     */
    private String getHealthTypeName(byte type) {
        switch (type) {
            case BleDataProtocol.TYPE_HEALTH_META:
                return "health_meta";
            case BleDataProtocol.TYPE_HEALTH_SLEEP:
                return "health_sleep";
            case BleDataProtocol.TYPE_HEALTH_EXERCISE:
                return "health_exercise";
            case BleDataProtocol.TYPE_HEALTH_WORKOUT:
                return "health_workout";
            default:
                return "health_unknown";
        }
    }
    
    /**
     * 发送数据包列表
     */
    private void sendPackets(byte type, List<byte[]> packets, DataSender sender) {
        try {
            for (int i = 0; i < packets.size(); i++) {
                byte[] packet = packets.get(i);
                boolean success = sender.send(packet);
                
                if (!success) {
                    HiLog.error(LABEL, getTypeName(type) + "数据包[" + (i+1) + "/" + packets.size() + "]发送失败");
                    return;
                }
                
                HiLog.debug(LABEL, getTypeName(type) + "数据包[" + (i+1) + "/" + packets.size() + "]发送成功, 大小=" + packet.length);
                
                try {
                    Thread.sleep(SEND_DELAY);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        } catch (Exception e) {
            HiLog.error(LABEL, "发送数据包错误: " + e.getMessage());
        }
    }
    
    /**
     * 获取数据类型名称
     */
    private String getTypeName(byte type) {
        switch (type) {
            case BleDataProtocol.TYPE_DEVICE:
                return "device";
            case BleDataProtocol.TYPE_HEALTH_META:
                return "health";
            case BleDataProtocol.TYPE_HEALTH_SLEEP:
                return "health_sleep";
            case BleDataProtocol.TYPE_HEALTH_EXERCISE:
                return "health_exercise";
            case BleDataProtocol.TYPE_HEALTH_WORKOUT:
                return "health_workout";
            case BleDataProtocol.TYPE_EVENT:
                return "event";
            default:
                return "unknown";
        }
    }
    
    /**
     * 添加数据包到接收缓存
     */
    private synchronized void addToReceiveBuffer(BleDataProtocol.DataPacket packet) {
        byte type = packet.type;
        byte index = packet.index;
        byte total = packet.total;
        
        // 获取或创建类型缓存
        Map<Byte, Map<Byte, byte[]>> typeMap = receiveBuffer.computeIfAbsent(type, k -> new ConcurrentHashMap<>());
        
        // 获取或创建总数缓存
        Map<Byte, byte[]> totalMap = typeMap.computeIfAbsent(total, k -> new ConcurrentHashMap<>());
        
        // 存储数据
        totalMap.put(index, packet.data);
        
        // 更新时间戳
        // 使用一个特殊位置存储时间戳
        totalMap.put((byte)255, longToBytes(System.currentTimeMillis()));
    }
    
    /**
     * 检查指定类型和总数的数据包是否已全部接收
     */
    private synchronized boolean isPacketComplete(byte type, byte total) {
        Map<Byte, Map<Byte, byte[]>> typeMap = receiveBuffer.get(type);
        if (typeMap == null) {
            return false;
        }
        
        Map<Byte, byte[]> totalMap = typeMap.get(total);
        if (totalMap == null) {
            return false;
        }
        
        // 查找0到total-1的所有索引是否都存在
        for (byte i = 0; i < total; i++) {
            if (!totalMap.containsKey(i)) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * 合并数据包
     */
    private synchronized byte[] mergePacketData(byte type, byte total) {
        try {
            Map<Byte, Map<Byte, byte[]>> typeMap = receiveBuffer.get(type);
            if (typeMap == null) {
                return null;
            }
            
            Map<Byte, byte[]> totalMap = typeMap.get(total);
            if (totalMap == null) {
                return null;
            }
            
            // 计算总大小
            int totalSize = 0;
            for (byte i = 0; i < total; i++) {
                byte[] data = totalMap.get(i);
                if (data != null) {
                    totalSize += data.length;
                }
            }
            
            // 创建合并后的数据
            ByteBuffer buffer = ByteBuffer.allocate(totalSize);
            for (byte i = 0; i < total; i++) {
                byte[] data = totalMap.get(i);
                if (data != null) {
                    buffer.put(data);
                }
            }
            
            return buffer.array();
        } catch (Exception e) {
            HiLog.error(LABEL, "合并数据包错误: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * 清理已处理的数据包
     */
    private synchronized void cleanPackets(byte type, byte total) {
        Map<Byte, Map<Byte, byte[]>> typeMap = receiveBuffer.get(type);
        if (typeMap != null) {
            typeMap.remove(total);
            if (typeMap.isEmpty()) {
                receiveBuffer.remove(type);
            }
        }
    }
    
    /**
     * 清理过期的数据包
     */
    private void cleanupBuffer() {
        try {
            long now = System.currentTimeMillis();
            
            synchronized (this) {
                // 遍历所有类型
                Iterator<Map.Entry<Byte, Map<Byte, Map<Byte, byte[]>>>> typeIter = receiveBuffer.entrySet().iterator();
                while (typeIter.hasNext()) {
                    Map.Entry<Byte, Map<Byte, Map<Byte, byte[]>>> typeEntry = typeIter.next();
                    Map<Byte, Map<Byte, byte[]>> typeMap = typeEntry.getValue();
                    
                    // 遍历总数
                    Iterator<Map.Entry<Byte, Map<Byte, byte[]>>> totalIter = typeMap.entrySet().iterator();
                    while (totalIter.hasNext()) {
                        Map.Entry<Byte, Map<Byte, byte[]>> totalEntry = totalIter.next();
                        Map<Byte, byte[]> totalMap = totalEntry.getValue();
                        
                        // 检查时间戳
                        byte[] timeBytes = totalMap.get((byte)255);
                        if (timeBytes != null) {
                            long time = bytesToLong(timeBytes);
                            if (now - time > MERGE_TIMEOUT) {
                                totalIter.remove();
                                HiLog.info(LABEL, "清理过期数据包: 类型=" + getTypeName(typeEntry.getKey()) + 
                                       ", 总数=" + totalEntry.getKey());
                            }
                        } else {
                            // 没有时间戳，直接清理
                            totalIter.remove();
                        }
                    }
                    
                    // 如果类型映射为空，移除类型
                    if (typeMap.isEmpty()) {
                        typeIter.remove();
                    }
                }
            }
        } catch (Exception e) {
            HiLog.error(LABEL, "清理接收缓存错误: " + e.getMessage());
        }
    }
    
    /**
     * 关闭并清理资源
     */
    public void shutdown() {
        if (cleanupService != null) {
            cleanupService.shutdown();
            try {
                if (!cleanupService.awaitTermination(1, TimeUnit.SECONDS)) {
                    cleanupService.shutdownNow();
                }
            } catch (InterruptedException e) {
                cleanupService.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
        
        // 清空接收缓存
        synchronized (this) {
            receiveBuffer.clear();
        }
        
        HiLog.info(LABEL, "BleDataProcessor已关闭");
    }
    
    /**
     * 将long转换为byte数组
     */
    private static byte[] longToBytes(long value) {
        ByteBuffer buffer = ByteBuffer.allocate(Long.BYTES);
        buffer.putLong(value);
        return buffer.array();
    }
    
    /**
     * 将byte数组转换为long
     */
    private static long bytesToLong(byte[] bytes) {
        ByteBuffer buffer = ByteBuffer.wrap(bytes);
        return buffer.getLong();
    }
    
    /**
     * 数据发送接口
     */
    public interface DataSender {
        /**
         * 发送数据
         * @param data 要发送的数据
         * @return 是否发送成功
         */
        boolean send(byte[] data);
    }
} 