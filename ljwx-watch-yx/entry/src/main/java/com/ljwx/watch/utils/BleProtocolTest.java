package com.ljwx.watch.utils;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import org.json.JSONObject;
import java.util.List;

public class BleProtocolTest {//BLE协议测试工具类
    private static final HiLogLabel LOG=new HiLogLabel(3,0xD001100,"ljwx");
    
    public static void testHealthDataEncoding(){//测试健康数据编码
        try{
            JSONObject health=new JSONObject();
            health.put("id","TEST_DEVICE_001");
            health.put("upload_method","bluetooth");
            health.put("heart_rate",78);
            health.put("blood_oxygen",98);
            health.put("body_temperature","36.5");
            health.put("step",8500);
            health.put("latitude","39.9042");
            health.put("longitude","116.4074");
            health.put("stress",25);
            // 不添加timestamp，测试自动添加功能
            
            HiLog.info(LOG,"原始健康数据JSON长度:"+health.toString().length());
            
            List<BleProtocolEncoder.ProtocolPacket>packets=
                BleProtocolEncoder.encodeHealthData(health.toString(),512);
            
            HiLog.info(LOG,"健康数据编码完成,分包数:"+packets.size());
            
            int totalSize=0;
            for(BleProtocolEncoder.ProtocolPacket packet:packets){
                totalSize+=packet.data.length;
                HiLog.info(LOG,"包大小:"+packet.data.length+"字节");
            }
            
            HiLog.info(LOG,"总传输大小:"+totalSize+"字节");
            HiLog.info(LOG,"压缩率:"+(100-totalSize*100/health.toString().length())+"%");
        }catch(Exception e){
            HiLog.error(LOG,"健康数据编码测试失败:"+e.getMessage());
        }
    }
    
    public static void testDeviceInfoEncoding(){//测试设备信息编码
        try{
            JSONObject device=new JSONObject();
            device.put("System Software Version","HarmonyOS 3.0");
            device.put("Wifi Address","AA:BB:CC:DD:EE:FF");
            device.put("Bluetooth Address","11:22:33:44:55:66");
            device.put("IP Address","192.168.1.100");
            device.put("Network Access Mode",1);
            device.put("SerialNumber","HW123456789");
            device.put("Device Name","智能手表");
            device.put("IMEI","861600076545735");
            device.put("batteryLevel",85);
            device.put("voltage",3800);
            device.put("chargingStatus","NONE");
            device.put("wearState",1);
            // 不添加timestamp，测试自动添加功能
            
            HiLog.info(LOG,"原始设备信息JSON长度:"+device.toString().length());
            
            List<BleProtocolEncoder.ProtocolPacket>packets=
                BleProtocolEncoder.encodeDeviceInfo(device.toString(),512);
            
            HiLog.info(LOG,"设备信息编码完成,分包数:"+packets.size());
            
            int totalSize=0;
            for(BleProtocolEncoder.ProtocolPacket packet:packets){
                totalSize+=packet.data.length;
            }
            
            HiLog.info(LOG,"总传输大小:"+totalSize+"字节");
            HiLog.info(LOG,"压缩率:"+(100-totalSize*100/device.toString().length())+"%");
        }catch(Exception e){
            HiLog.error(LOG,"设备信息编码测试失败:"+e.getMessage());
        }
    }
    
    public static void testCommonEventEncoding(){//测试公共事件编码
        try{
            // 测试1：冒号格式事件
            String event1="SOS:1:HW123456789";
            HiLog.info(LOG,"测试冒号格式事件:"+event1);
            
            List<BleProtocolEncoder.ProtocolPacket>packets1=
                BleProtocolEncoder.encodeCommonEvent(event1,512);
            
            HiLog.info(LOG,"冒号格式编码完成,分包数:"+packets1.size());
            
            // 测试2：JSON格式事件
            String event2="{\"action\":\"com.tdtech.ohos.action.WEAR_STATUS_CHANGED\",\"value\":\"1\",\"device_sn\":\"A5GTQ24821003006\",\"timestamp\":\"2025-05-24 18:45:54\"}";
            HiLog.info(LOG,"测试JSON格式事件:"+event2);
            
            List<BleProtocolEncoder.ProtocolPacket>packets2=
                BleProtocolEncoder.encodeCommonEvent(event2,512);
            
            HiLog.info(LOG,"JSON格式编码完成,分包数:"+packets2.size());
            
            int totalSize=0;
            for(BleProtocolEncoder.ProtocolPacket packet:packets2){
                totalSize+=packet.data.length;
                HiLog.info(LOG,"JSON事件包大小:"+packet.data.length+"字节");
            }
            
            HiLog.info(LOG,"JSON事件总传输大小:"+totalSize+"字节");
            HiLog.info(LOG,"JSON事件压缩率:"+(100-totalSize*100/event2.length())+"%");
        }catch(Exception e){
            HiLog.error(LOG,"公共事件编码测试失败:"+e.getMessage());
        }
    }
    
