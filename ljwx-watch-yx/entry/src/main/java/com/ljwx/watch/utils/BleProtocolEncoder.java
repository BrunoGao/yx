package com.ljwx.watch.utils;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import org.json.JSONObject;
import org.json.JSONArray;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.text.SimpleDateFormat;
import java.util.TimeZone;

public class BleProtocolEncoder {//BLE协议编码器，实现二进制TLV格式传输
    private static final HiLogLabel LOG=new HiLogLabel(3,0xD001100,"ljwx");
    private static final byte VERSION=1;//协议版本
    private static final byte FORMAT_BINARY=1,FORMAT_JSON=2;//数据格式
    
    //Type ID定义
    public static final byte TYPE_HEALTH_DATA=0x01,TYPE_DEVICE_INFO=0x02,TYPE_COMMON_EVENT=0x03,
        TYPE_MESSAGE=0x04,TYPE_CONFIG=0x05,TYPE_BLE_CONTROL=0x06,//TYPE_RESTART_DETECTION=0x07,
        TYPE_HEARTBEAT=(byte)0xFE,TYPE_DEBUG=(byte)0xFF;
    
    //字段ID定义-健康数据
    private static final byte HEALTH_ID=0x01,HEALTH_UPLOAD_METHOD=0x02,HEALTH_HEART_RATE=0x03,
        HEALTH_BLOOD_OXYGEN=0x04,HEALTH_BODY_TEMP=0x05,HEALTH_BP_SYS=0x06,HEALTH_BP_DIA=0x07,
        HEALTH_STEP=0x08,HEALTH_DISTANCE=0x09,HEALTH_CALORIE=0x0A,HEALTH_LAT=0x0B,HEALTH_LON=0x0C,
        HEALTH_ALT=0x0D,HEALTH_STRESS=0x0E,HEALTH_TIMESTAMP=0x0F,HEALTH_SLEEP_DATA=0x10;
    
    //字段ID定义-设备信息
    private static final byte DEVICE_SYSTEM_VER=0x01,DEVICE_WIFI_ADDR=0x02,DEVICE_BT_ADDR=0x03,
        DEVICE_IP=0x04,DEVICE_NETWORK_MODE=0x05,DEVICE_SERIAL=0x06,DEVICE_NAME=0x07,DEVICE_IMEI=0x08,
        DEVICE_BATTERY=0x09,DEVICE_VOLTAGE=0x0A,DEVICE_CHARGING=0x0B,DEVICE_WEAR_STATE=0x0D,
        DEVICE_TIMESTAMP=0x0E;
    
    //字段ID定义-通用事件
    private static final byte EVENT_ACTION=0x01,EVENT_VALUE=0x02,EVENT_DEVICE_SN=0x03,EVENT_TIMESTAMP=0x04;
    
    // 北京时间格式化器
    private static final SimpleDateFormat BEIJING_TIME_FORMAT=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
    static{
        BEIJING_TIME_FORMAT.setTimeZone(TimeZone.getTimeZone("Asia/Shanghai"));
    }
    
    public static class ProtocolPacket{//协议数据包
        public final byte[]data;public final boolean isChunked;public final int chunkIndex,totalChunks;
        public ProtocolPacket(byte[]data,boolean isChunked,int chunkIndex,int totalChunks){
            this.data=data;this.isChunked=isChunked;this.chunkIndex=chunkIndex;this.totalChunks=totalChunks;
        }
    }
    
    public static List<ProtocolPacket>encodeHealthData(String healthJson,int mtu){//编码健康数据
        try{
            JSONObject healthRoot=new JSONObject(healthJson);
            // 修复：健康数据在data字段中，需要先提取data对象
            JSONObject health=healthRoot.optJSONObject("data");
            if(health==null){
                // 如果没有data字段，直接使用根对象
                health=healthRoot;
            }
            
            HiLog.info(LOG,"解析健康数据字段数量:"+health.length());
            byte[]payload=buildHealthTLV(health);
            HiLog.info(LOG,"健康数据TLV编码后大小:"+payload.length+"字节");
            return createPackets(TYPE_HEALTH_DATA,FORMAT_BINARY,payload,mtu);
        }catch(Exception e){
            HiLog.error(LOG,"编码健康数据失败:"+e.getMessage());
            return Collections.emptyList();
        }
    }
    
