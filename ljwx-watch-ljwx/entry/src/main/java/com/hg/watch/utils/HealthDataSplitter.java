package com.hg.watch.utils;

import org.json.JSONException;
import org.json.JSONObject;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import java.util.UUID;
import java.util.ArrayList;
import java.util.List;
import com.hg.watch.BleConstants;

/**
 * 健康数据拆分工具类，用于将大型嵌套JSON数据拆分成小块进行传输
 */
public class HealthDataSplitter {
    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "ljwx");
    
    // 数据类型常量
    public static final String TYPE_HEALTH_META = "health_meta";
    public static final String TYPE_HEALTH_SLEEP = "health_sleep";
    public static final String TYPE_HEALTH_EXERCISE_DAILY = "health_exercise_daily";
    public static final String TYPE_HEALTH_EXERCISE_WEEK = "health_exercise_week";
    public static final String TYPE_HEALTH_SCIENTIFIC_SLEEP = "health_scientific_sleep";
    public static final String TYPE_HEALTH_WORKOUT = "health_workout";
    public static final String HEALTH_GROUP_ID_KEY = "health_group_id";
    
    // 默认MTU大小和消息开销，用于计算最大分片大小
    private static final int DEFAULT_MTU = BleConstants.DEFAULT_MTU;
    private static final int PACKET_OVERHEAD = 50; // 估计的JSON开销
    
    /**
     * 拆分健康数据为多个小包
     * @param healthData 完整的健康数据JSON字符串
     * @return 拆分后的健康数据元数据包
     */
    public static JSONObject[] splitHealthData(String healthData) {
        try {
            JSONObject healthJson = new JSONObject(healthData);
            return splitHealthData(healthJson);
        } catch (JSONException e) {
            HiLog.error(LABEL_LOG, "解析健康数据失败: " + e.getMessage());
            return new JSONObject[0];
        }
    }
    
    /**
     * 拆分健康数据为多个小包
     * @param healthJson 完整的健康数据JSON对象
     * @return 拆分后的健康数据包数组
     */
    public static JSONObject[] splitHealthData(JSONObject healthJson) {
        try {
            // 生成健康数据组ID，所有分片共享同一个组ID
            String healthGroupId = UUID.randomUUID().toString();
            
            // 提取嵌套数据
            JSONObject dataObj = healthJson.optJSONObject("data");
            if (dataObj == null) {
                HiLog.error(LABEL_LOG, "健康数据格式错误，缺少data字段");
                return new JSONObject[0];
            }
            
            // 使用ArrayList动态管理分片
            List<JSONObject> resultPackets = new ArrayList<>();
            
            // 1. 创建基础元数据包
            JSONObject metaData = new JSONObject();
            copyBasicFields(dataObj, metaData);
            metaData.put(HEALTH_GROUP_ID_KEY, healthGroupId);
            metaData.put("timestamp", dataObj.optString("cjsj", ""));
            
            JSONObject metaPacket = new JSONObject();
            metaPacket.put("type", TYPE_HEALTH_META);
            metaPacket.put("data", metaData);
            resultPackets.add(metaPacket);
            
            // 2. 处理嵌套字段，只有非null的字段才会被处理
            processNestedField(TYPE_HEALTH_SLEEP, "sleepData", healthGroupId, dataObj, resultPackets);
            processNestedField(TYPE_HEALTH_EXERCISE_DAILY, "exerciseDailyData", healthGroupId, dataObj, resultPackets);
            processNestedField(TYPE_HEALTH_EXERCISE_WEEK, "exerciseWeekData", healthGroupId, dataObj, resultPackets);
            processNestedField(TYPE_HEALTH_SCIENTIFIC_SLEEP, "scientificSleepData", healthGroupId, dataObj, resultPackets);
            processNestedField(TYPE_HEALTH_WORKOUT, "workoutData", healthGroupId, dataObj, resultPackets);
            
            // 转换为数组并返回
            JSONObject[] result = new JSONObject[resultPackets.size()];
            return resultPackets.toArray(result);
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "拆分健康数据失败: " + e.getMessage());
            return new JSONObject[0];
        }
    }
    
    /**
     * 处理嵌套字段，如果字段值不为null或"null"，则创建对应的分片包
     */
    private static void processNestedField(String type, String fieldName, String healthGroupId, 
                                          JSONObject source, List<JSONObject> resultPackets) throws JSONException {
        String fieldValue = JsonUtil.optString(source, fieldName, "null");
        if (!"null".equals(fieldValue) && !fieldValue.isEmpty()) {
            JSONObject packet = createNestedPacket(type, healthGroupId, fieldValue);
            if (packet != null) {
                resultPackets.add(packet);
            }
        }
    }
    
    /**
     * 创建嵌套字段数据包
     */
    private static JSONObject createNestedPacket(String type, String groupId, String fieldData) {
        try {
            // 检查数据是否为有效JSON，无需再次转义
            Object content;
            try {
                content = new JSONObject(fieldData);
            } catch (Exception e) {
                // 如果不是有效的JSON对象，尝试解析为字符串
                content = fieldData;
            }
            
            // 构建扁平化的数据结构，减少嵌套层次
            JSONObject data = new JSONObject();
            data.put(HEALTH_GROUP_ID_KEY, groupId);
            data.put("content", content);
            
            JSONObject packet = new JSONObject();
            packet.put("type", type);
            packet.put("data", data);
            
            return packet;
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "创建嵌套字段分片失败 [" + type + "]: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * 复制基本健康字段到目标JSON对象
     */
    private static void copyBasicFields(JSONObject source, JSONObject target) throws JSONException {
        // 复制所有非嵌套JSON的基本字段
        target.put("id", JsonUtil.optString(source, "id", ""));
        target.put("upload_method", JsonUtil.optString(source, "upload_method", "bluetooth"));
        target.put("heart_rate", source.optInt("heart_rate", 0));
        target.put("blood_oxygen", source.optInt("blood_oxygen", 0));
        target.put("body_temperature", JsonUtil.optString(source, "body_temperature", "0.0"));
        target.put("blood_pressure_systolic", source.optInt("blood_pressure_systolic", 0));
        target.put("blood_pressure_diastolic", source.optInt("blood_pressure_diastolic", 0));
        target.put("step", source.optInt("step", 0));
        target.put("distance", JsonUtil.optString(source, "distance", "0.0"));
        target.put("calorie", JsonUtil.optString(source, "calorie", "0.0"));
        target.put("latitude", JsonUtil.optString(source, "latitude", "0"));
        target.put("longitude", JsonUtil.optString(source, "longitude", "0"));
        target.put("altitude", JsonUtil.optString(source, "altitude", "0"));
        target.put("stress", source.optInt("stress", 0));
    }
} 