    public static void testHeartbeatEncoding(){//测试心跳包编码
        try{
            HiLog.info(LOG,"开始心跳包编码测试");
            
            List<BleProtocolEncoder.ProtocolPacket>packets=
                BleProtocolEncoder.encodeHeartbeat(512);
            
            HiLog.info(LOG,"心跳包编码完成,分包数:"+packets.size());
            
            int totalSize=0;
            for(BleProtocolEncoder.ProtocolPacket packet:packets){
                totalSize+=packet.data.length;
                HiLog.info(LOG,"心跳包大小:"+packet.data.length+"字节");
            }
            
            HiLog.info(LOG,"心跳包总传输大小:"+totalSize+"字节");
        }catch(Exception e){
            HiLog.error(LOG,"心跳包编码测试失败:"+e.getMessage());
        }
    }
    
    public static void testHealthDataWithNesting(){//测试嵌套结构的健康数据编码
        try{
            JSONObject data=new JSONObject();
            data.put("id","TEST_DEVICE_001");
            data.put("upload_method","bluetooth");
            data.put("heart_rate",78);
            data.put("blood_oxygen",98);
            data.put("body_temperature","36.5");
            data.put("step",8500);
            data.put("latitude","39.9042");
            data.put("longitude","116.4074");
            data.put("stress",25);
            
            JSONObject root=new JSONObject();
            root.put("data",data);
            
            HiLog.info(LOG,"嵌套健康数据JSON长度:"+root.toString().length());
            
            List<BleProtocolEncoder.ProtocolPacket>packets=
                BleProtocolEncoder.encodeHealthData(root.toString(),512);
            
            HiLog.info(LOG,"嵌套健康数据编码完成,分包数:"+packets.size());
            
            int totalSize=0;
            for(BleProtocolEncoder.ProtocolPacket packet:packets){
                totalSize+=packet.data.length;
            }
            
            HiLog.info(LOG,"嵌套健康数据总传输大小:"+totalSize+"字节");
            HiLog.info(LOG,"嵌套健康数据压缩率:"+(100-totalSize*100/root.toString().length())+"%");
        }catch(Exception e){
            HiLog.error(LOG,"嵌套健康数据编码测试失败:"+e.getMessage());
        }
    }
    
    public static void testHealthDataWithSleepData(){//测试包含sleepData的健康数据编码
        try{
            JSONObject data=new JSONObject();
            data.put("id","TEST_DEVICE_001");
            data.put("upload_method","bluetooth");
            data.put("heart_rate",78);
            data.put("blood_oxygen",98);
            data.put("body_temperature","36.5");
            data.put("step",8500);
            data.put("latitude","39.9042");
            data.put("longitude","116.4074");
            data.put("stress",25);
            // 添加sleepData字段
            data.put("sleepData","{\"code\":0,\"data\":[{\"endTimeStamp\":1747440420000,\"startTimeStamp\":1747418280000,\"type\":2}],\"name\":\"sleep\",\"type\":\"history\"}");
            
            JSONObject root=new JSONObject();
            root.put("data",data);
            
            HiLog.info(LOG,"包含sleepData的健康数据JSON长度:"+root.toString().length());
            
            List<BleProtocolEncoder.ProtocolPacket>packets=
                BleProtocolEncoder.encodeHealthData(root.toString(),512);
            
            HiLog.info(LOG,"包含sleepData的健康数据编码完成,分包数:"+packets.size());
            
            int totalSize=0;
            for(BleProtocolEncoder.ProtocolPacket packet:packets){
                totalSize+=packet.data.length;
            }
            
            HiLog.info(LOG,"包含sleepData的健康数据总传输大小:"+totalSize+"字节");
            HiLog.info(LOG,"包含sleepData的健康数据压缩率:"+(100-totalSize*100/root.toString().length())+"%");
        }catch(Exception e){
            HiLog.error(LOG,"包含sleepData的健康数据编码测试失败:"+e.getMessage());
        }
    }
    