    public static List<ProtocolPacket>encodeDeviceInfo(String deviceJson,int mtu){//编码设备信息
        try{
            JSONObject deviceRoot=new JSONObject(deviceJson);
            // 设备信息可能也有data嵌套，先检查
            JSONObject device=deviceRoot.optJSONObject("data");
            if(device==null){
                device=deviceRoot;
            }
            
            byte[]payload=buildDeviceTLV(device);
            return createPackets(TYPE_DEVICE_INFO,FORMAT_BINARY,payload,mtu);
        }catch(Exception e){
            HiLog.error(LOG,"编码设备信息失败:"+e.getMessage());
            return Collections.emptyList();
        }
    }
    
    public static List<ProtocolPacket>encodeCommonEvent(String event,int mtu){//编码公共事件
        try{
            JSONObject eventObj=null;
            
            // 首先尝试解析为JSON格式
            if(event.trim().startsWith("{")){
                try{
                    eventObj=new JSONObject(event);
                    HiLog.info(LOG,"解析JSON格式公共事件");
                }catch(Exception e){
                    HiLog.warn(LOG,"JSON解析失败，尝试冒号格式:"+e.getMessage());
                }
            }
            
            // 如果JSON解析失败，尝试冒号分隔格式
            if(eventObj==null){
                String[]parts=event.split(":");
                if(parts.length<3)throw new IllegalArgumentException("事件格式错误");
                
                eventObj=new JSONObject();
                eventObj.put("action",parts[0]);
                eventObj.put("value",parts[1]);
                eventObj.put("device_sn",parts[2]);
                HiLog.info(LOG,"解析冒号格式公共事件");
            }
            
            // 自动添加或覆盖timestamp
            String timestamp=eventObj.optString("timestamp","");
            if(timestamp.isEmpty()){
                timestamp=BEIJING_TIME_FORMAT.format(new Date());
                eventObj.put("timestamp",timestamp);
            }
            
            HiLog.info(LOG,"公共事件字段:action="+eventObj.optString("action","")+
                ",value="+eventObj.optString("value","")+
                ",device_sn="+eventObj.optString("device_sn","")+
                ",timestamp="+eventObj.optString("timestamp",""));
            
            byte[]payload=buildEventTLV(eventObj);
            HiLog.info(LOG,"公共事件TLV编码后大小:"+payload.length+"字节");
            return createPackets(TYPE_COMMON_EVENT,FORMAT_BINARY,payload,mtu);
        }catch(Exception e){
            HiLog.error(LOG,"编码公共事件失败:"+e.getMessage());
            return Collections.emptyList();
        }
    }
    
    // 完全移除重启检测编码功能
    // public static List<ProtocolPacket>encodeRestartDetection(String data,int mtu){//编码重启检测信号
    //     // 此功能已被移除
    //     return Collections.emptyList();
    // }
    
