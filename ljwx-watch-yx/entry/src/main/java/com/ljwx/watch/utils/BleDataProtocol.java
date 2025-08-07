package com.ljwx.watch.utils;

import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import com.ljwx.watch.BleConstants;
import org.json.JSONObject;
import org.json.JSONException;
import java.util.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

/**
 * 蓝牙数据传输协议，使用二进制格式高效传输数据#提高传输效率和可靠性
 */
public class BleDataProtocol {
    private static final HiLogLabel LABEL = new HiLogLabel(3, 0xD001100, "ljwx");
    
    // 协议常量定义
    private static final short HEADER_MAGIC = (short)0xA55A; // 头部标识
    private static final int HEADER_SIZE = 7; // 头部大小(2+1+1+1+2)
    private static final int DEFAULT_MTU = BleConstants.DEFAULT_MTU;
    
    // 数据类型定义
    public static final byte TYPE_DEVICE = 0x01; // 设备信息
    public static final byte TYPE_HEALTH_META = 0x11; // 健康元数据
    public static final byte TYPE_HEALTH_SLEEP = 0x12; // 睡眠数据
    public static final byte TYPE_HEALTH_EXERCISE = 0x13; // 运动数据
    public static final byte TYPE_HEALTH_WORKOUT = 0x14; // 锻炼数据
    public static final byte TYPE_EVENT = 0x21; // 事件数据
    
    /**
     * 将设备信息编码为字节数组片段列表
     * @param deviceInfo 设备信息JSON
     * @param mtu 当前MTU大小
     * @return 字节片段列表
     */
    public static List<byte[]> encodeDeviceInfo(JSONObject deviceInfo, int mtu) {
        try {
            // 修改为更安全的MTU计算方式
            int effectiveMtu = Math.min(mtu, 247); // 限制最大有效MTU为247
            int maxPayload = Math.max(20, effectiveMtu - HEADER_SIZE - 10); // 添加10字节安全余量
            
            HiLog.info(LABEL, "设备信息分包计算: 协商MTU=" + mtu + ", 有效MTU=" + effectiveMtu + 
                      ", 最大载荷=" + maxPayload + "字节");
            
            // 直接使用整个设备数据JSON
            byte[] deviceBytes = deviceInfo.toString().getBytes(StandardCharsets.UTF_8);
            
            // 分割数据
            return splitData(deviceBytes, TYPE_DEVICE, maxPayload);
        } catch (Exception e) {
            HiLog.error(LABEL, "编码设备信息失败: " + e.getMessage());
            return Collections.emptyList();
        }
    }
    
    /**
     * 将健康数据编码为字节数组片段列表
     * @param healthData 健康数据JSON
     * @param mtu 当前MTU大小
     * @return 字节片段列表
     */
    public static Map<Byte, List<byte[]>> encodeHealthData(JSONObject healthData, int mtu) {
        try {
            // 修改为更安全的MTU计算方式
            int effectiveMtu = Math.min(mtu, 247); // 限制最大有效MTU为247
            int maxPayload = Math.max(20, effectiveMtu - HEADER_SIZE - 10); // 添加10字节安全余量
            
            HiLog.info(LABEL, "健康数据分包计算: 协商MTU=" + mtu + ", 有效MTU=" + effectiveMtu + 
                      ", 最大载荷=" + maxPayload + "字节");
            
            // 结果集合，按类型分组
            Map<Byte, List<byte[]>> result = new HashMap<>();
            
            // 直接使用整个健康数据JSON
            byte[] healthBytes = healthData.toString().getBytes(StandardCharsets.UTF_8);
            result.put(TYPE_HEALTH_META, splitData(healthBytes, TYPE_HEALTH_META, maxPayload));
            
            return result;
        } catch (Exception e) {
            HiLog.error(LABEL, "编码健康数据失败: " + e.getMessage());
            return Collections.emptyMap();
        }
    }
    
    /**
     * 将事件数据编码为字节数组
     * @param eventData 事件数据JSON
     * @param mtu 当前MTU大小
     * @return 字节片段列表
     */
    public static List<byte[]> encodeEventData(JSONObject eventData, int mtu) {
        try {
            // 修改为更安全的MTU计算方式
            int effectiveMtu = Math.min(mtu, 247); // 限制最大有效MTU为247
            int maxPayload = Math.max(20, effectiveMtu - HEADER_SIZE - 10); // 添加10字节安全余量
            
            HiLog.info(LABEL, "事件数据分包计算: 协商MTU=" + mtu + ", 有效MTU=" + effectiveMtu + 
                      ", 最大载荷=" + maxPayload + "字节");
                      
            // 直接使用整个事件数据JSON
            byte[] eventBytes = eventData.toString().getBytes(StandardCharsets.UTF_8);
            
            return splitData(eventBytes, TYPE_EVENT, maxPayload);
        } catch (Exception e) {
            HiLog.error(LABEL, "编码事件数据失败: " + e.getMessage());
            return Collections.emptyList();
        }
    }
    