    public static void testComplexSleepDataEncoding(){//测试复杂sleepData的健康数据编码长度
        try{
            JSONObject data=new JSONObject();
            data.put("id","TEST_DEVICE_001");
            data.put("upload_method","bluetooth");
            data.put("heart_rate",78);
            data.put("blood_oxygen",98);
            data.put("body_temperature","36.5");
            data.put("step",8500);
            data.put("latitude","39.9042");
            data.put("longitude","116.4074");
            data.put("stress",25);
            // 添加用户指定的复杂sleepData
            data.put("sleepData","{\"code\":0,\"data\":[{\"endTimeStamp\":1638905820000,\"startTimeStamp\":1638895500000,\"type\":1},{\"endTimeStamp\":1638917160000,\"startTimeStamp\":1638905940000,\"type\":2}],\"name\":\"sleep\",\"type\":\"history\"}");
            
            JSONObject root=new JSONObject();
            root.put("data",data);
            
            String originalJson=root.toString();
            HiLog.info(LOG,"=== 复杂sleepData健康数据编码测试 ===");
            HiLog.info(LOG,"原始JSON长度:"+originalJson.length()+"字符");
            HiLog.info(LOG,"sleepData内容长度:"+data.getString("sleepData").length()+"字符");
            
            List<BleProtocolEncoder.ProtocolPacket>packets=BleProtocolEncoder.encodeHealthData(originalJson,512);
            
            int totalSize=0;
            for(BleProtocolEncoder.ProtocolPacket packet:packets){
                totalSize+=packet.data.length;
                HiLog.info(LOG,"数据包"+(packets.indexOf(packet)+1)+"大小:"+packet.data.length+"字节");
            }
            
            HiLog.info(LOG,"编码完成,分包数:"+packets.size());
            HiLog.info(LOG,"编码后总大小:"+totalSize+"字节");
            HiLog.info(LOG,"压缩率:"+(100-totalSize*100/originalJson.length())+"%");
            HiLog.info(LOG,"原始大小:"+originalJson.length()+"字节 -> 编码后:"+totalSize+"字节");
            HiLog.info(LOG,"=====================================");
        }catch(Exception e){
            HiLog.error(LOG,"复杂sleepData编码测试失败:"+e.getMessage());
        }
    }
    
    public static void testDecoding(){//测试解码功能
        try{
            BleProtocolDecoder decoder=new BleProtocolDecoder();
            
            // 模拟接收到的二进制数据包
            byte[]testPacket={
                1,  // version
                BleProtocolEncoder.TYPE_HEALTH_DATA,  // type
                1,  // format (binary)
                0,10,  // payload length (10 bytes)
                // TLV数据: ID=0x03(heart_rate), LEN=1, VALUE=78
                0x03,1,78,
                // ID=0x04(blood_oxygen), LEN=1, VALUE=98  
                0x04,1,98,
                // ID=0x0E(stress), LEN=1, VALUE=25
                0x0E,1,25
            };
            
            BleProtocolDecoder.DecodedData result=decoder.decode(testPacket);
            if(result!=null&&result.isComplete){
                HiLog.info(LOG,"解码成功:类型="+result.type+",数据="+result.data);
            }else{
                HiLog.warn(LOG,"解码未完成或失败");
            }
        }catch(Exception e){
            HiLog.error(LOG,"解码测试失败:"+e.getMessage());
        }
    }
    