    private static byte[]buildHealthTLV(JSONObject health){//构建健康数据TLV
        List<byte[]>fields=new ArrayList<>();
        int fieldCount=0; // 计数器，统计编码了多少个字段
        
        // 使用实际字段名编码，增加调试信息
        if(addStringFieldWithCheck(fields,HEALTH_ID,health.optString("id","")))fieldCount++;
        if(addStringFieldWithCheck(fields,HEALTH_UPLOAD_METHOD,health.optString("upload_method","")))fieldCount++;
        if(addUint8FieldWithCheck(fields,HEALTH_HEART_RATE,(byte)health.optInt("heart_rate",0)))fieldCount++;
        if(addUint8FieldWithCheck(fields,HEALTH_BLOOD_OXYGEN,(byte)health.optInt("blood_oxygen",0)))fieldCount++;
        if(addStringFieldWithCheck(fields,HEALTH_BODY_TEMP,health.optString("body_temperature","")))fieldCount++;
        if(addUint8FieldWithCheck(fields,HEALTH_BP_SYS,(byte)health.optInt("blood_pressure_systolic",0)))fieldCount++;
        if(addUint8FieldWithCheck(fields,HEALTH_BP_DIA,(byte)health.optInt("blood_pressure_diastolic",0)))fieldCount++;
        if(addUint16FieldWithCheck(fields,HEALTH_STEP,(short)health.optInt("step",0)))fieldCount++;
        if(addStringFieldWithCheck(fields,HEALTH_DISTANCE,health.optString("distance","")))fieldCount++;
        if(addStringFieldWithCheck(fields,HEALTH_CALORIE,health.optString("calorie","")))fieldCount++;
        if(addStringFieldWithCheck(fields,HEALTH_LAT,health.optString("latitude","")))fieldCount++;
        if(addStringFieldWithCheck(fields,HEALTH_LON,health.optString("longitude","")))fieldCount++;
        if(addStringFieldWithCheck(fields,HEALTH_ALT,health.optString("altitude","")))fieldCount++;
        if(addUint8FieldWithCheck(fields,HEALTH_STRESS,(byte)health.optInt("stress",0)))fieldCount++;
        
        // 添加sleepData字段支持
        String sleepData=health.optString("sleepData","");
        if(!sleepData.isEmpty()&&!sleepData.equals("null")){
            if(addStringFieldWithCheck(fields,HEALTH_SLEEP_DATA,compactSleepDataEncoding(sleepData)))fieldCount++;
        }
        
        // 自动添加当前北京时间作为timestamp
        String timestamp=health.optString("timestamp","");
        if(timestamp.isEmpty()){
            timestamp=BEIJING_TIME_FORMAT.format(new Date());
        }
        if(addStringFieldWithCheck(fields,HEALTH_TIMESTAMP,timestamp))fieldCount++;
        
        HiLog.info(LOG,"健康数据实际编码字段数:"+fieldCount+"/16");
        
        int totalLen=0;for(byte[]f:fields)totalLen+=f.length;
        ByteBuffer buf=ByteBuffer.allocate(totalLen);
        for(byte[]f:fields)buf.put(f);
        return buf.array();
    }
    
    private static byte[]buildDeviceTLV(JSONObject device){//构建设备信息TLV
        List<byte[]>fields=new ArrayList<>();
        int fieldCount=0; // 计数器，统计编码了多少个字段
        
        // 修复字段名映射，匹配实际JSON字段名，增加调试信息
        if(addStringFieldWithCheck(fields,DEVICE_SYSTEM_VER,device.optString("System Software Version","")))fieldCount++;
        if(addStringFieldWithCheck(fields,DEVICE_WIFI_ADDR,device.optString("Wifi Address","")))fieldCount++;
        if(addStringFieldWithCheck(fields,DEVICE_BT_ADDR,device.optString("Bluetooth Address","")))fieldCount++;
        if(addStringFieldWithCheck(fields,DEVICE_IP,device.optString("IP Address","")))fieldCount++;
        if(addUint8FieldWithCheck(fields,DEVICE_NETWORK_MODE,(byte)device.optInt("Network Access Mode",0)))fieldCount++;
        if(addStringFieldWithCheck(fields,DEVICE_SERIAL,device.optString("SerialNumber","")))fieldCount++;
        if(addStringFieldWithCheck(fields,DEVICE_NAME,device.optString("Device Name","")))fieldCount++;
        if(addStringFieldWithCheck(fields,DEVICE_IMEI,device.optString("IMEI","")))fieldCount++;
        if(addUint8FieldWithCheck(fields,DEVICE_BATTERY,(byte)device.optInt("batteryLevel",0)))fieldCount++;
        if(addUint16FieldWithCheck(fields,DEVICE_VOLTAGE,(short)device.optInt("voltage",0)))fieldCount++;
        if(addStringFieldWithCheck(fields,DEVICE_CHARGING,device.optString("chargingStatus","")))fieldCount++;
        if(addUint8FieldWithCheck(fields,DEVICE_WEAR_STATE,(byte)device.optInt("wearState",0)))fieldCount++;
        
        // 自动添加当前北京时间作为timestamp
        String timestamp=device.optString("timestamp","");
        if(timestamp.isEmpty()){
            timestamp=BEIJING_TIME_FORMAT.format(new Date());
        }
        if(addStringFieldWithCheck(fields,DEVICE_TIMESTAMP,timestamp))fieldCount++;
        
        HiLog.info(LOG,"设备信息实际编码字段数:"+fieldCount+"/13");
        
        int totalLen=0;for(byte[]f:fields)totalLen+=f.length;
        ByteBuffer buf=ByteBuffer.allocate(totalLen);
        for(byte[]f:fields)buf.put(f);
        return buf.array();
    }
    
