package com.hg.watch;


import com.hg.watch.utils.Utils;
import ohos.aafwk.ability.Ability;
import ohos.aafwk.content.Intent;
import ohos.app.Context;
import com.tdtech.ohos.mdm.DeviceManager;
import ohos.batterymanager.BatteryInfo;
import ohos.data.DatabaseHelper;
import ohos.data.preferences.Preferences;
import ohos.event.notification.NotificationHelper;
import ohos.event.notification.NotificationRequest;
import ohos.rpc.IRemoteObject;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Timer;
import java.util.TimerTask;
import java.nio.charset.StandardCharsets;
import com.hg.watch.utils.DataManager;
import ohos.rpc.RemoteException;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONArray;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.lang.Thread;
import java.util.Iterator;


public class HttpService extends Ability {
    private static HttpService instance;
    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "ljwx-log");

    // 统一的基础URL
    //private static final String BASE_URL = "https://www.heguang-tech.cn:5001";

    //private static final String BASE_URL = "http://www.lingjingwanxiang.com:5001";
    //private static final String BASE_URL = "http://www.lingjingwanxiang.com:5001";
    private static final String BASE_URL = "http://172.16.130.100:8001";
    

    // 数据管理器
    private DataManager dataManager = DataManager.getInstance();

    // 设备管理器
    private DeviceManager deviceManager = null;

    // 设备信息
    private String deviceSn = "";
    private String customerId = "0";
    private String customerName = "富力通";
    private String currentDeviceInfo = "";
    private String lastDeviceInfo = "";

    // API认证信息
    private String apiId = "";
    private String apiAuthorization = "";

    // 接口URL
    private String platformUrl = null;
    private String fetchMessageUrl = null;
    private String uploadDeviceUrl = null;
    private String uploadCommonEventUrl = null;
    private String fetchConfigUrl = null;

    // 接口间隔时间（秒）
    private int fetchConfigInterval = 0;
    private int uploadHealthInterval = 600;
    private int uploadDeviceInterval = 18000;
    private int fetchMessageInterval = 60;
    private int uploadCommonEventInterval = 0;

    // 接口启用状态
    private boolean fetchMessageEnabled = false;
    private boolean uploadHealthEnabled = true;
    private boolean uploadDeviceEnabled = true;
    private boolean uploadCommonEventEnabled = false;
    private boolean fetchConfigEnabled = false;

    // 通知ID
    private static int notificationId = 2000;

    // 电池信息
    private BatteryInfo batteryInfo;

    // 消息类型映射
    private static final Map<String, String> MESSAGE_TYPE_MAP = new HashMap<>();
    static {
        MESSAGE_TYPE_MAP.put("announcement", "公告");
        MESSAGE_TYPE_MAP.put("notification", "个人通知");
        MESSAGE_TYPE_MAP.put("warning", "告警");
        MESSAGE_TYPE_MAP.put("job", "作业指引");
        MESSAGE_TYPE_MAP.put("task", "任务管理");
    }

    // 定时器
    private Timer masterHttpTimer; // 统一主定时器
    private long httpTick = 0; // HTTP计数器
    private final int baseHttpPeriod = 5; // 基础周期60秒

    private static String lastHealthInfo;

    private static String lastBTHealthInfo;
    private static String lastBTDeviceInfo;
    private static long lastHealthUpdateTime;
    private static long lastDeviceUpdateTime;
    private static final long HEALTH_CACHE_DURATION = 5000; // 5秒缓存
    private static final long DEVICE_CACHE_DURATION = 60000; // 1分钟缓存

    // Preferences缓存
    private Preferences preferences;

    private HealthDataCache healthDataCache;

    public HttpService() {
        // 注册属性变化监听器
        dataManager.addPropertyChangeListener(evt -> {
            HiLog.info(LABEL_LOG, "PropertyChangeListener:" + evt.getPropertyName());
            if("wearState".equals(evt.getPropertyName())){
                HiLog.info(LABEL_LOG, "HttpService:: uploadDeviceInfo by wearState change" + dataManager.getWearState());
                uploadDeviceInfo();
            }else if("commonEvent".equals(evt.getPropertyName())){
                String commonEvent = dataManager.getCommonEvent();
                HiLog.info(LABEL_LOG, "HttpService::onPropertyChange commonEvent: " + commonEvent);
                uploadCommonEvent(commonEvent);
            }else if("config".equals(evt.getPropertyName())){
                HiLog.info(LABEL_LOG, "HttpService::onPropertyChange got config, initHttpParameters");
                //initHttpParameters();
                //startTimers();
            }
        });

        healthDataCache = HealthDataCache.getInstance();
    }


    @Override
    public void onStart(Intent intent) {
        HiLog.info(LABEL_LOG, "HttpService::onStart");
        super.onStart(intent);
        
        // 初始化Utils
        Utils.init(getContext());
        
        // 设置后台运行通知
        setupBackgroundNotification();
        startTimers();
        showNotification("启动http服务");
    }

    // 设置后台运行通知
    private void setupBackgroundNotification() {
        NotificationRequest request = new NotificationRequest(1005);
        NotificationRequest.NotificationNormalContent content = new NotificationRequest.NotificationNormalContent();
        content.setTitle("HttpService").setText("keepServiceAlive");
        NotificationRequest.NotificationContent notificationContent = new NotificationRequest.NotificationContent(content);
        request.setContent(notificationContent);

        // 绑定通知
        keepBackgroundRunning(1005, request);

        // 获取通知ID
        String storedNotificationId = fetchValue("notificationId");
        if (storedNotificationId.isEmpty()) {
            notificationId = 2000; // 默认值
            storeValue("notificationId", String.valueOf(notificationId));
        } else {
            notificationId = Integer.parseInt(storedNotificationId);
        }
    }


    // 启动定时任务
    private void startTimers() {
        HiLog.info(LABEL_LOG, "HttpService::startTimers");
        HiLog.info(LABEL_LOG, "HttpService::startTimers uploadDeviceInterval: " + dataManager.getUploadDeviceInterval());
        HiLog.info(LABEL_LOG, "HttpService::startTimers uploadHealthInterval: " + dataManager.getUploadHealthInterval());
        HiLog.info(LABEL_LOG, "HttpService::startTimers fetchMessageInterval: " + dataManager.getFetchMessageInterval());
        HiLog.info(LABEL_LOG, "HttpService::startTimers uploadCommonEventInterval: " + dataManager.getUploadCommonEventInterval());
        HiLog.info(LABEL_LOG, "HttpService::startTimers fetchConfigInterval: " + dataManager.getFetchConfigInterval());

        // 统一定时器调度 - 60秒基础周期
        if ("wifi".equals(dataManager.getUploadMethod())) {
            masterHttpTimer = new Timer();
            int uploadHealthInterval = dataManager.getUploadHealthInterval();
            int uploadDeviceInterval = dataManager.getUploadDeviceInterval();
            int fetchMessageInterval = dataManager.getFetchMessageInterval();
            int uploadCommonEventInterval = dataManager.getUploadCommonEventInterval();
            int fetchConfigInterval = dataManager.getFetchConfigInterval();
            
            masterHttpTimer.schedule(new TimerTask() {
                @Override
                public void run() {
                    httpTick++;
                    // 上传健康数据 - 每10分钟执行
                    if (uploadHealthInterval > 0 && httpTick % (uploadHealthInterval / baseHttpPeriod) == 0) {
                        HiLog.info(LABEL_LOG, "HttpService::masterTimer 执行健康数据批量上传");
                        uploadHealthData();
                    }
                    // 上传设备信息 - 根据配置周期执行
                    if (uploadDeviceInterval> 0 && httpTick % (uploadDeviceInterval / baseHttpPeriod) == 0) {
                        uploadDeviceInfo();
                    }
                    // 获取消息 - 根据配置周期执行
                    if (fetchMessageInterval > 0 && httpTick % (fetchMessageInterval / baseHttpPeriod) == 0) {
                        fetchMessageFromServer();
                    }
                    // 防止计数器溢出
                    if (httpTick >= 1440) httpTick = 0; // 24小时重置
                }
            }, 0, baseHttpPeriod * 1000);
        } else {
            HiLog.warn(LABEL_LOG, "HttpService::startTimers 非WiFi模式，跳过定时器启动");
        }
    }


    // 上传数据
    private boolean uploadData(String targetUrl, String data) {
        HiLog.info(LABEL_LOG, "HttpService::uploadData :: targetUrl: " + targetUrl);
        HiLog.info(LABEL_LOG, "HttpService::uploadData :: data: " + data.substring(0, Math.min(200, data.length())));
        boolean result = false;
        HttpURLConnection connection = null;
        try {
            URL url = new URL(targetUrl);
            connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(10000); // 10秒连接超时
            connection.setReadTimeout(10000);    // 10秒读取超时
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
            connection.setRequestProperty("Accept", "application/json");
            connection.setRequestProperty("Authorization", dataManager.getApiAuthorization());
            connection.setDoOutput(true);

            try (OutputStream os = connection.getOutputStream()) {
                byte[] input = data.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
                os.flush();
            }

            int responseCode = connection.getResponseCode();
            HiLog.info(LABEL_LOG, "HttpService::uploadData :: POST Response Code :: " + responseCode);

            if (responseCode == 200) {
                HiLog.info(LABEL_LOG, "HttpService::uploadData :: 目标地址可用: " + targetUrl);
                result = true;
            } else {
                // 读取错误响应内容
                String errorResponse = "";
                try (InputStream is = connection.getErrorStream()) {
                    if (is != null) {
                        ByteArrayOutputStream errorStream = new ByteArrayOutputStream();
                        byte[] buffer = new byte[1024];
                        int length;
                        while ((length = is.read(buffer)) != -1) {
                            errorStream.write(buffer, 0, length);
                        }
                        errorResponse = errorStream.toString(StandardCharsets.UTF_8.name());
                    }
                } catch (Exception ex) {
                    HiLog.error(LABEL_LOG, "读取错误响应失败: " + ex.getMessage());
                }
                HiLog.error(LABEL_LOG, "HttpService::uploadData :: 目标地址响应失败: " + targetUrl + ", 响应码: " + responseCode + ", 错误内容: " + errorResponse);
            }
        } catch (java.net.ConnectException e) {
            HiLog.error(LABEL_LOG, "HttpService::uploadData :: 连接被拒绝: " + targetUrl + ", 错误: " + e.getMessage());
        } catch (java.net.SocketTimeoutException e) {
            HiLog.error(LABEL_LOG, "HttpService::uploadData :: 连接超时: " + targetUrl + ", 错误: " + e.getMessage());
        } catch (java.net.UnknownHostException e) {
            HiLog.error(LABEL_LOG, "HttpService::uploadData :: 未知主机: " + targetUrl + ", 错误: " + e.getMessage());
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "HttpService::uploadData :: 目标地址不可用: " + targetUrl + ", 错误类型: " + e.getClass().getSimpleName() + ", 错误: " + e.getMessage());
            e.printStackTrace();
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
        return result;
    }

    // 从服务器获取数据
    private JSONObject fetchDataFromServer(String targetUrl) {
        HiLog.info(LABEL_LOG, "HttpService::fetchDataFromServer :: targetUrl: " + targetUrl);
        JSONObject result = null;
        try {
            // Check if the server is accessible
            URL url = new URL(targetUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(5000); // 5 seconds timeout
            connection.setReadTimeout(5000); // 5 seconds timeout
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Accept", "application/json");

            int responseCode = connection.getResponseCode();
            HiLog.info(LABEL_LOG, "HttpService::fetchDataFromServer ::responseCode " + responseCode);

            if (responseCode == HttpURLConnection.HTTP_OK) {
                try (InputStream is = connection.getInputStream();
                     ByteArrayOutputStream resultStream = new ByteArrayOutputStream()) {

                    byte[] buffer = new byte[1024];
                    int length;
                    while ((length = is.read(buffer)) != -1) {
                        resultStream.write(buffer, 0, length);
                    }

                    String response = resultStream.toString(StandardCharsets.UTF_8.name());
                    result = new JSONObject(response);
                }
            } else {
                HiLog.error(LABEL_LOG, "Failed to fetch data, response code: " + responseCode);
            }

            connection.disconnect();
        } catch (Exception e) {
            e.printStackTrace();
            HiLog.error(LABEL_LOG, "HttpService::fetchDataFromServer :: exception: " + e.getMessage());
            HiLog.error(LABEL_LOG, "HttpService::fetchDataFromServer :: exception stack trace: " + e.getStackTrace()[0]);
        }
        return result;
    }

    // 上传设备信息
    private void uploadDeviceInfo() {
        String currentDeviceInfo = Utils.getDeviceInfo();
        HiLog.info(LABEL_LOG, "HttpService::uploadDeviceInfo currentDeviceInfo: " + currentDeviceInfo);
        if(currentDeviceInfo == null || currentDeviceInfo.isEmpty()){
            HiLog.error(LABEL_LOG, "HttpService::uploadDeviceInfo currentDeviceInfo is null or empty");
            return;
        }
        if("wifi".equals(dataManager.getUploadMethod())){
            if (!currentDeviceInfo.equals(lastDeviceInfo)) {
                uploadData(dataManager.getUploadDeviceInfoUrl(), currentDeviceInfo);
                lastDeviceInfo = currentDeviceInfo;
            }
        }
    }

    // 上传健康数据
    public void uploadHealthData() {
        if(dataManager.getHeartRate() == 1000){
            HiLog.info(LABEL_LOG, "HttpService::uploadHealthData 心率是0，不上传健康数据");
            return;
        }
        
        String currentHealthInfo = Utils.getHealthInfo();
        if (currentHealthInfo != null && !currentHealthInfo.isEmpty()) {
            // 先缓存数据
            healthDataCache.addToCache(currentHealthInfo);
            HiLog.info(LABEL_LOG, "HttpService::uploadHealthData 数据已缓存");
        }
        
        // 尝试批量上传缓存数据
        if(!dataManager.isLicenseExceeded() && "wifi".equals(dataManager.getUploadMethod())){
            HiLog.info(LABEL_LOG, "HttpService::uploadHealthData 开始批量上传缓存数据");
            boolean uploadSuccess = uploadAllCachedData();
            if(!uploadSuccess && dataManager.isEnableResume()){
                HiLog.error(LABEL_LOG, "HttpService::uploadHealthData 批量上传失败，数据保留在缓存中");
            }
        } else {
            HiLog.warn(LABEL_LOG, "HttpService::uploadHealthData 不满足上传条件，数据已缓存等待上传");
        }
    }

    private boolean uploadAllCachedData() {
        List<String> cachedData = healthDataCache.getAllCachedData();
        HiLog.info(LABEL_LOG, "HttpService::uploadAllCachedData 开始上传缓存数据，数量: " + cachedData.size());
        if (cachedData.isEmpty()) {
            return true;
        }

        int retryCount = 0;
        boolean success = false;
        
        while (retryCount < dataManager.getUploadRetryCount() && !success) {
            try {
                // 构建统一格式的JSON数据
                JSONObject finalJson = new JSONObject();
                if (cachedData.size() == 1) {
                    // 单条数据，直接使用原始数据
                    finalJson = new JSONObject(cachedData.get(0));
                } else {
                    // 批量数据，提取每个对象中的data字段内容
                    JSONArray jsonArray = new JSONArray();
                    for (String data : cachedData) {
                        try {
                            JSONObject jsonObj = new JSONObject(data);
                            // 获取data字段的内容
                            JSONObject dataContent = jsonObj.getJSONObject("data");
                            jsonArray.put(dataContent);
                        } catch (JSONException e) {
                            HiLog.error(LABEL_LOG, "HttpService::uploadAllCachedData 解析JSON失败: " + e.getMessage());
                            continue;
                        }
                    }
                    finalJson.put("data", jsonArray);
                }
                
                String uploadData = finalJson.toString();
                HiLog.info(LABEL_LOG, "HttpService::uploadAllCachedData 准备上传数据: " + uploadData.substring(0, Math.min(100, uploadData.length())));
                
                // 尝试上传
                success = uploadData(dataManager.getUploadHealthDataUrl(), uploadData);
                
                if (success) {
                    // 上传成功，清空缓存
                    healthDataCache.clearCache();
                    HiLog.info(LABEL_LOG, "HttpService::uploadAllCachedData 批量上传成功");
                } else {
                    retryCount++;
                    HiLog.error(LABEL_LOG, "HttpService::uploadAllCachedData 上传失败，重试次数: " + retryCount);
                    // 等待一段时间后重试
                    Thread.sleep(1000 * retryCount);
                }
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "HttpService::uploadAllCachedData error: " + e.getMessage());
                retryCount++;
                try {
                    Thread.sleep(1000 * retryCount);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
            }
        }
        
        if (!success) {
            HiLog.error(LABEL_LOG, "HttpService::uploadAllCachedData 达到最大重试次数，上传失败");
        }
        
        return success;
    }

    // 上传公共事件
    public void uploadCommonEvent(String commonEvent) {
        // 在后台线程执行网络操作，避免NetworkOnMainThreadException
        new Thread(() -> {
            try {
                JSONObject commonEventJson = new JSONObject();
                String[] parts = commonEvent.split(":");

                String commonEventType = parts[0];
                String commonEventValue = parts[1];
                DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
                String timestamp = Instant.now().atZone(ZoneId.systemDefault()).format(formatter);

                commonEventJson.put("eventType", commonEventType);
                commonEventJson.put("eventValue", commonEventValue);
                commonEventJson.put("deviceSn", dataManager.getDeviceSn());
                commonEventJson.put("latitude", dataManager.getLatitude());
                commonEventJson.put("longitude", dataManager.getLongitude());
                commonEventJson.put("altitude", dataManager.getAltitude());
                commonEventJson.put("timestamp", timestamp);
                
                // 修复healthData字段JSON嵌套问题
                String healthInfoStr = Utils.getHealthInfo();
                if (healthInfoStr != null && !healthInfoStr.isEmpty()) {
                    try {
                        JSONObject healthDataObj = new JSONObject(healthInfoStr);
                        commonEventJson.put("healthData", healthDataObj);
                    } catch (JSONException e) {
                        HiLog.error(LABEL_LOG, "解析healthData JSON失败: " + e.getMessage());
                        commonEventJson.put("healthData", healthInfoStr); // 降级处理
                    }
                } else {
                    commonEventJson.put("healthData", JSONObject.NULL);
                }

                String commonEventData = commonEventJson.toString();
                HiLog.info(LABEL_LOG, "HttpService::uploadCommonEvent commonEvent: " + commonEvent + " uploadCommonEventUrl: " + dataManager.getUploadCommonEventUrl());
                HiLog.info(LABEL_LOG, "HttpService::uploadCommonEvent commonEventData: " + commonEventData);
                
                // 添加重试机制和wifi检查
                if (!"wifi".equals(dataManager.getUploadMethod())) {
                    HiLog.warn(LABEL_LOG, "HttpService::uploadCommonEvent 非WiFi模式，跳过上传");
                    return;
                }
                
                boolean success = uploadData(dataManager.getUploadCommonEventUrl(), commonEventData);
                if (!success) {
                    HiLog.error(LABEL_LOG, "HttpService::uploadCommonEvent 上传失败");
                }
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "HttpService::uploadCommonEvent 异常: " + e.getMessage());
                e.printStackTrace();
            }
        }).start();
    }

    // 从服务器获取消息
    public void fetchMessageFromServer() {
        HiLog.info(LABEL_LOG, "HttpService::fetchMessageFromServer fetchMessageUrl: " + dataManager.getFetchMessageUrl());
        HiLog.info(LABEL_LOG, "HttpService::fetchMessageFromServer deviceSn: " + dataManager.getDeviceSn());
        HiLog.info(LABEL_LOG, "HttpService::fetchMessageFromServer licenseExceeded: " + dataManager.isLicenseExceeded());
        HiLog.info(LABEL_LOG, "HttpService::fetchMessageFromServer uploadMethod: " + dataManager.getUploadMethod());
        
        if(dataManager.isLicenseExceeded() || !"wifi".equals(dataManager.getUploadMethod())) {
            return;
        }

        String finalTargetUrl = dataManager.getFetchMessageUrl() + "/receive?deviceSn=" + dataManager.getDeviceSn();
        HiLog.info(LABEL_LOG, "HttpService::fetchMessageFromServer finalTargetUrl: " + finalTargetUrl);

        JSONObject response = fetchDataFromServer(finalTargetUrl);
        HiLog.info(LABEL_LOG, "HttpService::fetchMessageFromServer response: " + response);

        if (response != null && response.getBoolean("success")) {
            try {
                JSONObject data = response.getJSONObject("data");
                if (data != null) {
                    // 记录消息统计信息
                    HiLog.info(LABEL_LOG, String.format("消息统计: 总数=%d, 个人消息=%d, 公共消息=%d, 部门数=%d", 
                        data.getInt("totalMessages"),
                        data.getInt("personalMessagesCount"),
                        data.getInt("publicMessagesCount"),
                        data.getJSONArray("departments").length()));

                   

                    // 记录消息类型统计
                    JSONObject typeCount = data.getJSONObject("messageTypeCount");
                    Iterator<String> types = typeCount.keys();
                    while (types.hasNext()) {
                        String type = types.next();
                        HiLog.info(LABEL_LOG, String.format("消息类型[%s]数量: %d", 
                            type, typeCount.getInt(type)));
                    }

                    if (data.has("messages")) {
                        JSONArray messages = data.getJSONArray("messages");
                        for (int i = 0; i < messages.length(); i++) {
                            JSONObject message = messages.getJSONObject(i);
                            HiLog.info(LABEL_LOG, "处理消息: " + message.toString());

                            String messageType = message.getString("message_type");
                            String translatedMessageType = MESSAGE_TYPE_MAP.getOrDefault(messageType, messageType);
                            
                            // 构建消息内容
                            String messageContent = String.format("平台在%s%s：%s, 内容为:%s (部门: %s)",
                                message.getString("sent_time"),
                                message.isNull("user_name") || message.getString("user_name").isEmpty() ? "群发" : "发来",
                                translatedMessageType,
                                message.getString("message"),
                                message.getString("department_name"));

                            HiLog.info(LABEL_LOG, "消息内容: " + messageContent);
                            showNotification(messageContent);

                            // 构建响应消息
                            JSONObject responseMessage = new JSONObject();
                            // 复制原有字段
                            responseMessage.put("department_id", message.getString("department_id"));
                            responseMessage.put("department_name", message.getString("department_name"));
                            responseMessage.put("is_public", message.getBoolean("is_public"));
                            responseMessage.put("message", message.getString("message"));
                            responseMessage.put("message_id", message.getString("message_id"));
                            responseMessage.put("message_type", message.getString("message_type"));
                            responseMessage.put("sent_time", message.getString("sent_time"));
                            responseMessage.put("user_id", message.isNull("user_id") ? JSONObject.NULL : message.get("user_id"));
                            responseMessage.put("user_name", message.isNull("user_name") ? JSONObject.NULL : message.get("user_name"));
                            responseMessage.put("sender_type", "device");
                            responseMessage.put("receiver_type", "platform");
                            
                            // 更新需要修改的字段
                            responseMessage.put("device_sn", dataManager.getDeviceSn());
                            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
                            String formattedTime = Instant.now().atZone(ZoneId.of("Asia/Shanghai")).format(formatter);
                            responseMessage.put("received_time", formattedTime);
                            responseMessage.put("message_status", "responded");

                            // 发送更新后的消息回平台
                            String responseUrl = dataManager.getFetchMessageUrl() + "/send";
                            HiLog.info(LABEL_LOG, "发送响应消息到: " + responseUrl);
                            sendMessagesToPlatform(responseUrl, responseMessage.toString());
                        }
                    }
                }
            } catch (JSONException e) {
                HiLog.error(LABEL_LOG, "处理消息时发生错误: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }

    // 发送消息到平台
    public void sendMessagesToPlatform(String httpUrl, String message) {
        HiLog.info(LABEL_LOG, "HttpService::sendMessagesToPlatform httpUrl: " + httpUrl);
        HiLog.info(LABEL_LOG, "HttpService::sendMessagesToPlatform message: " + message);
        if("wifi".equals(dataManager.getUploadMethod())){
            HiLog.info(LABEL_LOG, "HttpService::sendMessagesToPlatform targetUrl: " + httpUrl);
            uploadData(httpUrl, message);
        }
    }


    // 显示通知
    private void showNotification(String textContent) {
        NotificationRequest request = new NotificationRequest(notificationId++);
        NotificationRequest.NotificationNormalContent content = new NotificationRequest.NotificationNormalContent();
        content.setTitle(dataManager.getCustomerName())
                .setText(textContent);
        NotificationRequest.NotificationContent notificationContent = new NotificationRequest.NotificationContent(content);
        request.setContent(notificationContent);
        try {
            NotificationHelper.publishNotification(request);
            keepBackgroundRunning(notificationId, request);
            storeValue("notificationId", String.valueOf(notificationId));
        } catch (RemoteException ex) {
            ex.printStackTrace();
        }
    }



    // 获取Preferences的优化版
    private Preferences getPreferences() {
        if (preferences == null) {
            Context context = getContext();
            DatabaseHelper databaseHelper = new DatabaseHelper(context);
            String fileName = "pref";
            preferences = databaseHelper.getPreferences(fileName);
        }
        return preferences;
    }

    // 存储值到Preferences
    public void storeValue(String key, String value){
        Preferences preferences = getPreferences();
        preferences.putString(key, value);
        preferences.flush();
    }

    // 从Preferences获取值
    public String fetchValue(String key){
        Preferences preferences = getPreferences();
        return preferences.getString(key,"");
    }

    @Override
    public void onBackground() {
        super.onBackground();
        HiLog.info(LABEL_LOG, "HttpService::onBackground");
    }

    @Override
    public void onStop() {
        super.onStop();
        cancelBackgroundRunning();

        // 取消定时器
        if (masterHttpTimer != null) {
            masterHttpTimer.cancel();
        }

        HiLog.info(LABEL_LOG, "HttpService::onStop");
    }

    

    @Override
    public void onCommand(Intent intent, boolean restart, int startId) {
    }

    @Override
    public IRemoteObject onConnect(Intent intent) {
        return null;
    }

    @Override
    public void onDisconnect(Intent intent) {
    }
   
}