    public static void calculateComplexSleepDataSize(){//手动计算复杂sleepData编码后的大小
        try{
            HiLog.info(LOG,"=== 手动计算复杂sleepData编码大小 ===");
            
            // 构建测试数据
            String sleepDataContent="{\"code\":0,\"data\":[{\"endTimeStamp\":1638905820000,\"startTimeStamp\":1638895500000,\"type\":1},{\"endTimeStamp\":1638917160000,\"startTimeStamp\":1638905940000,\"type\":2}],\"name\":\"sleep\",\"type\":\"history\"}";
            
            // 计算各字段的TLV编码大小
            int totalTlvSize=0;
            
            // 0x01 id: "TEST_DEVICE_001" = 1+1+15 = 17字节
            totalTlvSize+=17;
            HiLog.info(LOG,"id字段: 17字节");
            
            // 0x02 upload_method: "bluetooth" = 1+1+9 = 11字节  
            totalTlvSize+=11;
            HiLog.info(LOG,"upload_method字段: 11字节");
            
            // 0x03 heart_rate: 78 = 1+1+1 = 3字节
            totalTlvSize+=3;
            HiLog.info(LOG,"heart_rate字段: 3字节");
            
            // 0x04 blood_oxygen: 98 = 1+1+1 = 3字节
            totalTlvSize+=3;
            HiLog.info(LOG,"blood_oxygen字段: 3字节");
            
            // 0x05 body_temperature: "36.5" = 1+1+4 = 6字节
            totalTlvSize+=6;
            HiLog.info(LOG,"body_temperature字段: 6字节");
            
            // 0x08 step: 8500 = 1+1+2 = 4字节(uint16)
            totalTlvSize+=4;
            HiLog.info(LOG,"step字段: 4字节");
            
            // 0x0B latitude: "39.9042" = 1+1+7 = 9字节
            totalTlvSize+=9;
            HiLog.info(LOG,"latitude字段: 9字节");
            
            // 0x0C longitude: "116.4074" = 1+1+8 = 10字节
            totalTlvSize+=10;
            HiLog.info(LOG,"longitude字段: 10字节");
            
            // 0x0E stress: 25 = 1+1+1 = 3字节
            totalTlvSize+=3;
            HiLog.info(LOG,"stress字段: 3字节");
            
            // 0x10 sleepData: 复杂JSON字符串
            int sleepDataLen=sleepDataContent.length();
            totalTlvSize+=1+1+sleepDataLen; // ID+长度+内容
            HiLog.info(LOG,"sleepData字段: "+(2+sleepDataLen)+"字节 (内容"+sleepDataLen+"字节)");
            
            // 0x0F timestamp: "2025-01-XX XX:XX:XX" = 1+1+19 = 21字节(自动添加)
            totalTlvSize+=21;
            HiLog.info(LOG,"timestamp字段: 21字节");
            
            // 协议头: 版本(1)+类型(1)+格式(1)+长度(2) = 5字节
            int protocolHeader=5;
            int totalPacketSize=protocolHeader+totalTlvSize;
            
            HiLog.info(LOG,"TLV数据总大小: "+totalTlvSize+"字节");
            HiLog.info(LOG,"协议头大小: "+protocolHeader+"字节");
            HiLog.info(LOG,"完整数据包大小: "+totalPacketSize+"字节");
            
            // 原始JSON大小估算
            String originalJson="{\"data\":{\"id\":\"TEST_DEVICE_001\",\"upload_method\":\"bluetooth\",\"heart_rate\":78,\"blood_oxygen\":98,\"body_temperature\":\"36.5\",\"step\":8500,\"latitude\":\"39.9042\",\"longitude\":\"116.4074\",\"stress\":25,\"sleepData\":\""+sleepDataContent+"\"}}";
            int originalSize=originalJson.length();
            
            HiLog.info(LOG,"原始JSON大小: "+originalSize+"字节");
            HiLog.info(LOG,"压缩率: "+(100-totalPacketSize*100/originalSize)+"%");
            HiLog.info(LOG,"节省空间: "+(originalSize-totalPacketSize)+"字节");
            
            // 分包情况分析(MTU=512)
            int mtu=512;
            int maxPayload=mtu-5-3; // MTU-协议头-ATT开销
            int packetCount=(totalTlvSize+maxPayload-1)/maxPayload;
            HiLog.info(LOG,"MTU="+mtu+"时分包数: "+packetCount+"包");
            
            HiLog.info(LOG,"=====================================");
        }catch(Exception e){
            HiLog.error(LOG,"手动计算编码大小失败:"+e.getMessage());
        }
    }
    
