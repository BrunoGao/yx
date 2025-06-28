package com.hg.watch.slice;

import com.hg.watch.MainAbility;
import com.hg.watch.ResourceTable;
import com.hg.watch.custom.BTCircularDashboard;
import com.hg.watch.custom.CircularDashboard;

import com.tdtech.ohos.mdm.DeviceManager;

import ohos.aafwk.ability.AbilitySlice;
import ohos.aafwk.content.Intent;
import ohos.aafwk.content.Operation;
import ohos.agp.window.dialog.ToastDialog;
import ohos.app.Context;
import ohos.bundle.IBundleManager;
import ohos.data.DatabaseHelper;
import ohos.data.preferences.Preferences;
import ohos.event.notification.NotificationRequest;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import ohos.location.Location;
import ohos.location.Locator;
import ohos.location.LocatorCallback;
import ohos.location.RequestParam;
import ohos.net.*;
import ohos.security.SystemPermission;

import java.math.BigDecimal;


import java.util.Timer;
import java.util.TimerTask;


import ohos.vibrator.agent.VibratorAgent;
import ohos.vibrator.bean.VibrationPattern;
import ohos.bluetooth.BluetoothHost;
import org.json.JSONException;
import org.json.JSONObject;

import java.net.HttpURLConnection;
import java.net.URL;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.function.Consumer;

import com.hg.watch.utils.DataManager;
import com.hg.watch.HealthDataCache;

public class MainAbilitySlice extends AbilitySlice {
    BTCircularDashboard BTDashboard = null;
    CircularDashboard dashboard = null;
    private Timer timer;
    private boolean showFirstPage = true;
    private boolean isheartRateExceeded = false;
    private boolean isbloodOxygenLow = false;

    private boolean isMethaneExceeded = false;
    private boolean isOxygenLow = false;
    private VibratorAgent vibratorAgent;
    private boolean isVibrating = false; // 跟踪振动状态

    private DataManager dataManager = DataManager.getInstance();
    //private HttpService httpService = HttpService.getInstance();
    private Intent HealthDataIntent;
    private Intent bluetoothIntent;
    private Intent httpIntent;
    private DeviceManager deviceManager = null;

