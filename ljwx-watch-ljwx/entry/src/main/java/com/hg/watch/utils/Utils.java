package com.hg.watch.utils;
import ohos.hiviewdfx.HiLogLabel;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Random;

import com.tdtech.ohos.mdm.DeviceManager;
import ohos.batterymanager.BatteryInfo;
import ohos.app.Context;
import ohos.hiviewdfx.HiLog;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

/**
 * LogUtils common log print
 *
 * @since 2021-05-29
 */
public class Utils {

    private static final Random random = new Random();
    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "ljwx");
    private static DeviceManager deviceManager;
    private static DataManager dataManager;
    private static BatteryInfo batteryInfo;
    private static String deviceSn;
    private static String customerId;
    private static String apiId;
    private static String lastHealthInfo;
    private static String lastDeviceInfo;
    private static String lastBTHealthInfo;
    private static String lastBTDeviceInfo;
    private static long lastHealthUpdateTime;
    private static long lastDeviceUpdateTime;
    private static final long HEALTH_CACHE_DURATION = 5000; // 5秒缓存
    private static final long DEVICE_CACHE_DURATION = 60000; // 1分钟缓存


    public static void init(Context context) {
        if (deviceManager == null) {
            deviceManager = DeviceManager.getInstance(context);
        }
        if (dataManager == null) {
            dataManager = DataManager.getInstance();
        }
        if (batteryInfo == null) {
            batteryInfo = new BatteryInfo();
        }
    }

    public static int calculateChecksum(String hexString) {
        int sum = 0;

        // 将字符串按每两个字符分割，转换为整数并求和
        for (int i = 0; i < hexString.length(); i += 2) {
            String byteStr = hexString.substring(i, i + 2);
            int value = Integer.parseInt(byteStr, 16);
            sum += value;
        }
        // 取低8位
        return sum & 0xFF;
    }

    public static String generateHealthDataJson() {
        DataManager dataManager = DataManager.getInstance();
        int heartRate = dataManager.getHeartRate();
        int bloodOxygen = dataManager.getBloodOxygen();
        double temperature = dataManager.getTemperature();
        int step = dataManager.getStep();
        int pressureHigh = dataManager.getPressureHigh();
        int pressureLow = dataManager.getPressureLow();

        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("heartRate", heartRate);
            jsonObject.put("bloodOxygen", bloodOxygen);
            jsonObject.put("temperature", temperature);
            jsonObject.put("step", step);
            jsonObject.put("pressureHigh", pressureHigh);
            jsonObject.put("pressureLow", pressureLow);
        } catch (JSONException e) {
            System.err.println("Error creating JSON: " + e.getMessage());
        }
        return jsonObject.toString();
    }


    public static <Int> byte[] encodeHealthData() {
        DataManager dataManager = DataManager.getInstance();
        int heartRate = dataManager.getHeartRate();
        int spo2 = dataManager.getBloodOxygen();
        int pressureHigh = dataManager.getPressureHigh();
        int pressureLow = dataManager.getPressureLow();
        int step = dataManager.getStep();
        double temperature = dataManager.getTemperature();
    
        // 心率: 1 byte
        byte heartRateByte = (byte) heartRate;
    
        // 血氧: 1 byte
        byte spo2Byte = (byte) spo2;
    
        // 血压高压值: 2 bytes, 小端格式
        byte[] pressureHighBytes = new byte[2];
        pressureHighBytes[0] = (byte) (pressureHigh & 0xFF);
        pressureHighBytes[1] = (byte) ((pressureHigh >> 8) & 0xFF);
    
        // 血压低压值: 2 bytes, 小端格式
        byte[] pressureLowBytes = new byte[2];
        pressureLowBytes[0] = (byte) (pressureLow & 0xFF);
        pressureLowBytes[1] = (byte) ((pressureLow >> 8) & 0xFF);

        // 体温: 2 bytes, 小端格式, scaled by 10
        int scaledTemperature = (int) (temperature * 10);
        byte[] temperatureBytes = new byte[2];
        temperatureBytes[0] = (byte) (scaledTemperature & 0xFF);
        temperatureBytes[1] = (byte) ((scaledTemperature >> 8) & 0xFF);

        // 步数: 4 bytes, 小端格式
        byte[] stepBytes = new byte[4];
        stepBytes[0] = (byte) (step & 0xFF);
        stepBytes[1] = (byte) ((step >> 8) & 0xFF);
        stepBytes[2] = (byte) ((step >> 16) & 0xFF);
        stepBytes[3] = (byte) ((step >> 24) & 0xFF);

        // 合并数据部分，确保顺序和格式正确
        byte[] dataPart = new byte[12];
        dataPart[0] = heartRateByte;
        dataPart[1] = spo2Byte;
        System.arraycopy(pressureHighBytes, 0, dataPart, 2, 2);
        System.arraycopy(pressureLowBytes, 0, dataPart, 4, 2);
        System.arraycopy(temperatureBytes, 0, dataPart, 6, 2);
        System.arraycopy(stepBytes, 0, dataPart, 8, 4);

        // 计算校验和
        String dataPartHex = bytesToHex(dataPart);
        String hexString = "6801800C"+ dataPartHex;
        //HiLog.info(LABEL_LOG, " hexString():" + hexString);

        //HiLog.info(LABEL_LOG, " 校验和: %02X\\n" + calculateChecksum(hexString));


        int checksum = calculateChecksum(hexString);
        String checksumHex = String.format("%02X", checksum);
        //HiLog.info(LABEL_LOG, " checksumString)():" + checksum);

        // 组装最终数据
        //String finalDataHex = "FEFE6801800C53007C0055000000000000001916";
        String finalDataHex = "FEFE6801800C" + dataPartHex + checksumHex + "16";
        byte[] finalData = hexStringToByteArray(finalDataHex);

        return finalData;
    }

    public static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02X", b));
        }
        return sb.toString();
    }

    private static byte[] hexStringToByteArray(String s) {
        int len = s.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4)
                                 + Character.digit(s.charAt(i+1), 16));
        }
        return data;
    }



    private static String insertSpaces(String data) {
        StringBuilder spacedData = new StringBuilder();
        for (int i = 0; i < data.length(); i += 2) {
            if (i > 0) {
                spacedData.append(" ");
            }
            spacedData.append(data, i, i + 2);
        }
        return spacedData.toString();
    }


    public static String getDeviceInfo() {
        if (deviceManager == null) {
            HiLog.error(LABEL_LOG, "Utils::getDeviceInfo deviceManager is null");
            return "";
        }

        // 检查缓存是否有效
        long currentTime = System.currentTimeMillis();

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String timestamp = Instant.now().atZone(ZoneId.systemDefault()).format(formatter);

        String deviceInfo = deviceManager.getDeviceInfo();
        try {
            JSONObject deviceInfoJson = new JSONObject(deviceInfo);
            deviceSn = deviceInfoJson.getString("SerialNumber");

            String ipAddress = deviceInfoJson.getString("IP Address");
            if(ipAddress != null && ipAddress.length() > 0){
                deviceInfoJson.put("IP Address", ipAddress.split("\\n")[0]);
            }
            HiLog.info(LABEL_LOG, "Utils::getDeviceInfo ipAddress:" + ipAddress);
            
            // 更新设备信息
            int batteryLevelPercentage = batteryInfo.getCapacity();
            deviceInfoJson.put("batteryLevel", batteryLevelPercentage);
            deviceInfoJson.put("voltage", batteryInfo.getVoltage());
            deviceInfoJson.put("chargingStatus", batteryInfo.getChargingStatus());
            deviceInfoJson.put("status", "ACTIVE");
            deviceInfoJson.put("timestamp", timestamp);
            HiLog.info(LABEL_LOG, "Utils::getDeviceInfo wearState:" + dataManager.getWearState());
            deviceInfoJson.put("wearState", dataManager.getWearState());
            
            deviceInfo = deviceInfoJson.toString();
            dataManager.setDeviceInfo(deviceInfo);
            
            // 更新缓存
            lastDeviceInfo = deviceInfo;
            lastDeviceUpdateTime = currentTime;
            
            return deviceInfo;
        } catch (JSONException e) {
            HiLog.error(LABEL_LOG, "Error updating deviceInfo: " + e.getMessage());
            return deviceInfo;
        }
    }

 

    public static String getHealthInfo() {
        // 检查缓存是否有效
        long currentTime = System.currentTimeMillis();
        
        // 更新缓存时间逻辑，增加随机延迟，避免所有设备同时更新
        long cacheValidDuration = HEALTH_CACHE_DURATION + (long)(Math.random() * 5000);
        
        if (lastHealthInfo != null && (currentTime - lastHealthUpdateTime) < cacheValidDuration) {
            return lastHealthInfo;
        }

        // 如果心率是0，尝试检查缓存是否有效
        if(dataManager.getHeartRate() == 0){
            HiLog.info(LABEL_LOG, "Utils::getHealthInfo 心率为0，可能未正常采集");
            if(lastHealthInfo != null) {
                // 如果缓存间隔不太长，继续使用缓存数据但更新时间戳
                if ((currentTime - lastHealthUpdateTime) < cacheValidDuration * 3) {
                    return updateTimestampInHealthData(lastHealthInfo);
                } else {
                    HiLog.info(LABEL_LOG, "Utils::getHealthInfo 心率为0且缓存已过期，尝试强制更新健康数据");
                }
            }
        }
        
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String timestamp = Instant.now().atZone(ZoneId.systemDefault()).format(formatter);

        JSONObject healthInfoJson = new JSONObject();
        try {
            HiLog.info(LABEL_LOG, "Utils::getHealthInfo dataManager.getDeviceSn():" + dataManager.getDeviceSn());
            healthInfoJson.put("deviceSn", dataManager.getDeviceSn());
           
            
            // 获取健康数据，确保不使用0值(可能表示未采集)
            int heartRate = dataManager.getHeartRate();
            int bloodOxygen = dataManager.getBloodOxygen();
            double temperature = dataManager.getTemperature();
            int pressureHigh = dataManager.getPressureHigh();
            int pressureLow = dataManager.getPressureLow();
            
            // 使用上次有效值替代0值
            if (lastHealthInfo != null && heartRate == 0) {
                try {
                    JSONObject lastData = new JSONObject(lastHealthInfo);
                    JSONObject lastHealthData = lastData.optJSONObject("data");
                    if (lastHealthData != null) {
                        heartRate = lastHealthData.optInt("heart_rate", 0);
                        HiLog.info(LABEL_LOG, "Utils::getHealthInfo 使用上次缓存心率:" + heartRate);
                    }
                } catch (Exception e) {
                    HiLog.error(LABEL_LOG, "解析上次健康数据失败: " + e.getMessage());
                }
            }
            
            healthInfoJson.put("heart_rate", heartRate);
            healthInfoJson.put("blood_oxygen", bloodOxygen);
            healthInfoJson.put("body_temperature", String.format("%.1f", temperature));
           

            healthInfoJson.put("step", dataManager.getStep());
            healthInfoJson.put("distance", String.format("%.1f", dataManager.getDistance()));
            healthInfoJson.put("calorie", String.format("%.1f", dataManager.getCalorie()));

            
            BigDecimal latitude = dataManager.getLatitude();
            BigDecimal longitude = dataManager.getLongitude();
            BigDecimal altitude = dataManager.getAltitude();
            
            healthInfoJson.put("latitude", latitude != null ? latitude.toString() : "0");
            healthInfoJson.put("longitude", longitude != null ? longitude.toString() : "0");
            healthInfoJson.put("altitude", altitude != null ? altitude.toString() : "0");
            healthInfoJson.put("stress", dataManager.getStress());
            
                healthInfoJson.put("upload_method", dataManager.getUploadMethod());
                healthInfoJson.put("blood_pressure_systolic", pressureHigh);
                healthInfoJson.put("blood_pressure_diastolic", pressureLow);
                healthInfoJson.put("sleepData", dataManager.getSleepData() != null ? dataManager.getSleepData() : "null");
                healthInfoJson.put("exerciseDailyData", dataManager.getExerciseDailyData() != null ? dataManager.getExerciseDailyData() : "null");
                healthInfoJson.put("exerciseWeekData", dataManager.getExerciseWeekData() != null ? dataManager.getExerciseWeekData() : "null");
                healthInfoJson.put("scientificSleepData", dataManager.getScientificSleepData() != null ? dataManager.getScientificSleepData() : "null");
                healthInfoJson.put("workoutData", dataManager.getWorkoutData() != null ? dataManager.getWorkoutData() : "null");
            
            healthInfoJson.put("timestamp", timestamp);
            JSONObject resultJson = new JSONObject();
            resultJson.put("data", healthInfoJson);
            
            // 检查返回的健康数据是否有效（心率>0或血氧>0）
            boolean hasValidData = heartRate > 0 || bloodOxygen > 0;
            
            // 更新缓存，仅当数据有效或缓存为空时更新
            if (hasValidData || lastHealthInfo == null) {
                lastHealthInfo = resultJson.toString();
                HiLog.info(LABEL_LOG, "Utils::getHealthInfo 更新健康数据缓存");
                lastHealthUpdateTime = currentTime;
            } else if (lastHealthInfo != null) {
                HiLog.warn(LABEL_LOG, "Utils::getHealthInfo 当前健康数据无效(心率、血氧均为0)，使用缓存数据");
                return updateTimestampInHealthData(lastHealthInfo);
            }
            
            return lastHealthInfo;
        } catch (JSONException e) {
            HiLog.error(LABEL_LOG, "Error creating health info: " + e.getMessage());
            // 发生错误时，尝试返回上次缓存，但更新时间戳
            if (lastHealthInfo != null) {
                return updateTimestampInHealthData(lastHealthInfo);
            }
            return "{}";
        }
    }



    public static void clearCache() {
        lastHealthInfo = null;
        lastDeviceInfo = null;
        lastHealthUpdateTime = 0;
        lastDeviceUpdateTime = 0;
    }

    // 更新健康数据中的timestamp为当前时间
    private static String updateTimestampInHealthData(String healthDataJson) {
        try {
            JSONObject healthJson = new JSONObject(healthDataJson);
            JSONObject dataObj = healthJson.optJSONObject("data");
            if (dataObj != null) {
                DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
                String newTimestamp = Instant.now().atZone(ZoneId.systemDefault()).format(formatter);
                dataObj.put("timestamp", newTimestamp);
                HiLog.info(LABEL_LOG, "Utils::updateTimestampInHealthData 更新时间戳为: " + newTimestamp);
                return healthJson.toString();
            }
        } catch (JSONException e) {
            HiLog.error(LABEL_LOG, "Utils::updateTimestampInHealthData 更新时间戳失败: " + e.getMessage());
        }
        return healthDataJson; // 失败时返回原数据
    }

    /**
     * 解析传入的十六进制字符串，根据协议提取气体浓度
     * @param hexString 十六进制字符串
     * @return 气体浓度的描述
     */
    public static String decodeGas(String hexString) {
        DataManager dataManager = DataManager.getInstance();
        // 移除所有空格并转换为大写
        hexString = hexString.replaceAll("\\s", "").toUpperCase();

        System.out.println("jjgao::decodeGas: simpleMode");

        // 检查同步头和结束标志
        if (!hexString.startsWith("FEFE68") || !hexString.endsWith("16")) {
            return "Invalid data format";
        }

        // 提取数据部分
        String dataPart = hexString.substring(6, hexString.length() - 2);

        // 检查控制码
        String controlCode = dataPart.substring(2, 4);
        if (!controlCode.equals("80")) {
            return "Invalid control code";
        }

        // 检查长度
        String lengthCode = dataPart.substring(4, 6);
        if (lengthCode.equals("0F") || lengthCode.equals("06")) {
            dataManager.setFullMode(lengthCode.equals("0F"));
            System.out.println("jjgao::decodeGas: simpleMode");
            dataManager.setSimpleMode(!lengthCode.equals("0F"));
        }

        // 提取Data部分
        String data = dataPart.substring(6, dataPart.length() );

        System.out.println("jjgao::decodeGas: data" + data);

        // 解析Data部分
        StringBuilder result = new StringBuilder();
        int numberOfSensors = lengthCode.equals("0F") ? 5 : 2; // Full mode has 5 sensors, simple mode has 2 sensors
        for (int i = 0; i < numberOfSensors; i++) {
            int type = Integer.parseInt(data.substring(i * 6, i * 6 + 2), 16);
            int highByte = Integer.parseInt(data.substring(i * 6 + 2, i * 6 + 4), 16);
            int lowByte = Integer.parseInt(data.substring(i * 6 + 4, i * 6 + 6), 16);
            int value = (highByte << 8) + lowByte;

            switch (type) {
                case 1:
                    double ch4Value = value / 100.0;
                    result.append("CH4: ").append(String.format("%.2f", ch4Value)).append(" ");
                    dataManager.setCh4(ch4Value);
                    break;
                case 2:
                    double o2Value = value / 10.0;
                    result.append("O2: ").append(value).append(" ");
                    dataManager.setO2(o2Value );
                    break;
                case 3:
                    if (lengthCode.equals("0F")) {
                        result.append("Co: ").append(value).append("ppm ");
                        dataManager.setCo(value);
                    }
                    break;
                case 4:
                    if (lengthCode.equals("0F")) {
                        double co2Value = value / 100.0;
                        result.append("CO2: ").append(value ).append(" ");
                        dataManager.setCo2(co2Value );
                    }
                    break;
                case 5:
                    if (lengthCode.equals("0F")) {
                        result.append("H2S: ").append(value).append("ppm ");
                        dataManager.setH2s(value);
                    }
                    break;
            }
        }

        return result.toString();
    }

}