    public static void calculateUserSleepDataSize(){//精确计算用户sleepData的编码长度
        HiLog.info(LOG,"=== 精确计算用户sleepData编码长度 ===");
        
        // 用户提供的sleepData内容
        String userSleepData="{\"code\":0,\"data\":[{\"endTimeStamp\":1638905820000,\"startTimeStamp\":1638895500000,\"type\":1},{\"endTimeStamp\":1638917160000,\"startTimeStamp\":1638905940000,\"type\":2}],\"name\":\"sleep\",\"type\":\"history\"}";
        
        HiLog.info(LOG,"用户sleepData内容长度: "+userSleepData.length()+"字符");
        HiLog.info(LOG,"sleepData内容: "+userSleepData);
        
        // 计算完整健康数据的TLV编码大小
        int tlvSize=0;
        
        // 基础字段编码大小(固定部分)
        tlvSize+=17; // id: "TEST_DEVICE_001" (1+1+15)
        tlvSize+=11; // upload_method: "bluetooth" (1+1+9)  
        tlvSize+=3;  // heart_rate: 78 (1+1+1)
        tlvSize+=3;  // blood_oxygen: 98 (1+1+1)
        tlvSize+=6;  // body_temperature: "36.5" (1+1+4)
        tlvSize+=4;  // step: 8500 (1+1+2, uint16)
        tlvSize+=9;  // latitude: "39.9042" (1+1+7)
        tlvSize+=10; // longitude: "116.4074" (1+1+8)
        tlvSize+=3;  // stress: 25 (1+1+1)
        tlvSize+=21; // timestamp: "2025-01-XX XX:XX:XX" (1+1+19, 自动添加)
        
        // sleepData字段编码大小
        int sleepDataTlvSize=1+1+userSleepData.length(); // ID(1) + Length(1) + Content
        tlvSize+=sleepDataTlvSize;
        
        HiLog.info(LOG,"基础字段TLV大小: "+(tlvSize-sleepDataTlvSize)+"字节");
        HiLog.info(LOG,"sleepData字段TLV大小: "+sleepDataTlvSize+"字节");
        HiLog.info(LOG,"总TLV数据大小: "+tlvSize+"字节");
        
        // 协议头大小: 版本(1)+类型(1)+格式(1)+长度(2)
        int headerSize=5;
        int totalPacketSize=headerSize+tlvSize;
        
        HiLog.info(LOG,"协议头大小: "+headerSize+"字节");
        HiLog.info(LOG,"完整数据包大小: "+totalPacketSize+"字节");
        
        // 原始JSON大小计算
        String completeJson="{\"data\":{\"id\":\"TEST_DEVICE_001\",\"upload_method\":\"bluetooth\",\"heart_rate\":78,\"blood_oxygen\":98,\"body_temperature\":\"36.5\",\"step\":8500,\"latitude\":\"39.9042\",\"longitude\":\"116.4074\",\"stress\":25,\"sleepData\":\""+userSleepData.replace("\"","\\\"")+"\",\"timestamp\":\"2025-01-15 10:30:45\"}}";
        
        HiLog.info(LOG,"原始JSON大小: "+completeJson.length()+"字节");
        HiLog.info(LOG,"压缩效果: "+completeJson.length()+"字节 -> "+totalPacketSize+"字节");
        HiLog.info(LOG,"压缩率: "+(100-totalPacketSize*100/completeJson.length())+"%");
        HiLog.info(LOG,"节省: "+(completeJson.length()-totalPacketSize)+"字节");
        
        // 分包分析
        int mtu=512;
        int effectivePayload=mtu-5-3; // 减去协议头和ATT开销
        int packetCount=(tlvSize+effectivePayload-1)/effectivePayload;
        
        HiLog.info(LOG,"MTU "+mtu+"字节时:");
        HiLog.info(LOG,"  有效载荷: "+effectivePayload+"字节/包");
        HiLog.info(LOG,"  需要分包数: "+packetCount+"包");
        
        if(packetCount>1){
            HiLog.info(LOG,"  第1包: "+Math.min(effectivePayload,tlvSize)+"字节数据");
            if(tlvSize>effectivePayload){
                HiLog.info(LOG,"  第2包: "+(tlvSize-effectivePayload)+"字节数据");
            }
        }
        
        HiLog.info(LOG,"=====================================");
    }
    