    private BluetoothHost bluetooth = BluetoothHost.getDefaultHost(this);
    public static final int MY_PERMISSIONS_REQUEST_LOCATION = 100;
    private String uploadMethod = "";

    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "ljwx-log");
    private boolean hasRequestedLocationPermission = false;

    private String appStatus = "灵境万象";


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

     String configUrl = "";
     private NetManager netManager = null;

     private final String DEFAULT_CONFIG = "{\n" +
            "  \"customer_id\": \"1\",\n" +
            "  \"customer_name\": \"富力通\",\n" +
            "  \"cache_max_count\": 50,\n" +
            "  \"enable_resume\": 0,\n" +
            "  \"upload_retry_count\": 3,\n" +
            "  \"upload_retry_interval\": 5,\n" +
            "  \"health_data\": {\n" +
            "    \"blood_oxygen\": \"20:1:1:100.0:90.0:5\",\n" +
            "    \"calorie\": \"60:1:1:0.0:0.0:0\",\n" +
            "    \"distance\": \"60:1:1:0.0:0.0:0\",\n" +
            "    \"ecg\": \"1800:1:1:0.0:0.0:0\",\n" +
            "    \"exercise_daily\": \"1800:1:0:-1:-1:-1\",\n" +
            "    \"exercise_week\": \"1800:0:0:-1:-1:-1\",\n" +
            "    \"heart_rate\": \"20:1:1:100.0:80.0:5\",\n" +
            "    \"location\": \"60:1:1:0.0:0.0:0\",\n" +
            "    \"scientific_sleep\": \"1800:0:0:-1:-1:-1\",\n" +
            "    \"sleep\": \"1800:1:1:0.0:0.0:0\",\n" +
            "    \"step\": \"60:1:1:0.0:0.0:0\",\n" +
            "    \"stress\": \"20:1:1:66.0:0.0:5\",\n" +
            "    \"temperature\": \"20:1:1:37.5:35.0:5\",\n" +
            "    \"wear\": \"1800:1:1:-1:-1:-1\",\n" +
            "    \"work_out\": \"1800:1:1:-1:-1:-1\"\n" +
            "  },\n" +
            "  \"interface_data\": {\n" +
            "    \"事件上传接口\": \"http://192.168.1.6:8001/upload_common_event;5;1;ZNSB_SBSJ;Basic b3Blbl91c2VyOnVzZXJfMTIzIw==\",\n" +
            "    \"健康数据上传接口\": \"http://192.168.1.6:8001/upload_health_data;60;1;ZNSB_SBSJ;Basic b3Blbl91c2VyOnVzZXJfMTIzIw==\",\n" +
            "    \"平台消息交互接口\": \"http://192.168.1.6:8001/DeviceMessage;60;1;ZNSB_SBSJ;Basic b3Blbl91c2VyOnVzZXJfMTIzIw==\",\n" +
            "    \"设备信息上传接口\": \"http://192.168.1.6:8001/upload_device_info;300;1;ZNSB_SBSJ;Basic b3Blbl91c2VyOnVzZXJfMTIzIw==\",\n" +
            "    \"配置获取接口\": \"http://192.168.1.6:8001/fetch_health_data_config;36000;1;ZNSB_SBSJ;Basic b3Blbl91c2VyOnVzZXJfMTIzIw==\"\n" +
            "  },\n" +
            "  \"is_support_license\": 0,\n" +
            "  \"license_key\": 400,\n" +
            "  \"upload_method\": \"wifi\"\n" +
            "}";
 
    //private Utils utils = new Utils();

    public MainAbilitySlice() {
        
        dataManager.addPropertyChangeListener(evt -> {
            HiLog.info(LABEL_LOG, "PropertyChangeListener:" + evt.getPropertyName());
            if ("heartRate".equals(evt.getPropertyName()) || "bloodOxygen".equals(evt.getPropertyName()) || "temperature".equals(evt.getPropertyName()) || "stress".equals(evt.getPropertyName()) ) {
                updateDashboard();
                
            }else if("licenseExceeded".equals(evt.getPropertyName())){
                if(dataManager.isLicenseExceeded()){
                    storeValue("licenseExceeded", "true");
                }
            }else if("supportLocation".equals(evt.getPropertyName())){
                if(dataManager.isSupportLocation()){
                    System.out.println("jjgao::MainAbilitySlice::dataManager.isSupportLocation():" + dataManager.isSupportLocation());
                    HiLog.info(LABEL_LOG, "jjgao::MainAbilitySlice::dataManager.isSupportLocation():" + dataManager.isSupportLocation());
                    getLocation();
                }else{
                    dataManager.setLatitude(BigDecimal.valueOf(0));
                    dataManager.setLongitude(BigDecimal.valueOf(0));
                    dataManager.setAltitude(BigDecimal.valueOf(0));
                }
            }else if("config".equals(evt.getPropertyName())){
                JSONObject config = dataManager.getConfig();
                HiLog.info(LABEL_LOG, "MainAbilitySlice::config:" + config);
                if(config != null){
                    processConfig(config);
                }
            }else if("isHealthServiceReady".equals(evt.getPropertyName())){
                boolean isReady = dataManager.getIsHealthServiceReady();
                HiLog.info(LABEL_LOG, "MainAbilitySlice::健康服务状态变化: " + isReady);
                if(isReady && "bluetooth".equals(dataManager.getUploadMethod())){
                    HiLog.info(LABEL_LOG, "健康服务已就绪，现在启动蓝牙服务");
                    startBluetoothWhenHealthReady();
                }
            }
        });
    }


    @Override
    public void onStart(Intent intent) {
        super.onStart(intent);
        HealthDataCache.init(this);

        setCustomerName();
        MainAbility mainAbility = (MainAbility) getAbility();
        mainAbility.setMainAbilitySlice(this);


        HiLog.info(LABEL_LOG, "MainAbilitySlice::onStart::start");

        NotificationRequest request = new NotificationRequest(2223);
        NotificationRequest.NotificationNormalContent content = new NotificationRequest.NotificationNormalContent();
        content.setTitle("MainAbilitySlice").setText("keepServiceAlive");
        NotificationRequest.NotificationContent notificationContent = new NotificationRequest.NotificationContent(content);
        request.setContent(notificationContent);
        
        HiLog.info(LABEL_LOG, "MainAbilitySlice::onStart::setUIContent");
        setUIContent(ResourceTable.Layout_ability_main);
        dashboard = (CircularDashboard) findComponentById(ResourceTable.Id_custom_dashboard);

        deviceManager = DeviceManager.getInstance(getContext());
        setDeviceSn();
        HiLog.info(LABEL_LOG, "MainAbilitySlice::onStart::deviceSn:" + deviceSn);

        //configUrl = "http://www.lingjingwanxiang.com:5001/fetch_health_data_config?customer_id=0&deviceSn=" + deviceSn;

        configUrl = "http://192.168.1.6:5001/fetch_health_data_config?customer_id=0&deviceSn=" + deviceSn;
        HiLog.info(LABEL_LOG, "MainAbilitySlice::onStart::configUrl:" + configUrl);


        fetchConfig(success -> {
                HiLog.info(LABEL_LOG, "配置拉取" + (success ? "成功" : "失败") + "，开始启动后台服务");
                appStatus = "读取配置成功";
                dataManager.setAppStatus(appStatus);
                runHealthData();
                // 配置处理完成后启动相应服务
                String uploadMethod = dataManager.getUploadMethod();
                HiLog.info(LABEL_LOG, "MainAbilitySlice::onStart::当前上传方式: " + uploadMethod);
                
                if("wifi".equals(uploadMethod)){
                    HiLog.info(LABEL_LOG, "MainAbilitySlice::onStart::启动http");
                    getUITaskDispatcher().asyncDispatch(() -> {
                        runHttp();
                    });
                    //deviceManager.setBluetoothEnable(false);
                }else if("bluetooth".equals(uploadMethod)){
                    HiLog.info(LABEL_LOG, "MainAbilitySlice::onStart::蓝牙模式，等待健康服务就绪后启动");
                    // 蓝牙模式下不立即启动，等待健康服务就绪后通过监听器启动
                    // 如果健康服务已经就绪，立即启动蓝牙服务
                    if(dataManager.getIsHealthServiceReady()){
                        HiLog.info(LABEL_LOG, "健康服务已就绪，立即启动蓝牙服务");
                        startBluetoothWhenHealthReady();
                    } else {
                        HiLog.info(LABEL_LOG, "健康服务未就绪，等待健康服务初始化完成");
                    }
                }           
        });


        String locationPermission = "ohos.permission.LOCATION";
        if (!hasRequestedLocationPermission) {
            HiLog.info(LABEL_LOG, "MainAbilitySlice::onStart::检查位置权限");
            if ((verifySelfPermission(locationPermission) != IBundleManager.PERMISSION_GRANTED) && !hasRequestedLocationPermission) {
                hasRequestedLocationPermission = true;
                HiLog.info(LABEL_LOG, "MainAbilitySlice::onStart::请求位置权限");
                if (canRequestPermission(locationPermission)) {
                    requestPermissionsFromUser(new String[]{"ohos.permission.LOCATION","ohos.permission.LOCATION_IN_BACKGROUND"}, MY_PERMISSIONS_REQUEST_LOCATION);
                } else {
                    new ToastDialog(getContext()).setText("请进入系统设置进行授权").show();
                }
            }
        }

        vibratorAgent = new VibratorAgent();

        if (verifySelfPermission(SystemPermission.VIBRATE) != IBundleManager.PERMISSION_GRANTED) {
            if (canRequestPermission(SystemPermission.VIBRATE)) {
                requestPermissionsFromUser(new String[] {SystemPermission.VIBRATE}, 0);
            }
        }

        // 定时拉取配置
        HiLog.info(LABEL_LOG, "MainAbilitySlice::onStart::定时拉取配置" + dataManager.getFetchConfigInterval() + "秒"  );

        int interval = dataManager.getFetchConfigInterval();
        if(interval == 0){
            interval = 600;
        }
        final int fetchConfigInterval = interval * 1000;

        timer = new Timer();
 
        timer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                //updateDashboard();
                fetchHttpConfig(success -> {
                    HiLog.info(LABEL_LOG, "配置拉取" + (success ? "成功" : "失败") + ",应用配置到手表");

                });
            }
        }, fetchConfigInterval, fetchConfigInterval); 

        /* 

        Timer updateDashboardTimer = new Timer();
        int updateDashboardInterval = dataManager.getUploadHealthInterval();
        if(updateDashboardInterval == 0){
            updateDashboardInterval = 5;
        }
 
        updateDashboardTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                updateDashboard();          
            }
        }, 0, updateDashboardInterval); 
        */

    }


    private void setCustomerName(){
        if(dataManager.getCustomerName() != null && dataManager.getCustomerName() != "" && !dataManager.getCustomerName().isEmpty()){
            customerName = dataManager.getCustomerName();
            HiLog.info(LABEL_LOG, "MainAbilitySlice::setCustomerName::getCustomerName:" + customerName);
        }else{
            customerName = fetchValue("customerName", "");
            HiLog.info(LABEL_LOG, "MainAbilitySlice::setCustomerName::fetchValue:" + customerName);
            if(customerName == null || customerName == "" || customerName.isEmpty()){
                customerName = "富力通";
                HiLog.info(LABEL_LOG, "MainAbilitySlice::setCustomerName::customerName:" + customerName);
            }
        }
    }

    private void setDeviceSn(){
        deviceSn = fetchValue("deviceSn", "");
        if(deviceSn == null || deviceSn == "" || deviceSn.isEmpty()){
            // 提取设备序列号
            deviceSn = fetchValueFromJson(deviceManager.getDeviceInfo(), "SerialNumber");
            storeValue("deviceSn", deviceSn);
        }
        dataManager.setDeviceSn(deviceSn);
    }

    /**  
     * 拉取并处理完配置以后，直接告诉调用者"OK" 或 "Fail"  
     */
    public void fetchConfig(Consumer<Boolean> callback) {
        new Thread(() -> {
            boolean success = false;
            try {
                // ----- 1. 尝试从服务器获取配置 -----
                HiLog.info(LABEL_LOG, "MainAbilitySlice::fetchConfig::fetch config from http server");
                URL url = new URL(configUrl);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setConnectTimeout(2000);
                conn.setReadTimeout(2000);
                conn.setRequestMethod("GET");
 
                HiLog.info(LABEL_LOG, "MainAbilitySlice::fetchConfig::conn.getResponseCode():" + conn.getResponseCode());
                //System.out.println("MainAbilitySlice::fetchConfig::conn.getResponseCode():" + conn.getResponseCode());
                
                if (conn.getResponseCode() == 200) {
                    BufferedReader r = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = r.readLine()) != null) sb.append(line);
                    r.close();
                    String jsonText = sb.toString();
                    
                    // 解析并存储服务器配置
                    JSONObject cfg = new JSONObject(jsonText);
                    HiLog.info(LABEL_LOG, "MainAbilitySlice::fetchConfig::server config:" + jsonText);
                    System.out.println("MainAbilitySlice::fetchConfig::server config:" + jsonText);
                    processConfig(cfg);
                    dataManager.setConfig(cfg);
                    storeValue("config", cfg.toString());
                    success = true;
                }
                conn.disconnect();
    
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "服务器配置获取失败，尝试读取本地存储的配置");
                
                // ----- 2. 尝试读取本地存储的配置 -----
                String storedConfig = fetchValue("config", "");
                if (!storedConfig.isEmpty() && storedConfig != "") {
                    try {
                        HiLog.info(LABEL_LOG, "MainAbilitySlice::fetchConfig::using stored config:" + storedConfig);
                        JSONObject storedCfg = new JSONObject(storedConfig);
                        processConfig(storedCfg);
                        dataManager.setConfig(storedCfg);
                        success = true;
                    } catch (JSONException je) {
                        HiLog.error(LABEL_LOG, "本地存储的配置解析失败，使用默认配置");
                        // ----- 3. 使用默认配置 -----
                        useDefaultConfig();
                        success = true;
                    }
                } else {
                    HiLog.info(LABEL_LOG, "本地无存储的配置，使用默认配置");
                    // ----- 3. 使用默认配置 -----
                    useDefaultConfig();
                    success = true;
                }
            }
    
            // ----- 4. 回调 -----
            callback.accept(success);
        }).start();
    }
    
    public void fetchHttpConfig(Consumer<Boolean> callback) {
        new Thread(() -> {
            boolean success = false;
            try {
                // ----- 1. 尝试从服务器获取配置 -----
                HiLog.info(LABEL_LOG, "MainAbilitySlice::fetchHttpConfig::fetch config from http server");
                URL url = new URL(configUrl);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setConnectTimeout(2000);
                conn.setReadTimeout(2000);
                conn.setRequestMethod("GET");
 
                HiLog.info(LABEL_LOG, "MainAbilitySlice::fetchHttpConfig::conn.getResponseCode():" + conn.getResponseCode());
                
                if (conn.getResponseCode() == 200) {
                    BufferedReader r = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = r.readLine()) != null) sb.append(line);
                    r.close();
                    String jsonText = sb.toString();
                    
                    // 解析并存储服务器配置
                    JSONObject cfg = new JSONObject(jsonText);
                    HiLog.info(LABEL_LOG, "MainAbilitySlice::fetchHttpConfig::server config:" + jsonText);
                    processConfig(cfg);
                    dataManager.setConfig(cfg);
                    storeValue("config", cfg.toString());
                    success = true;
                }
                conn.disconnect();
    
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "服务器配置获取失败，暂不更新配置");
            }
    
            // ----- 4. 回调 -----
            callback.accept(success);
        }).start();
    }
    // 使用默认配置的辅助方法
    private void useDefaultConfig() {
        try {
            JSONObject def = new JSONObject(DEFAULT_CONFIG);
            processConfig(def);
            dataManager.setConfig(def);
        } catch (JSONException e) {
            HiLog.error(LABEL_LOG, "默认配置解析失败: " + e.getMessage());
        }
    }

    private void getLocation(){
        Locator locator = new Locator(getContext());
        locator.requestEnableLocation();
        if (locator.isLocationSwitchOn()) {
            HiLog.info(LABEL_LOG, "MainAbilitySlice::getLocation isLocationSwitchOn");
            try {
                int timeInterval = dataManager.getLocationMeasurePeriod();
                int distanceInterval = 0;
                RequestParam requestParam = new RequestParam(RequestParam.PRIORITY_FAST_FIRST_FIX, timeInterval, distanceInterval);
                
                HiLog.info(LABEL_LOG, "MainAbilitySlice::getLocation startLocating");
                locator.startLocating(requestParam, new LocatorCallback() {
                    @Override
                    public void onLocationReport(Location location) {

                        dataManager.setLatitude(BigDecimal.valueOf(location.getLatitude()));
                        dataManager.setLongitude(BigDecimal.valueOf(location.getLongitude()));
                        dataManager.setAltitude(BigDecimal.valueOf(location.getAltitude()));
                        //HiLog.info(LABEL_LOG, "jjgao::onLocationReport : " + dataManager.getLatitude() + "-" + dataManager.getLongitude() + "-" + dataManager.getAltitude());

                    }
                    @Override
                    public void onStatusChanged(int statusCode) {
                        HiLog.info(LABEL_LOG, "%{public}s", "MyLocatorCallback onStatusChanged : " + statusCode);
                     
                        //2 开始  3 结束
                    }
                    @Override
                    public void onErrorReport(int errorCode) {
                        HiLog.info(LABEL_LOG, "%{public}s", "MyLocatorCallback onErrorReport : " + errorCode);
                    
                    }
                
                });
    
            } catch (IllegalArgumentException e) {
                HiLog.info(LABEL_LOG, "MainAbilitySlice::getLocation startLocating error:" + e.getMessage());
                e.printStackTrace();
            }
        }else{
            HiLog.info(LABEL_LOG, "MainAbilitySlice::getLocation isLocationSwitchOff");
        }
    }

    private void checkLicense(){
        String licenseExceeded = fetchValue("licenseExceeded", "false");
        if("true".equals(licenseExceeded)){
            dataManager.setLicenseExceeded(true);
        }
    }

    Preferences getPreferences() {
        //Context context = getContext(); // 数据文件存储路径：/data/data/{PackageName}/{AbilityName}/preferences。
        Context context = getApplicationContext(); // 数据文件储路径：/data/data/{PackageName}/preferences。
        //HiLog.info(LABEL_LOG, "MainAbilitySlice::getPreferences context: " + context.getPreferencesDir());
        DatabaseHelper databaseHelper = new DatabaseHelper(context); // context入参类型为ohos.app.Context。
        String fileName = "pref"; // fileName表示件名，其值不能为空，也不能包含路径，默认存储目录可以通过context.getPreferencesDir()获取。
        return databaseHelper.getPreferences(fileName);
    }
    public  void storeValue(String key, String value){
        Preferences preferences = getPreferences();
        preferences.putString(key, value);
        preferences.flush();
    }
    public  String fetchValue(String key, String defaultValue){
        Preferences preferences = getPreferences();
        String value = preferences.getString(key, defaultValue);
        return value != null ? value : defaultValue;
    }

    public void runBluetooth(){
        bluetoothIntent = new Intent();
        Operation btOperation = new Intent.OperationBuilder()
                .withDeviceId("")
                .withBundleName("com.hg.watch")
                .withAbilityName("com.hg.watch.BluetoothService")
                .build();
        bluetoothIntent.setOperation(btOperation);
        startAbility(bluetoothIntent);
        HiLog.info(LABEL_LOG, "run bluetooth in background:");
    }
    public void runHttp(){
        httpIntent = new Intent();
        Operation httpOperation = new Intent.OperationBuilder()
                .withDeviceId("")
                .withBundleName("com.hg.watch")
                .withAbilityName("com.hg.watch.HttpService")
                .build();
        httpIntent.setOperation(httpOperation);
        startAbility(httpIntent);
        HiLog.info(LABEL_LOG, "run http in background:");
    }

    public void runHealthData(){
        HealthDataIntent = new Intent();
        Operation HdOperation = new Intent.OperationBuilder()
                .withDeviceId("")
                .withBundleName("com.hg.watch")
                .withAbilityName("com.hg.watch.HealthDataService")
                .build();   
        HealthDataIntent.setOperation(HdOperation);
        startAbility(HealthDataIntent);
        HiLog.info(LABEL_LOG, "run health data in background:");
    }

    private void updateVibration(boolean shouldVibrate) {
        if (shouldVibrate && !isVibrating) {
            vibratorAgent.start(VibrationPattern.VIBRATOR_TYPE_RINGTONE_BOUNCE, false);
            isVibrating = true;
        } else if (!shouldVibrate && isVibrating) {
            vibratorAgent.stop();
            isVibrating = false;
        }
    }

    private void manageVibration(boolean shouldVibrate) {

        getUITaskDispatcher().asyncDispatch(() -> {
            updateVibration(shouldVibrate);
        });
    }



    private void updateDashboard() {
        //HiLog.info(LABEL_LOG, "jjgao::MainAbilitySlice::updateDashboard..." );

        double heartRate = dataManager.getHeartRate() ;
        String heartRateValue = String.format("%.0f", heartRate);
    

        double temperature = dataManager.getTemperature();
        String temperatureValue = String.format("%.1f", temperature); // 温度单位是摄氏度

        double bloodOxygen = dataManager.getBloodOxygen();
        String bloodOxygenValue = String.format("%.0f", bloodOxygen);

        double stress = dataManager.getStress();
        String stressValue = String.format("%d", (int) stress);

        double step = dataManager.getStep();
        String stepValue = String.format("%d", (int) step);


        int pressureHigh = dataManager.getPressureHigh();
        String pressureHighValue = String.format("%d", pressureHigh);

        int pressureLow = dataManager.getPressureLow();
        String pressureLowValue = String.format("%d", pressureLow);

        boolean shouldTriggerAlarm = isheartRateExceeded || isbloodOxygenLow;
        manageVibration(shouldTriggerAlarm);

        String appStatus = dataManager.getAppStatus();

        getUITaskDispatcher().asyncDispatch(() -> {
            //dashboard.alert(heartRateValue, isheartRateExceeded, bloodOxygenValue, isbloodOxygenLow);

            if(!shouldTriggerAlarm){
                dashboard.updateDashboard(heartRateValue,bloodOxygenValue,temperatureValue,pressureHighValue,pressureLowValue,stressValue,stepValue,appStatus);
                //dashboard.setShowSimplePage(dataManager.isSimpleMode());
            }
        });
    }



    @Override
    public void onStop() {
        super.onStop();
        if (httpIntent != null) {
            stopAbility(httpIntent);
        }
        if (bluetoothIntent != null) {
            stopAbility(bluetoothIntent);
        }
        if (HealthDataIntent != null) {
            stopAbility(HealthDataIntent);
        }
        if (timer != null) {
            timer.cancel();
        }
        // 如果业务执行完毕，可以停止获
    }

    @Override
    public void onActive() {
        super.onActive();
    }

    @Override
    public void onForeground(Intent intent) {
        super.onBackground();
        manageVibration(dataManager.getCh4() >= 1 ); // 确保后台时也处理振动
    }

    @Override
    public void onBackground() {
        super.onBackground();
        //HiLog.info(LABEL_LOG, "manageVibration on background");
        manageVibration(dataManager.getCh4() >= 1); // 确保后台时也处理振动
    }

    private void processConfig(JSONObject configJson) {
        // 设置上传方式
        String uploadMethod = configJson.getString("upload_method");
        dataManager.setUploadMethod(uploadMethod);
        HiLog.info(LABEL_LOG, "MainAbilitySlice::processConfig::uploadMethod:" + uploadMethod);

        // 设置客户名称
        String customerName = configJson.getString("customer_name");
        dataManager.setCustomerName(customerName);
        storeValue("customerName", customerName);
        HiLog.info(LABEL_LOG, "MainAbilitySlice::processConfig::customerName:" + customerName);

        // 设置license支持
        int val = configJson.getInt("is_support_license");
        boolean isSupportLicense = (val == 1);
        dataManager.setIsSupportLicense(isSupportLicense);

        // 设置license key
        int licenseKey = configJson.getInt("license_key") ;
        dataManager.setLicenseKey(licenseKey);

          // 设置license key
        int cacheMaxCount = configJson.getInt("cache_max_count") ;
        dataManager.setCacheMaxCount(cacheMaxCount);
        HiLog.info(LABEL_LOG, "MainAbilitySlice::processConfig::cacheMaxCount:" + dataManager.getCacheMaxCount());


         // 
        Boolean enableResume = configJson.getInt("enable_resume") == 1 ;
        dataManager.setEnableResume(enableResume);
        HiLog.info(LABEL_LOG, "MainAbilitySlice::processConfig::enableResume:" + dataManager.isEnableResume());
         // 设置license key
        int uploadRetryCount = configJson.getInt("upload_retry_count");
        dataManager.setUploadRetryCount(uploadRetryCount);
        HiLog.info(LABEL_LOG, "MainAbilitySlice::processConfig::uploadRetryCount:" + dataManager.getUploadRetryCount());

         // 设置license key
        int uploadRetryInterval = configJson.getInt("upload_retry_interval");
        dataManager.setUploadRetryInterval(uploadRetryInterval);
        HiLog.info(LABEL_LOG, "MainAbilitySlice::processConfig::uploadRetryInterval:" + dataManager.getUploadRetryInterval());
        // 处理接口配置
        JSONObject interfaceData = configJson.getJSONObject("interface_data");
        processInterfaceDataConfig(interfaceData);

        // 处理健康数据配置
        JSONObject healthData = configJson.getJSONObject("health_data");
        processHealthDataConfig(healthData);
    }

    public String fetchValueFromJson(String json, String key) {
        try {
            JSONObject jsonObject = new JSONObject(json);
            return jsonObject.getString(key);
        } catch (JSONException e) {
            HiLog.error(LABEL_LOG, "Error parsing JSON: " + e.getMessage());
            return "";
        }
    }

    private void processHealthDataConfig(JSONObject healthData) throws JSONException {
        for (String key : healthData.keySet()) {
            String value = healthData.getString(key);
            String[] parts = value.split(":");

            int interval = Integer.parseInt(parts[0]);
            boolean collect = Integer.parseInt(parts[1]) == 1;
            boolean isRealtime = Integer.parseInt(parts[2]) == 1;
            double warningHigh = Double.parseDouble(parts[3]);
            double warningLow = Double.parseDouble(parts[4]);
            int warningCnt = Integer.parseInt(parts[5]);

            HiLog.info(LABEL_LOG, "MainAbilitySlice::processHealthDataConfig :: key: " + key +
                    " interval: " + interval +
                    " collect: " + collect +
                    " isRealtime: " + isRealtime +
                    " warningHigh: " + warningHigh +
                    " warningLow: " + warningLow +
                    " warningCnt: " + warningCnt);

            switch (key) {
                case "heart_rate":
                    dataManager.setSupportHeartRate(collect);
                    dataManager.setHeartRateMeasurePeriod(interval);
                    dataManager.setHeartRateIsRealtime(isRealtime);
                    HiLog.info(LABEL_LOG, "MainAbilitySlice::processHealthDataConfig::heart_rate::warningHigh:" + (int)warningHigh);
                    HiLog.info(LABEL_LOG, "MainAbilitySlice::processHealthDataConfig::heart_rate::warningLow:" + (int)warningLow);
                    dataManager.setHeartRateWarningHigh((int)warningHigh);
                    dataManager.setHeartRateWarningLow((int)warningLow);
                    HiLog.info(LABEL_LOG, "MainAbilitySlice::processHealthDataConfig::heart_rate::warningHigh:" + dataManager.getHeartRateWarningHigh());
                    HiLog.info(LABEL_LOG, "MainAbilitySlice::processHealthDataConfig::heart_rate::warningLow:" + dataManager.getHeartRateWarningLow());
                    dataManager.setHeartRateWarningCnt(warningCnt);
                    break;
                case "temperature":
                    dataManager.setSupportTemperature(collect);
                    dataManager.setBodyTemperatureMeasurePeriod(interval);
                    dataManager.setBodyTemperatureIsRealtime(isRealtime);
                    // 验证体温告警阈值
                    if(warningHigh <= warningLow) {
                        HiLog.error(LABEL_LOG, "体温告警阈值设置错误:高温阈值(" + warningHigh + ")必须大于低温阈值(" + warningLow + ")");
                        return;
                    }
                    dataManager.setBodyTemperatureWarningHigh(warningHigh);
                    dataManager.setBodyTemperatureWarningLow(warningLow);
                    dataManager.setBodyTemperatureWarningCnt(warningCnt);
                    break;
                case "stress":
                    dataManager.setSupportStress(collect);
                    dataManager.setStressMeasurePeriod(interval);
                    dataManager.setStressIsRealtime(isRealtime);
                    dataManager.setStressWarningHigh((int)warningHigh);
                    dataManager.setStressWarningLow((int)warningLow);
                    dataManager.setStressWarningCnt(warningCnt);
                    break;
                case "blood_oxygen":
                    dataManager.setSupportBloodOxygen(collect);
                    dataManager.setBloodOxygenMeasurePeriod(interval);
                    dataManager.setBloodOxygenIsRealtime(isRealtime);
                    dataManager.setSpo2Warning((int)warningLow);
                    dataManager.setSpo2WarningCnt(warningCnt);
                    break;
                case "calorie":
                    dataManager.setSupportCalorie(collect);
                    dataManager.setCalorieMeasurePeriod(interval);
                    break;
                case "distance":
                    dataManager.setSupportDistance(collect);
                    dataManager.setDistanceMeasurePeriod(interval);
                    break;
                case "ecg":
                    dataManager.setSupportEcg(collect);
                    dataManager.setEcgMeasurePeriod(interval);
                    break;
                case "location":
                    dataManager.setSupportLocation(collect);
                    dataManager.setLocationMeasurePeriod(interval);
                    break;
                case "sleep":
                    dataManager.setSupportSleep(collect);
                    dataManager.setSleepMeasurePeriod(interval);
                    break;
                case "step":
                    dataManager.setSupportStep(collect);
                    dataManager.setStepsMeasurePeriod(interval);
                    break;
                case "wear":
                    dataManager.setSupportWear(collect);
                    break;
                case "work_out":
                    dataManager.setSupportWorkout(collect);
                    dataManager.setWorkoutMeasurePeriod(interval);
                    break;
                case "exercise_daily":
                    dataManager.setSupportExerciseDaily(collect);
                    dataManager.setExerciseDailyMeasurePeriod(interval);
                    break;
                case "exercise_week":
                    dataManager.setSupportExerciseWeek(collect);
                    dataManager.setExerciseDailyMeasurePeriod(interval);
                    break;
                case "scientific_sleep":
                    dataManager.setSupportScientificSleep(collect);
                    dataManager.setScientificSleepMeasurePeriod(interval);
                    break;
            }
        }
    }

    // 处理接口数据配置
    private void processInterfaceDataConfig(JSONObject interfaceData) throws JSONException {
        for (String key : interfaceData.keySet()) {
            String value = interfaceData.getString(key);
            String[] parts = value.split(";");

            String url = parts[0];
            int interval = Integer.parseInt(parts[1]);
            boolean isEnabled = Integer.parseInt(parts[2]) == 1;

            HiLog.info(LABEL_LOG, "MainAbilitySlice::processInterfaceDataConfig :: Interface: " + key
                    +"\nurl: " + url  
                    + "\ninterval: " + interval 
                    + "\nisEnabled: " + isEnabled 
                    + "\napiId: " + apiId 
                    + "\napiAuthorization: " + apiAuthorization);

            // 更新API认证信息
            apiId = parts[3];
            storeValue("apiId", apiId);
            dataManager.setApiId(apiId);
            apiAuthorization = parts[4];
            storeValue("apiAuthorization", apiAuthorization);
            dataManager.setApiAuthorization(apiAuthorization);

            // 处理特定接口
            switch (key) {
                case "平台消息交互接口":
                    fetchMessageUrl = url;
                    storeValue("fetchMessageUrl", fetchMessageUrl);
                    dataManager.setFetchMessageUrl(fetchMessageUrl);
                    fetchMessageInterval = interval;
                    storeValue("fetchMessageInterval", String.valueOf(fetchMessageInterval));
                    dataManager.setFetchMessageInterval(fetchMessageInterval);
                    storeValue("fetchMessageEnabled", String.valueOf(isEnabled));
                    fetchMessageEnabled = isEnabled;
                    break;
                case "事件上传接口":
                    uploadCommonEventUrl = url;
                    storeValue("uploadCommonEventUrl", uploadCommonEventUrl);
                    dataManager.setUploadCommonEventUrl(uploadCommonEventUrl);
                    uploadCommonEventInterval = interval;
                    storeValue("uploadCommonEventInterval", String.valueOf(uploadCommonEventInterval));
                    dataManager.setUploadCommonEventInterval(uploadCommonEventInterval);
                    storeValue("uploadCommonEventEnabled", isEnabled ? "1" : "0");
                    uploadCommonEventEnabled = isEnabled;
                    break;
                case "设备信息上传接口":
                    uploadDeviceUrl = url;
                    storeValue("uploadDeviceUrl", uploadDeviceUrl);
                    dataManager.setUploadDeviceInfoUrl(uploadDeviceUrl);
                    uploadDeviceInterval = interval;
                    storeValue("uploadDeviceInterval", String.valueOf(uploadDeviceInterval));
                    dataManager.setUploadDeviceInterval(uploadDeviceInterval);
                    storeValue("uploadDeviceEnabled", String.valueOf(isEnabled));
                    uploadDeviceEnabled = isEnabled;
                    break;
                case "健康数据上传接口":
                    
                    storeValue("uploadHealthDataUrl", url);
                    dataManager.setUploadHealthDataUrl(url);
                    uploadHealthInterval = interval;
                    storeValue("uploadHealthInterval", String.valueOf(uploadHealthInterval));
                    dataManager.setUploadHealthInterval(uploadHealthInterval);
                    storeValue("uploadHealthEnabled", String.valueOf(isEnabled));
                    uploadHealthEnabled = isEnabled;
                    break;
                case "配置获取接口":
                    storeValue("configUrl", url);
                    dataManager.setFetchConfigUrl(url);
                    fetchConfigInterval = interval;
                    HiLog.info(LABEL_LOG, "MainAbilitySlice::processInterfaceDataConfig::fetchConfigInterval:" + fetchConfigInterval);
                    storeValue("fetchConfigInterval", String.valueOf(fetchConfigInterval));
                    dataManager.setFetchConfigInterval(fetchConfigInterval);
                    break;
            }
        }
    }

    // 添加健康服务就绪后启动蓝牙的方法
    private void startBluetoothWhenHealthReady() {
        deviceManager.setBluetoothEnable(true);
        getUITaskDispatcher().asyncDispatch(() -> {
            runBluetooth();
        });
    }
}