    private static byte[]buildEventTLV(JSONObject event){//构建通用事件TLV
        List<byte[]>fields=new ArrayList<>();
        int fieldCount=0; // 计数器，统计编码了多少个字段
        
        // 编码事件字段
        if(addStringFieldWithCheck(fields,EVENT_ACTION,event.optString("action","")))fieldCount++;
        if(addStringFieldWithCheck(fields,EVENT_VALUE,event.optString("value","")))fieldCount++;
        if(addStringFieldWithCheck(fields,EVENT_DEVICE_SN,event.optString("device_sn","")))fieldCount++;
        
        // 自动添加当前北京时间作为timestamp
        String timestamp=event.optString("timestamp","");
        if(timestamp.isEmpty()){
            timestamp=BEIJING_TIME_FORMAT.format(new Date());
        }
        if(addStringFieldWithCheck(fields,EVENT_TIMESTAMP,timestamp))fieldCount++;
        
        HiLog.info(LOG,"公共事件实际编码字段数:"+fieldCount+"/4");
        
        int totalLen=0;for(byte[]f:fields)totalLen+=f.length;
        ByteBuffer buf=ByteBuffer.allocate(totalLen);
        for(byte[]f:fields)buf.put(f);
        return buf.array();
    }
    
    private static boolean addStringFieldWithCheck(List<byte[]>fields,byte id,String value){//添加字符串字段
        if(value!=null&&!value.isEmpty()){
            byte[]valueBytes=value.getBytes(StandardCharsets.UTF_8);
            if(valueBytes.length<=255){
                ByteBuffer buf=ByteBuffer.allocate(2+valueBytes.length);
                buf.put(id).put((byte)valueBytes.length).put(valueBytes);
                fields.add(buf.array());
                return true;
            }
        }
        return false;
    }
    
    private static boolean addUint8FieldWithCheck(List<byte[]>fields,byte id,byte value){//添加uint8字段
        fields.add(new byte[]{id,1,value});
        return true;
    }
    
    private static boolean addUint16FieldWithCheck(List<byte[]>fields,byte id,short value){//添加uint16字段
        ByteBuffer buf=ByteBuffer.allocate(4);
        buf.put(id).put((byte)2).putShort(value);
        fields.add(buf.array());
        return true;
    }
    
    private static void addUint32Field(List<byte[]>fields,byte id,long value){//添加uint32字段
        ByteBuffer buf=ByteBuffer.allocate(6);
        buf.put(id).put((byte)4).putInt((int)value);
        fields.add(buf.array());
    }
    