    public static void testCompactSleepDataEncoding(){//测试紧凑sleepData编码格式
        HiLog.info(LOG,"=== 测试紧凑sleepData编码(240字节限制) ===");
        
        // 原始sleepData JSON格式
        String originalSleepData="{\"code\":0,\"data\":[{\"endTimeStamp\":1638905820000,\"startTimeStamp\":1638895500000,\"type\":1},{\"endTimeStamp\":1638917160000,\"startTimeStamp\":1638905940000,\"type\":2}],\"name\":\"sleep\",\"type\":\"history\"}";
        
        // 紧凑编码格式: endTimeStamp:startTimeStamp:type
        String compactSleepData="1638905820000:1638895500000:1;1638917160000:1638905940000:2";
        
        HiLog.info(LOG,"原始sleepData长度: "+originalSleepData.length()+"字符");
        HiLog.info(LOG,"紧凑sleepData长度: "+compactSleepData.length()+"字符");
        HiLog.info(LOG,"压缩率: "+(100-compactSleepData.length()*100/originalSleepData.length())+"%");
        
        // 计算基础字段的TLV大小(不含sleepData)
        int baseTlvSize=0;
        baseTlvSize+=17; // id: "TEST_DEVICE_001"
        baseTlvSize+=11; // upload_method: "bluetooth"
        baseTlvSize+=3;  // heart_rate: 78
        baseTlvSize+=3;  // blood_oxygen: 98
        baseTlvSize+=6;  // body_temperature: "36.5"
        baseTlvSize+=4;  // step: 8500
        baseTlvSize+=9;  // latitude: "39.9042"
        baseTlvSize+=10; // longitude: "116.4074"
        baseTlvSize+=3;  // stress: 25
        baseTlvSize+=21; // timestamp: "2025-01-XX XX:XX:XX"
        
        int headerSize=5; // 协议头
        int basePacketSize=headerSize+baseTlvSize;
        
        HiLog.info(LOG,"基础数据包大小(不含sleepData): "+basePacketSize+"字节");
        
        // 计算紧凑sleepData的TLV大小
        int compactSleepTlvSize=1+1+compactSleepData.length(); // ID+Length+Content
        int totalWithCompactSleep=basePacketSize+compactSleepTlvSize;
        
        HiLog.info(LOG,"紧凑sleepData TLV大小: "+compactSleepTlvSize+"字节");
        HiLog.info(LOG,"包含紧凑sleepData的总大小: "+totalWithCompactSleep+"字节");
        
        // 计算240字节限制下的可用空间
        int targetLimit=240;
        int availableForSleepData=targetLimit-basePacketSize-2; // 减去sleepData的ID和Length字节
        
        HiLog.info(LOG,"240字节限制下可用于sleepData内容: "+availableForSleepData+"字节");
        
        // 分析单组睡眠数据的大小
        String singleSleepEntry="1638905820000:1638895500000:1"; // 单组数据
        int singleEntrySize=singleSleepEntry.length();
        String separator=";"; // 分隔符
        
        HiLog.info(LOG,"单组睡眠数据大小: "+singleEntrySize+"字符");
        HiLog.info(LOG,"分隔符大小: "+separator.length()+"字符");
        
        // 计算最大支持的组数
        // 公式: n*singleEntrySize + (n-1)*separatorSize <= availableForSleepData
        // 即: n*(singleEntrySize + separatorSize) - separatorSize <= availableForSleepData
        int entryWithSeparatorSize=singleEntrySize+separator.length();
        int maxGroups=(availableForSleepData+separator.length())/entryWithSeparatorSize;
        
        // 验证计算结果
        int actualSizeForMaxGroups=maxGroups*singleEntrySize+(maxGroups-1)*separator.length();
        int finalPacketSize=basePacketSize+2+actualSizeForMaxGroups; // +2为sleepData的ID和Length
        
        HiLog.info(LOG,"最大支持组数: "+maxGroups+"组");
        HiLog.info(LOG,""+maxGroups+"组数据实际大小: "+actualSizeForMaxGroups+"字符");
        HiLog.info(LOG,"最终数据包大小: "+finalPacketSize+"字节");
        HiLog.info(LOG,"是否满足240字节限制: "+(finalPacketSize<=targetLimit?"是":"否"));
        
        // 生成示例数据
        StringBuilder exampleSleepData=new StringBuilder();
        for(int i=0;i<Math.min(maxGroups,5);i++){ // 最多显示5组示例
            if(i>0)exampleSleepData.append(";");
            long baseTime=1638905820000L+i*3600000; // 每组间隔1小时
            exampleSleepData.append(baseTime).append(":").append(baseTime-10320000).append(":").append((i%2)+1);
        }
        
        HiLog.info(LOG,"示例紧凑sleepData(前5组): "+exampleSleepData.toString());
        
        // 对比原始JSON方式
        HiLog.info(LOG,"--- 对比分析 ---");
        HiLog.info(LOG,"原始JSON方式: 2组数据 = "+originalSleepData.length()+"字符, 总包大小="+(basePacketSize+2+originalSleepData.length())+"字节");
        HiLog.info(LOG,"紧凑编码方式: "+maxGroups+"组数据 = "+actualSizeForMaxGroups+"字符, 总包大小="+finalPacketSize+"字节");
        HiLog.info(LOG,"数据容量提升: "+(maxGroups/2.0)+"倍");
        
        HiLog.info(LOG,"=====================================");
    }
    
