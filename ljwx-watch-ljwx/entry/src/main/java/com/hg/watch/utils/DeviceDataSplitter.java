package com.hg.watch.utils;

import org.json.JSONException;
import org.json.JSONObject;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import java.util.UUID;
import java.util.ArrayList;
import java.util.List;
import java.util.Iterator;
import java.nio.charset.StandardCharsets;
import com.hg.watch.BleConstants;

/**
 * 设备数据拆分工具类，专门处理设备数据的分片传输#提供更高效的设备数据分片方案
 */
public class DeviceDataSplitter {
    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "ljwx");
    
    // 数据类型常量
    public static final String TYPE_DEVICE = "device";
    public static final String TYPE_DEVICE_CHUNK = "device_chunk";
    public static final String DEVICE_GROUP_ID_KEY = "device_group_id";
    
    // 默认MTU大小和消息开销，用于计算最大分片大小
    private static final int DEFAULT_MTU = BleConstants.DEFAULT_MTU;
    private static final int PACKET_OVERHEAD = 60; // 增加JSON格式开销估计
    
    /**
     * 拆分设备数据为多个小包
     * @param deviceData 完整的设备数据JSON字符串
     * @param mtu 当前MTU大小，用于计算分片大小
     * @return 拆分后的设备数据包数组
     */
    public static JSONObject[] splitDeviceData(String deviceData, int mtu) {
        try {
            JSONObject deviceJson = new JSONObject(deviceData);
            return splitDeviceData(deviceJson, mtu);
        } catch (JSONException e) {
            HiLog.error(LABEL_LOG, "解析设备数据失败: " + e.getMessage());
            return new JSONObject[0];
        }
    }
    
    /**
     * 拆分设备数据为多个小包
     * @param deviceJson 完整的设备数据JSON对象
     * @param mtu 当前MTU大小，用于计算分片大小
     * @return 拆分后的设备数据包数组
     */
    public static JSONObject[] splitDeviceData(JSONObject deviceJson, int mtu) {
        try {
            // 生成设备数据组ID，所有分片共享同一个组ID
            String deviceGroupId = UUID.randomUUID().toString();
            
            // 计算可用最大分片大小，减去通信协议开销，确保安全余量
            int maxChunkSize = Math.max(50, Math.min(mtu - PACKET_OVERHEAD, 450)); // 确保不超过MTU限制
            
            // 从设备信息中提取序列号作为设备ID
            String deviceId = "";
            try {
                deviceId = deviceJson.optString("SerialNumber", "unknown");
            } catch (Exception e) {
                HiLog.warn(LABEL_LOG, "无法从设备数据中提取SerialNumber: " + e.getMessage());
            }
            
            // 将JSON对象转换为字段集合，每个字段作为一个单元进行分片
            List<String> fields = new ArrayList<>();
            Iterator<String> keys = deviceJson.keys();
            while (keys.hasNext()) {
                String key = keys.next();
                Object value = deviceJson.opt(key);
                String fieldStr = formatJsonField(key, value);
                fields.add(fieldStr);
            }
            
            // 估算每个字段的字节大小
            List<Integer> fieldSizes = new ArrayList<>(fields.size());
            int totalSize = 0;
            for (String field : fields) {
                int fieldSize = field.getBytes(StandardCharsets.UTF_8).length;
                fieldSizes.add(fieldSize);
                totalSize += fieldSize;
            }
            
            // 计算理想分片数量，确保均匀分布
            int idealChunkCount = (int)Math.ceil((double)totalSize / maxChunkSize);
            int targetChunkSize = totalSize / idealChunkCount;
            
            HiLog.info(LABEL_LOG, "设备数据共有 " + fields.size() + " 个字段, 总大小: " + totalSize 
                     + " 字节, 分片数量: " + idealChunkCount + ", 目标分片大小: " + targetChunkSize);
            
            // 根据计算的分片大小组合分片
            List<JSONObject> resultPackets = new ArrayList<>();
            List<StringBuilder> chunks = new ArrayList<>();
            List<Integer> chunkSizes = new ArrayList<>();
            
            // 初始化第一个分片
            chunks.add(new StringBuilder());
            chunkSizes.add(0);
            
            // 贪心算法: 尽量平均分配字段到各个分片
            for (int i = 0; i < fields.size(); i++) {
                String field = fields.get(i);
                int fieldSize = fieldSizes.get(i);
                
                // 找到最小的分片添加
                int minChunkIndex = 0;
                int minChunkSize = chunkSizes.get(0);
                
                for (int j = 1; j < chunks.size(); j++) {
                    if (chunkSizes.get(j) < minChunkSize) {
                        minChunkIndex = j;
                        minChunkSize = chunkSizes.get(j);
                    }
                }
                
                // 如果最小分片加上该字段会超过限制，且当前分片数小于理想分片数，创建新分片
                if (minChunkSize + fieldSize > maxChunkSize && chunks.size() < idealChunkCount) {
                    chunks.add(new StringBuilder());
                    chunkSizes.add(0);
                    minChunkIndex = chunks.size() - 1;
                    minChunkSize = 0;
                }
                
                // 添加字段到选定的分片
                StringBuilder chunk = chunks.get(minChunkIndex);
                if (minChunkSize > 0) {
                    chunk.append(",");
                    chunkSizes.set(minChunkIndex, minChunkSize + 1); // 逗号大小
                }
                
                chunk.append(field);
                chunkSizes.set(minChunkIndex, chunkSizes.get(minChunkIndex) + fieldSize);
            }
            
            // 生成最终的分片包
            for (int i = 0; i < chunks.size(); i++) {
                StringBuilder chunk = chunks.get(i);
                if (chunk.length() > 0) {
                    JSONObject packet = createDeviceChunkPacket(
                        deviceGroupId, 
                        deviceId, 
                        chunk.toString(), 
                        i,
                        chunks.size()
                    );
                    resultPackets.add(packet);
                }
            }
            
            // 打印分片大小信息
            for (int i = 0; i < resultPackets.size(); i++) {
                JSONObject packet = resultPackets.get(i);
                String chunkStr = packet.toString();
                int chunkSize = chunkStr.getBytes(StandardCharsets.UTF_8).length;
                HiLog.debug(LABEL_LOG, "设备数据分片 " + (i+1) + "/" + resultPackets.size() + 
                           ", 索引=" + i + ", 大小=" + chunkSize + " 字节" +
                           (chunkSize > maxChunkSize ? " [警告:超出最大大小]" : ""));
            }
            
            // 转换为数组并返回
            JSONObject[] result = new JSONObject[resultPackets.size()];
            return resultPackets.toArray(result);
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "拆分设备数据失败: " + e.getMessage());
            return new JSONObject[0];
        }
    }
    
    /**
     * 格式化JSON字段值为字符串，避免使用JSONObject.valueToString
     */
    private static String formatJsonField(String key, Object value) {
        StringBuilder result = new StringBuilder();
        result.append("\"").append(key).append("\":");
        
        if (value == null) {
            result.append("null");
        } else if (value instanceof String) {
            // 字符串类型需要添加引号并转义特殊字符
            result.append("\"").append(escapeJsonString((String)value)).append("\"");
        } else if (value instanceof Number || value instanceof Boolean) {
            // 数字和布尔值直接使用toString
            result.append(value.toString());
        } else if (value instanceof JSONObject || value instanceof org.json.JSONArray) {
            // JSON对象或数组直接使用toString
            result.append(value.toString());
        } else {
            // 其他类型转为字符串并添加引号
            result.append("\"").append(escapeJsonString(value.toString())).append("\"");
        }
        
        return result.toString();
    }
    
    /**
     * 转义JSON字符串中的特殊字符
     */
    private static String escapeJsonString(String input) {
        if (input == null) {
            return "";
        }
        
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < input.length(); i++) {
            char c = input.charAt(i);
            switch (c) {
                case '\\': result.append("\\\\"); break;
                case '\"': result.append("\\\""); break;
                case '\b': result.append("\\b"); break;
                case '\f': result.append("\\f"); break;
                case '\n': result.append("\\n"); break;
                case '\r': result.append("\\r"); break;
                case '\t': result.append("\\t"); break;
                default:
                    if (c < ' ') {
                        result.append(String.format("\\u%04x", (int)c));
                    } else {
                        result.append(c);
                    }
            }
        }
        return result.toString();
    }
    
    /**
     * 创建设备数据分片包
     */
    private static JSONObject createDeviceChunkPacket(
        String groupId, 
        String deviceId, 
        String chunkData, 
        int index,
        int totalChunks) throws JSONException {
        
        // 构建设备分片数据
        JSONObject data = new JSONObject();
        data.put(DEVICE_GROUP_ID_KEY, groupId);
        data.put("device_id", deviceId);
        data.put("chunk", chunkData);
        data.put("index", index);
        data.put("total_chunks", totalChunks);
        
        // 构建完整包
        JSONObject packet = new JSONObject();
        packet.put("type", TYPE_DEVICE_CHUNK);
        packet.put("data", data);
        
        return packet;
    }
    
    /**
     * 在客户端合并设备数据分片的示例
     */
    public static JSONObject mergeDeviceChunks(List<JSONObject> chunks) {
        try {
            if (chunks == null || chunks.isEmpty()) {
                return null;
            }
            
            // 按索引排序
            chunks.sort((a, b) -> {
                try {
                    int indexA = a.getJSONObject("data").getInt("index");
                    int indexB = b.getJSONObject("data").getInt("index");
                    return Integer.compare(indexA, indexB);
                } catch (JSONException e) {
                    return 0;
                }
            });
            
            // 合并chunk数据
            StringBuilder mergedData = new StringBuilder("{");
            for (int i = 0; i < chunks.size(); i++) {
                JSONObject chunk = chunks.get(i);
                String chunkData = chunk.getJSONObject("data").getString("chunk");
                
                // 直接添加字段，不添加大括号
                if (i > 0 && !mergedData.toString().endsWith(",") && 
                   !chunkData.startsWith(",")) {
                    mergedData.append(",");
                }
                
                mergedData.append(chunkData);
            }
            // 添加结束大括号
            mergedData.append("}");
            
            // 解析合并后的JSON
            String jsonStr = mergedData.toString();
            HiLog.debug(LABEL_LOG, "合并后的设备数据: " + jsonStr);
            return new JSONObject(jsonStr);
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "合并设备数据分片失败: " + e.getMessage());
            return null;
        }
    }
} 