    private static List<ProtocolPacket>createPackets(byte type,byte format,byte[]payload,int mtu){//创建数据包
        int headerSize=5;//版本+类型+格式+长度
        int maxPayloadSize=Math.max(20,mtu-headerSize-3);//保留3字节ATT开销
        
        if(payload.length<=maxPayloadSize){//单包发送
            ByteBuffer buf=ByteBuffer.allocate(headerSize+payload.length);
            buf.put(VERSION).put(type).put(format).putShort((short)payload.length).put(payload);
            return Arrays.asList(new ProtocolPacket(buf.array(),false,0,1));
        }
        
        //分包发送
        List<ProtocolPacket>packets=new ArrayList<>();
        int totalChunks=(payload.length+maxPayloadSize-1)/maxPayloadSize;
        
        for(int i=0;i<totalChunks;i++){
            int start=i*maxPayloadSize;
            int end=Math.min(start+maxPayloadSize,payload.length);
            int chunkLen=end-start;
            
            ByteBuffer buf=ByteBuffer.allocate(headerSize+chunkLen);
            buf.put(VERSION).put(type).put(format).putShort((short)chunkLen);
            buf.put(payload,start,chunkLen);
            
            packets.add(new ProtocolPacket(buf.array(),true,i,totalChunks));
        }
        
        HiLog.info(LOG,"数据分包:类型="+type+",总包数="+totalChunks+",总大小="+payload.length);
        return packets;
    }

    // 新增心跳包编码
    public static List<ProtocolPacket>encodeHeartbeat(int mtu){//编码心跳包
        try{
            // 心跳包字段定义
            List<byte[]>fields=new ArrayList<>();
            addUint32Field(fields,(byte)0x01,System.currentTimeMillis()/1000); // 时间戳
            addUint8Field(fields,(byte)0x02,(byte)DataManager.getInstance().getStep()); // 电量(用步数代替)
            addUint8Field(fields,(byte)0x03,(byte)DataManager.getInstance().getWearState()); // 佩戴状态
            
            int totalLen=0;for(byte[]f:fields)totalLen+=f.length;
            ByteBuffer buf=ByteBuffer.allocate(totalLen);
            for(byte[]f:fields)buf.put(f);
            
            byte[]payload=buf.array();
            return createPackets(TYPE_HEARTBEAT,FORMAT_BINARY,payload,mtu);
        }catch(Exception e){
            HiLog.error(LOG,"编码心跳包失败:"+e.getMessage());
            return Collections.emptyList();
        }
    }

    // 兼容旧方法，避免编译错误
    private static void addStringField(List<byte[]>fields,byte id,String value){//添加字符串字段
        addStringFieldWithCheck(fields,id,value);
    }
    
    private static void addUint8Field(List<byte[]>fields,byte id,byte value){//添加uint8字段
        addUint8FieldWithCheck(fields,id,value);
    }
    
    private static void addUint16Field(List<byte[]>fields,byte id,short value){//添加uint16字段
        addUint16FieldWithCheck(fields,id,value);
    }

    private static String compactSleepDataEncoding(String sleepDataJson){//sleepData紧凑编码
        if(sleepDataJson==null||sleepDataJson.trim().isEmpty()||sleepDataJson.equals("null")){
            return "0:0:0"; // 空值编码
        }
        
        try{
            JSONObject sleepObj=new JSONObject(sleepDataJson);
            int code=sleepObj.optInt("code",-1);
            
            // 处理错误码或空数据
            if(code!=0){
                return "0:0:0";
            }
            
            JSONArray dataArray=sleepObj.optJSONArray("data");
            if(dataArray==null||dataArray.length()==0){
                return "0:0:0";
            }
            
            // 编码多组睡眠数据
            StringBuilder compact=new StringBuilder();
            for(int i=0;i<dataArray.length();i++){
                if(i>0)compact.append(";");
                
                JSONObject item=dataArray.getJSONObject(i);
                long endTime=item.optLong("endTimeStamp",0);
                long startTime=item.optLong("startTimeStamp",0);
                int type=item.optInt("type",0);
                
                compact.append(endTime).append(":").append(startTime).append(":").append(type);
            }
            
            HiLog.info(LOG,"sleepData紧凑编码: "+sleepDataJson.length()+"字符 -> "+compact.length()+"字符");
            return compact.toString();
        }catch(Exception e){
            HiLog.warn(LOG,"sleepData编码失败,使用默认值: "+e.getMessage());
            return "0:0:0";
        }
    }
} 