    public static void testSleepDataCompactEncoding(){//测试sleepData紧凑编码功能
        HiLog.info(LOG,"=== 测试sleepData紧凑编码功能 ===");
        
        // 测试用例1: null值
        testSleepDataCase("null值","null","0:0:0");
        
        // 测试用例2: 错误码
        testSleepDataCase("错误码","{\"code\":-1}","0:0:0");
        
        // 测试用例3: 空数据数组
        testSleepDataCase("空数据","{\"code\":0,\"data\":[]}","0:0:0");
        
        // 测试用例4: 单组数据
        String singleData="{\"code\":0,\"data\":[{\"endTimeStamp\":1747440420000,\"startTimeStamp\":1747418280000,\"type\":2}]}";
        testSleepDataCase("单组数据",singleData,"1747440420000:1747418280000:2");
        
        // 测试用例5: 多组数据
        String multiData="{\"code\":0,\"data\":[{\"endTimeStamp\":1638905820000,\"startTimeStamp\":1638895500000,\"type\":1},{\"endTimeStamp\":1638917160000,\"startTimeStamp\":1638905940000,\"type\":2}],\"name\":\"sleep\",\"type\":\"history\"}";
        testSleepDataCase("多组数据",multiData,"1638905820000:1638895500000:1;1638917160000:1638905940000:2");
        
        // 测试完整健康数据编码
        testCompleteHealthDataWithCompactSleep();
        
        HiLog.info(LOG,"=====================================");
    }
    
    private static void testSleepDataCase(String caseName,String input,String expected){//测试单个sleepData编码用例
        try{
            JSONObject data=new JSONObject();
            data.put("id","TEST_DEVICE");
            data.put("sleepData",input);
            
            JSONObject root=new JSONObject();
            root.put("data",data);
            
            List<BleProtocolEncoder.ProtocolPacket>packets=BleProtocolEncoder.encodeHealthData(root.toString(),512);
            
            HiLog.info(LOG,"测试"+caseName+": 输入长度="+input.length()+", 编码包数="+packets.size());
            if(!packets.isEmpty()){
                HiLog.info(LOG,"  编码后包大小: "+packets.get(0).data.length+"字节");
            }
        }catch(Exception e){
            HiLog.error(LOG,"测试"+caseName+"失败: "+e.getMessage());
        }
    }
    
    private static void testCompleteHealthDataWithCompactSleep(){//测试完整健康数据的紧凑编码
        try{
            JSONObject data=new JSONObject();
            data.put("id","TEST_DEVICE_001");
            data.put("upload_method","bluetooth");
            data.put("heart_rate",78);
            data.put("blood_oxygen",98);
            data.put("body_temperature","36.5");
            data.put("step",8500);
            data.put("latitude","39.9042");
            data.put("longitude","116.4074");
            data.put("stress",25);
            
            // 使用多组睡眠数据测试
            String multiSleepData="{\"code\":0,\"data\":[{\"endTimeStamp\":1638905820000,\"startTimeStamp\":1638895500000,\"type\":1},{\"endTimeStamp\":1638917160000,\"startTimeStamp\":1638905940000,\"type\":2},{\"endTimeStamp\":1638920720000,\"startTimeStamp\":1638910400000,\"type\":1}]}";
            data.put("sleepData",multiSleepData);
            
            JSONObject root=new JSONObject();
            root.put("data",data);
            
            String originalJson=root.toString();
            List<BleProtocolEncoder.ProtocolPacket>packets=BleProtocolEncoder.encodeHealthData(originalJson,512);
            
            int totalSize=0;
            for(BleProtocolEncoder.ProtocolPacket packet:packets){
                totalSize+=packet.data.length;
            }
            
            HiLog.info(LOG,"--- 完整健康数据紧凑编码测试 ---");
            HiLog.info(LOG,"原始JSON大小: "+originalJson.length()+"字节");
            HiLog.info(LOG,"编码后总大小: "+totalSize+"字节");
            HiLog.info(LOG,"压缩率: "+(100-totalSize*100/originalJson.length())+"%");
            HiLog.info(LOG,"分包数: "+packets.size());
            HiLog.info(LOG,"是否满足240字节限制: "+(totalSize<=240?"是":"否"));
        }catch(Exception e){
            HiLog.error(LOG,"完整健康数据测试失败: "+e.getMessage());
        }
    }
    
