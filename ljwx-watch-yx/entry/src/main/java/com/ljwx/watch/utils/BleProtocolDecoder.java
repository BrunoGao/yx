package com.ljwx.watch.utils;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import org.json.JSONObject;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class BleProtocolDecoder {//BLE协议解码器，解析二进制TLV格式数据
    private static final HiLogLabel LOG=new HiLogLabel(3,0xD001100,"ljwx");
    private final Map<Byte,Map<Integer,byte[]>>chunkBuffer=new ConcurrentHashMap<>();//分包缓冲区
    private final Map<Byte,Long>lastReceiveTime=new ConcurrentHashMap<>();//最后接收时间
    private static final long TIMEOUT_MS=10000;//分包超时时间
    
    public static class DecodedData{//解码后的数据
        public final byte type;public final String data;public final boolean isComplete;
        public DecodedData(byte type,String data,boolean isComplete){
            this.type=type;this.data=data;this.isComplete=isComplete;
        }
    }
    
    public DecodedData decode(byte[]packet){//解码数据包
        try{
            if(packet.length<5)return null;//最小包头大小
            
            ByteBuffer buf=ByteBuffer.wrap(packet);
            byte version=buf.get();
            if(version!=1){
                HiLog.error(LOG,"不支持的协议版本:"+version);
                return null;
            }
            
            byte type=buf.get();
            byte format=buf.get();
            short payloadLen=buf.getShort();
            
            if(payloadLen<0||payloadLen>packet.length-5){
                HiLog.error(LOG,"无效的载荷长度:"+payloadLen);
                return null;
            }
            
            byte[]payload=new byte[payloadLen];
            buf.get(payload);
            
            //检查是否为分包数据
            if(isChunkedData(type,payload)){
                return handleChunkedData(type,format,payload);
            }else{
                return new DecodedData(type,decodePayload(format,payload),true);
            }
        }catch(Exception e){
            HiLog.error(LOG,"解码数据包失败:"+e.getMessage());
            return null;
        }
    }
    
    private boolean isChunkedData(byte type,byte[]payload){//判断是否为分包数据
        //简单启发式判断:如果载荷很小且类型为常见数据类型，可能是分包
        return payload.length<100&&(type==BleProtocolEncoder.TYPE_HEALTH_DATA||
            type==BleProtocolEncoder.TYPE_DEVICE_INFO);
    }
    
    private DecodedData handleChunkedData(byte type,byte format,byte[]payload){//处理分包数据
        try{
            //假设分包索引在payload前两个字节
            if(payload.length<2)return null;
            
            int chunkIndex=payload[0]&0xFF;
            int totalChunks=payload[1]&0xFF;
            
            if(chunkIndex>=totalChunks||totalChunks<=0)return null;
            
            byte[]chunkData=Arrays.copyOfRange(payload,2,payload.length);
            
            //获取或创建该类型的缓冲区
            Map<Integer,byte[]>typeBuffer=chunkBuffer.computeIfAbsent(type,k->new ConcurrentHashMap<>());
            typeBuffer.put(chunkIndex,chunkData);
            lastReceiveTime.put(type,System.currentTimeMillis());
            
            HiLog.debug(LOG,"接收分包:类型="+type+",索引="+(chunkIndex+1)+"/"+totalChunks);
            
            //检查是否接收完整
            if(typeBuffer.size()==totalChunks){
                byte[]completeData=mergeChunks(typeBuffer,totalChunks);
                typeBuffer.clear();
                lastReceiveTime.remove(type);
                
                if(completeData!=null){
                    HiLog.info(LOG,"分包合并完成:类型="+type+",总大小="+completeData.length);
                    return new DecodedData(type,decodePayload(format,completeData),true);
                }
            }
            
            return new DecodedData(type,"",false);//分包未完成
        }catch(Exception e){
            HiLog.error(LOG,"处理分包数据失败:"+e.getMessage());
            return null;
        }
    }
    
    private byte[]mergeChunks(Map<Integer,byte[]>chunks,int totalChunks){//合并分包数据
        try{
            int totalSize=0;
            for(byte[]chunk:chunks.values())totalSize+=chunk.length;
            
            ByteBuffer result=ByteBuffer.allocate(totalSize);
            for(int i=0;i<totalChunks;i++){
                byte[]chunk=chunks.get(i);
                if(chunk==null){
                    HiLog.error(LOG,"缺失分包:"+i);
                    return null;
                }
                result.put(chunk);
            }
            
            return result.array();
        }catch(Exception e){
            HiLog.error(LOG,"合并分包失败:"+e.getMessage());
            return null;
        }
    }
    
    private String decodePayload(byte format,byte[]payload){//解码载荷数据
        try{
            if(format==1){//二进制TLV格式
                return decodeTLV(payload);
            }else if(format==2){//JSON格式
                return new String(payload,StandardCharsets.UTF_8);
            }else{
                HiLog.error(LOG,"不支持的数据格式:"+format);
                return "";
            }
        }catch(Exception e){
            HiLog.error(LOG,"解码载荷失败:"+e.getMessage());
            return "";
        }
    }
    
    private String decodeTLV(byte[]tlvData){//解码TLV数据为JSON
        try{
            JSONObject result=new JSONObject();
            ByteBuffer buf=ByteBuffer.wrap(tlvData);
            
            while(buf.hasRemaining()){
                if(buf.remaining()<2)break;
                
                byte id=buf.get();
                byte len=buf.get();
                
                if(len<=0||buf.remaining()<len)break;
                
                byte[]value=new byte[len];
                buf.get(value);
                
                String fieldName=getFieldName(id);
                if(fieldName!=null){
                    if(len==1){//uint8
                        result.put(fieldName,value[0]&0xFF);
                    }else if(len==2){//uint16
                        result.put(fieldName,ByteBuffer.wrap(value).getShort()&0xFFFF);
                    }else{//字符串
                        result.put(fieldName,new String(value,StandardCharsets.UTF_8));
                    }
                }
            }
            
            return result.toString();
        }catch(Exception e){
            HiLog.error(LOG,"解码TLV失败:"+e.getMessage());
            return "{}";
        }
    }
    
    private String getFieldName(byte id){//根据字段ID获取字段名
        switch(id){
            //健康数据字段
            case 0x01:return"id";
            case 0x02:return"upload_method";
            case 0x03:return"heart_rate";
            case 0x04:return"blood_oxygen";
            case 0x05:return"body_temperature";
            case 0x06:return"blood_pressure_systolic";
            case 0x07:return"blood_pressure_diastolic";
            case 0x08:return"step";
            case 0x09:return"distance";
            case 0x0A:return"calorie";
            case 0x0B:return"latitude";
            case 0x0C:return"longitude";
            case 0x0D:return"altitude";
            case 0x0E:return"stress";
            case 0x0F:return"timestamp";
            //设备信息字段(使用相同ID空间，通过类型区分)
            default:
                HiLog.warn(LOG,"未知字段ID:"+id);
                return"field_"+id;
        }
    }
    
    public void cleanupExpiredChunks(){//清理过期的分包数据
        long now=System.currentTimeMillis();
        Iterator<Map.Entry<Byte,Long>>it=lastReceiveTime.entrySet().iterator();
        
        while(it.hasNext()){
            Map.Entry<Byte,Long>entry=it.next();
            if(now-entry.getValue()>TIMEOUT_MS){
                byte type=entry.getKey();
                chunkBuffer.remove(type);
                it.remove();
                HiLog.warn(LOG,"清理过期分包:类型="+type);
            }
        }
    }
} 