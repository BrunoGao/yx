package com.hg.watch.utils;

import org.json.JSONException;
import org.json.JSONObject;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;

public class JsonUtil {
    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "ljwx");
    
    public static JSONObject parse(String jsonStr) throws JSONException {
        if (jsonStr == null || jsonStr.isEmpty()) {
            return new JSONObject();
        }
        try {
            return new JSONObject(jsonStr);
        } catch (JSONException e) {
            HiLog.error(LABEL_LOG, "JSON parse error: " + e.getMessage());
            throw e;
        }
    }
    
    public static boolean isValidJson(String test) {
        try {
            new JSONObject(test);
            return true;
        } catch (JSONException ex) {
            return false;
        }
    }
    
    /**
     * 创建标准格式的数据包
     * @param type 数据类型
     * @param data 数据内容
     * @return 标准格式的JSON对象
     */
    public static JSONObject createPacket(String type, Object data) {
        try {
            // 使用标准格式，避免额外转义
            JSONObject packet = new JSONObject();
            packet.put("type", type);
            packet.put("data", data);
            
            // 确保JSON格式正确，无多余转义
            return packet;
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "Create packet error: " + e.getMessage());
            return new JSONObject();
        }
    }
    
    /**
     * 从JSON对象中安全获取字符串
     */
    public static String optString(JSONObject json, String key, String defaultValue) {
        if (json == null || !json.has(key)) {
            return defaultValue;
        }
        try {
            Object value = json.get(key);
            if (value == null || value == JSONObject.NULL) {
                return defaultValue;
            }
            return value.toString();
        } catch (Exception e) {
            return defaultValue;
        }
    }
    
    /**
     * 移除JSON字符串中的转义字符，使其更易于解析
     */
    public static String unescapeJson(String json) {
        if (json == null || json.isEmpty()) {
            return json;
        }
        
        // 仅替换多余的转义符号
        return json.replace("\\\"", "\"")
                   .replace("\\\\", "\\")
                   .replace("\\/", "/");
    }
} 