    public static void testSleepDataCompactEncodingSimple(){//简单测试sleepData紧凑编码
        HiLog.info(LOG,"=== 简单测试sleepData紧凑编码 ===");
        
        // 测试用例：用户提供的多组数据
        String multiSleepData="{\"code\":0,\"data\":[{\"endTimeStamp\":1638905820000,\"startTimeStamp\":1638895500000,\"type\":1},{\"endTimeStamp\":1638917160000,\"startTimeStamp\":1638905940000,\"type\":2}],\"name\":\"sleep\",\"type\":\"history\"}";
        
        // 构建完整健康数据
        JSONObject data=new JSONObject();
        data.put("id","TEST_DEVICE_001");
        data.put("upload_method","bluetooth");
        data.put("heart_rate",78);
        data.put("blood_oxygen",98);
        data.put("body_temperature","36.5");
        data.put("step",8500);
        data.put("latitude","39.9042");
        data.put("longitude","116.4074");
        data.put("stress",25);
        data.put("sleepData",multiSleepData);
        
        JSONObject root=new JSONObject();
        root.put("data",data);
        
        String originalJson=root.toString();
        
        // 编码测试
        List<BleProtocolEncoder.ProtocolPacket>packets=BleProtocolEncoder.encodeHealthData(originalJson,512);
        
        int totalSize=0;
        for(BleProtocolEncoder.ProtocolPacket packet:packets){
            totalSize+=packet.data.length;
        }
        
        HiLog.info(LOG,"原始JSON长度: "+originalJson.length()+"字符");
        HiLog.info(LOG,"sleepData原始长度: "+multiSleepData.length()+"字符");
        HiLog.info(LOG,"编码后总大小: "+totalSize+"字节");
        HiLog.info(LOG,"分包数: "+packets.size());
        HiLog.info(LOG,"是否满足240字节限制: "+(totalSize<=240?"✅ 是":"❌ 否"));
        
        // 计算压缩率
        int compressionRate=100-totalSize*100/originalJson.length();
        HiLog.info(LOG,"整体压缩率: "+compressionRate+"%");
        
        // 预期紧凑编码结果
        String expectedCompact="1638905820000:1638895500000:1;1638917160000:1638905940000:2";
        HiLog.info(LOG,"预期紧凑编码: "+expectedCompact+" ("+expectedCompact.length()+"字符)");
        HiLog.info(LOG,"sleepData压缩率: "+(100-expectedCompact.length()*100/multiSleepData.length())+"%");
        
        HiLog.info(LOG,"=====================================");
    }
    
    public static void runAllTests(){//运行所有测试
        HiLog.info(LOG,"开始BLE协议测试...");
        testHealthDataEncoding();
        testDeviceInfoEncoding();
        testCommonEventEncoding();
        testHeartbeatEncoding();
        testHealthDataWithNesting();
        testHealthDataWithSleepData();
        testComplexSleepDataEncoding();
        testDecoding();
        calculateComplexSleepDataSize();
        calculateUserSleepDataSize();
        testCompactSleepDataEncoding();
        testSleepDataCompactEncoding(); // 新增紧凑编码测试
        testSleepDataCompactEncodingSimple(); // 新增简单紧凑编码测试
        HiLog.info(LOG,"BLE协议测试完成");
    }
} 