    /**
     * 解码接收到的数据包
     * @param packet 接收到的完整数据包
     * @return 解码后的数据包信息，如果无效则返回null
     */
    public static DataPacket decodePacket(byte[] packet) {
        try {
            if (packet.length < HEADER_SIZE) {
                return null; // 数据包过短
            }
            
            ByteBuffer buffer = ByteBuffer.wrap(packet);
            
            // 验证头部标识
            short magic = buffer.getShort();
            if (magic != HEADER_MAGIC) {
                return null; // 头部标识不匹配
            }
            
            // 读取包头信息
            byte type = buffer.get();
            byte index = buffer.get();
            byte total = buffer.get();
            short dataLength = buffer.getShort();
            
            // 验证数据长度
            if (buffer.remaining() < dataLength) {
                return null; // 实际数据长度不足
            }
            
            // 提取数据
            byte[] data = new byte[dataLength];
            buffer.get(data);
            
            return new DataPacket(type, index, total, data);
        } catch (Exception e) {
            HiLog.error(LABEL, "解码数据包失败: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * 将Map序列化为紧凑的二进制格式
     * 格式: [键长度(1B)][键][值长度(2B)][值]...
     */
    private static byte[] serializeMap(Map<String, String> map) {
        try {
            ByteBuffer buffer = ByteBuffer.allocate(4096); // 预分配足够大的缓冲区
            
            for (Map.Entry<String, String> entry : map.entrySet()) {
                byte[] keyBytes = entry.getKey().getBytes(StandardCharsets.UTF_8);
                byte[] valueBytes = entry.getValue().getBytes(StandardCharsets.UTF_8);
                
                // 键长度(限制为255)
                buffer.put((byte)Math.min(255, keyBytes.length));
                // 键内容
                buffer.put(keyBytes, 0, Math.min(255, keyBytes.length));
                // 值长度(限制为65535)
                buffer.putShort((short)Math.min(65535, valueBytes.length));
                // 值内容
                buffer.put(valueBytes, 0, Math.min(65535, valueBytes.length));
            }
            
            // 创建结果数组
            byte[] result = new byte[buffer.position()];
            buffer.flip();
            buffer.get(result);
            
            return result;
        } catch (Exception e) {
            HiLog.error(LABEL, "序列化Map失败: " + e.getMessage());
            return new byte[0];
        }
    }
    
    /**
     * 将Map反序列化为JSON对象
     */
    public static JSONObject deserializeMap(byte[] data) {
        try {
            JSONObject result = new JSONObject();
            ByteBuffer buffer = ByteBuffer.wrap(data);
            
            while (buffer.hasRemaining()) {
                // 至少需要3字节来读取键长度和值长度
                if (buffer.remaining() < 3) {
                    break;
                }
                
                // 读取键长度
                int keyLen = buffer.get() & 0xFF;
                if (buffer.remaining() < keyLen + 2) {
                    break; // 剩余数据不足
                }
                
                // 读取键
                byte[] keyBytes = new byte[keyLen];
                buffer.get(keyBytes);
                String key = new String(keyBytes, StandardCharsets.UTF_8);
                
                // 读取值长度
                int valueLen = buffer.getShort() & 0xFFFF;
                if (buffer.remaining() < valueLen) {
                    break; // 剩余数据不足
                }
                
                // 读取值
                byte[] valueBytes = new byte[valueLen];
                buffer.get(valueBytes);
                String value = new String(valueBytes, StandardCharsets.UTF_8);
                
                // 添加到结果
                result.put(key, value);
            }
            
            return result;
        } catch (Exception e) {
            HiLog.error(LABEL, "反序列化Map失败: " + e.getMessage());
            return new JSONObject();
        }
    }
    
    /**
     * 分割数据为多个包
     */
    private static List<byte[]> splitData(byte[] data, byte type, int maxPayload) {
        List<byte[]> result = new ArrayList<>();
        
        // 计算分片数量
        int totalChunks = (int)Math.ceil((double)data.length / maxPayload);
        totalChunks = Math.min(255, totalChunks); // 最多255个分片
        
        for (int i = 0; i < totalChunks; i++) {
            // 计算当前分片的数据范围
            int start = i * maxPayload;
            int end = Math.min(start + maxPayload, data.length);
            int length = end - start;
            
            // 创建完整数据包
            ByteBuffer buffer = ByteBuffer.allocate(HEADER_SIZE + length);
            
            // 写入头部
            buffer.putShort(HEADER_MAGIC); // 头部标识
            buffer.put(type); // 数据类型
            buffer.put((byte)i); // 分片索引
            buffer.put((byte)totalChunks); // 总分片数
            buffer.putShort((short)length); // 数据长度
            
            // 写入数据
            buffer.put(data, start, length);
            
            // 添加到结果列表
            result.add(buffer.array());
        }
        
        return result;
    }
    
    /**
     * 数据包类，表示解码后的数据包
     */
    public static class DataPacket {
        public final byte type;
        public final byte index;
        public final byte total;
        public final byte[] data;
        
        public DataPacket(byte type, byte index, byte total, byte[] data) {
            this.type = type;
            this.index = index;
            this.total = total;
            this.data = data;
        }
        
        @Override
        public String toString() {
            return String.format("DataPacket[type=%d, index=%d/%d, dataSize=%d]", 
                                type, index + 1, total, data.length);
        }
    }
} 