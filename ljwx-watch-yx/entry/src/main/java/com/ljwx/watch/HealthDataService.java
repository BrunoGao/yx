package com.ljwx.watch;


import com.tdtech.ohos.health.sensor.IBodySensorDataListener;

import ohos.aafwk.ability.Ability;
import ohos.aafwk.content.Intent;
import ohos.event.commonevent.*;
import ohos.event.notification.NotificationRequest;

import ohos.rpc.IRemoteObject;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import com.tdtech.ohos.health.*;
import com.tdtech.ohos.health.ServiceStateException;
import com.tdtech.ohos.health.StepsQueryConfig;

import com.ljwx.watch.utils.DataManager;
import com.ljwx.watch.utils.Utils;
import ohos.rpc.RemoteException;

import ohos.sensor.agent.CategoryBodyAgent;
import ohos.sensor.bean.CategoryBody;
import ohos.sensor.data.CategoryBodyData;
import ohos.sensor.listener.ICategoryBodyDataCallback;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Timer;
import java.util.TimerTask;


import ohos.event.notification.NotificationHelper;

import java.util.Calendar;
import java.util.TimeZone;
import java.text.SimpleDateFormat;
import java.util.Date;



public class HealthDataService extends Ability {
    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "ljwx-log");

    HealthManager healthManager;
    private DataManager dataManager = DataManager.getInstance();
    boolean mIsServiceReady = false;
    private Timer masterTimer; // 统一主定时器
    private long tick = 0; // 计数器
    private final int basePeriod = 5; // 基础周期5秒（以心率为基准）
    private String customerName = "";
    private HealthDataCache healthDataCache; // 健康数据缓存实例

    // 采集周期和支持状态缓存变量（减少重复计算，节省电量）
    private boolean stepSupported, distanceSupported, calorieSupported, temperatureSupported;
    private boolean bloodOxygenSupported, stressSupported, sleepSupported, exerciseDailySupported;
    private boolean exerciseWeekSupported, scientificSleepSupported, workoutSupported;
    private long heartRatePeriod, stepPeriod, distancePeriod, caloriePeriod, temperaturePeriod;
    private long bloodOxygenPeriod, stressPeriod, sleepPeriod, exerciseDailyPeriod;
    private long exerciseWeekPeriod, scientificSleepPeriod, workoutPeriod;
    private int stepTickInterval, distanceTickInterval, calorieTickInterval, temperatureTickInterval;
    private int bloodOxygenTickInterval, stressTickInterval, sleepTickInterval, exerciseDailyTickInterval;
    private int exerciseWeekTickInterval, scientificSleepTickInterval, workoutTickInterval;

    long endTime = System.currentTimeMillis();
    long startTime = endTime - (endTime % (24 * 60 * 60 * 1000L));




    @Override
    public void onStart(Intent intent) {
        HiLog.info(LABEL_LOG, "HealthDataService::onStart");

        // 初始化健康数据缓存
        HealthDataCache.init(getContext());
        healthDataCache = HealthDataCache.getInstance();
      
        startHealthManager();
        customerName = dataManager.getCustomerName();

    }
    private long getTodayStartTimeMillis() {
        long now = System.currentTimeMillis();
        return now - (now % (24 * 60 * 60 * 1000L));
    }
    private void startHealthManager(){
        NotificationRequest request = new NotificationRequest(1004);
        NotificationRequest.NotificationNormalContent content = new NotificationRequest.NotificationNormalContent();
        content.setTitle("HealthDataService").setText("keepServiceAlive");
        NotificationRequest.NotificationContent notificationContent = new NotificationRequest.NotificationContent(content);
        request.setContent(notificationContent);

        // 绑定通知，1005为创建通知时传入的notificationId
        keepBackgroundRunning(1004, request);
        healthManager = HealthManager.getInstance(getContext());

        HiLog.info(LABEL_LOG, "jjgao::healthManager.init" + healthManager );
        healthManager.init(new HealthInitListener() {
            @Override
            public void onServiceReady() {
                showNotification("健康数据采集服务已启动");
                mIsServiceReady = true;
                dataManager.setIsHealthServiceReady(true);
                enableAutoMeasures();
                setMeasurePeriod();
                enableAlertThreshold();
                getParameterData();
                startRealtimeHealthData();

                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getStepsMeasurePeriod:" + dataManager.getStepsMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getDistanceMeasurePeriod:" + dataManager.getDistanceMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getCalorieMeasurePeriod:" + dataManager.getCalorieMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getBodyTemperatureMeasurePeriod:" + dataManager.getBodyTemperatureMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getBloodOxygenMeasurePeriod:" + dataManager.getBloodOxygenMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getStressMeasurePeriod:" + dataManager.getStressMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getSleepMeasurePeriod:" + dataManager.getSleepMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getExerciseDailyMeasurePeriod:" + dataManager.getExerciseDailyMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getExerciseWeekMeasurePeriod:" + dataManager.getExerciseWeekMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getScientificSleepMeasurePeriod:" + dataManager.getScientificSleepMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getWorkoutMeasurePeriod:" + dataManager.getWorkoutMeasurePeriod());
                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getHeartRateMeasurePeriod:" + dataManager.getHeartRateMeasurePeriod());

                // 初始化缓存变量，避免定时器中重复计算（省电优化）
                initCachedVariables();

                // 统一定时器调度 - 以心率为基数
                masterTimer = new Timer();

                HiLog.info(LABEL_LOG, "jjgao::onServiceReady:basePeriod:" + basePeriod);
                masterTimer.schedule(new TimerTask() {
                    @Override
                    public void run() {
                        tick++;
                        HiLog.info(LABEL_LOG, "jjgao::onServiceReady:tick:" + tick);

                        // 获取当前时间作为endTime
                        long currentTime = System.currentTimeMillis();
                        long startTime = currentTime - 647437;
                        
                        // 步数采集
                        if (stepSupported && tick % stepTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getStepData");
                            //long stepStartTime = currentTime - (stepPeriod * 5);
                            getStepData(startTime, currentTime);
                        }
                        // 距离采集
                        if (distanceSupported && tick % distanceTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getDistanceData");
                            //long distanceStartTime = currentTime - (distancePeriod * 5);
                            getDistanceData(startTime, currentTime);
                        }
                        // 卡路里采集
                        if (calorieSupported && tick % calorieTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getCalorieData");
                            //long calorieStartTime = currentTime - (caloriePeriod * 5);
                            getCalorieData(startTime, currentTime);
                        }
                        // 体温采集
                        if (temperatureSupported && tick % temperatureTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getTemperature");
                            //long temperatureStartTime = currentTime - (temperaturePeriod * 5);
                            getTemperature(startTime, currentTime);
                        }
                        // 血氧采集
                        if (bloodOxygenSupported && tick % bloodOxygenTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getSpo2");
                            //long bloodOxygenStartTime = currentTime - (bloodOxygenPeriod * 5);
                            getSpo2(startTime, currentTime);
                        }
                        // 压力采集
                        if (stressSupported && tick % stressTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getStress");
                            //long stressStartTime = currentTime - (stressPeriod * 5);
                            getStressData(startTime, currentTime);
                        }
                        // 睡眠采集（睡眠数据采用24小时时间窗口）
                        if (sleepSupported && tick % sleepTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getSleep");
                            long sleepStartTime = currentTime - 24 * 60 * 60 * 1000; // 24小时历史数据
                            getSleepData(sleepStartTime, currentTime);
                        }
                        // 日运动采集
                        if (exerciseDailySupported && tick % exerciseDailyTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getExerciseDaily");
                            //long exerciseDailyStartTime = currentTime - (exerciseDailyPeriod * 5);
                            getExerciseDailyData(startTime, currentTime);
                        }
                        // 周运动采集
                        if (exerciseWeekSupported && tick % exerciseWeekTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getExerciseWeek");
                            //long exerciseWeekStartTime = currentTime - (exerciseWeekPeriod * 5);
                            getExerciseWeekData(startTime, currentTime);
                        }
                        // 科学睡眠采集
                        if (scientificSleepSupported && tick % scientificSleepTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getScientificSleep");
                            //long scientificSleepStartTime = currentTime - (scientificSleepPeriod * 5);
                            getScientificSleepData(startTime, currentTime);
                        }
                        // 运动记录采集
                        if (workoutSupported && tick % workoutTickInterval == 0) {
                            HiLog.info(LABEL_LOG, "jjgao::onServiceReady:getWorkout");
                            //long workoutStartTime = currentTime - (workoutPeriod * 5);
                            getWorkoutData(startTime, currentTime);
                        }                     

                        // 防止计数器溢出
                        if (tick >= 3600) tick = 0;
                    }
                }, 0, basePeriod * 1000);

                //getWearStatus();
                showNotification("开始采集健康数据");
                getCommonEvent();

            }
            @Override
            public void onServiceDisconnect(int errCode) {
                mIsServiceReady = false;
                stopRealtimeHealthData();
                disableAlert();
                showNotification("停止采集健康数据");
                dataManager.setIsHealthServiceReady(false);
                HiLog.info(LABEL_LOG, "jjgao::onServiceDisconnect");
            }
        });
    }
    private void stopHealthManager(){
        HealthManager.getInstance(getContext()).release();
        HiLog.info(LABEL_LOG, "HealthManager.getInstance(getContext()).release() ");
    }
    private void disableAutoMeasures(){
        //(1004, "HealthDataService", "disableAutoMeasures");
        HiLog.info(LABEL_LOG, "jjgao::disableAutoMeasures");
        HiLog.info(LABEL_LOG, "jjgao::disableAutoMeasures:isSupportTemperature:" + dataManager.isSupportTemperature());
        HiLog.info(LABEL_LOG, "jjgao::disableAutoMeasures:isSupportBloodOxygen:" + dataManager.isSupportBloodOxygen());
        HiLog.info(LABEL_LOG, "jjgao::disableAutoMeasures:isSupportHeartRate:" + dataManager.isSupportHeartRate());
        HiLog.info(LABEL_LOG, "jjgao::disableAutoMeasures:isSupportStress:" + dataManager.isSupportStress());
        HiLog.info(LABEL_LOG, "jjgao::disableAutoMeasures:isSupportSleep:" + dataManager.isSupportSleep());
        HiLog.info(LABEL_LOG, "jjgao::disableAutoMeasures:isSupportExerciseDaily:" + dataManager.isSupportExerciseDaily());
        HiLog.info(LABEL_LOG, "jjgao::disableAutoMeasures:isSupportExerciseWeek:" + dataManager.isSupportExerciseWeek());
        try {
            if(dataManager.isSupportTemperature()){
                HealthManager.getInstance(getContext()).switchOffBodyTemperatureAutoMeasure();
            }
            if(dataManager.isSupportBloodOxygen()){
                HealthManager.getInstance(getContext()).switchOffSpo2AutoMeasure();
            }
            if(dataManager.isSupportHeartRate()){
                HealthManager.getInstance(getContext()).switchOffHeartRateContinueMeasure();
            }
            if(dataManager.isSupportStress()){
                HealthManager.getInstance(getContext()).switchOffStressAutoMeasure();
            }

        } catch (ServiceStateException e) {
            throw new RuntimeException(e);
        }
    }




    private void enableAlertThreshold(){
        try {
            HiLog.info(LABEL_LOG, "jjgao::enableAlertThreshold:heartRateWarningHigh:" + dataManager.getHeartRateWarningHigh() + " heartRateWarningLow:" + dataManager.getHeartRateWarningLow());
            int heartRateWarningHigh = dataManager.getHeartRateWarningHigh();
            if(heartRateWarningHigh <= 0){
                heartRateWarningHigh = 100;
            }
            int heartRateWarningLow = dataManager.getHeartRateWarningLow();
            if(heartRateWarningLow <= 0){
                heartRateWarningLow = 60;
            }
            int spo2Warning = dataManager.getSpo2Warning();
            HiLog.info(LABEL_LOG, "jjgao::enableAlertThreshold:spo2Warning:" + spo2Warning);
            if(spo2Warning <= 0){
                spo2Warning = 90;
            }
            int stressWarning = dataManager.getStressWarning();
            if(stressWarning <= 0){
                stressWarning = 66;
            }

            float temperatureWarningHigh = (float) dataManager.getBodyTemperatureWarningHigh();
            HiLog.info(LABEL_LOG, "jjgao::enableAlertThreshold:temperatureWarningHigh:" + temperatureWarningHigh);
            if(temperatureWarningHigh <= 0){
                temperatureWarningHigh = 37.5f;
            }
            float temperatureWarningLow = (float) dataManager.getBodyTemperatureWarningLow();
            HiLog.info(LABEL_LOG, "jjgao::enableAlertThreshold:temperatureWarningLow:" + temperatureWarningLow);
            if(temperatureWarningLow <= 0){
                temperatureWarningLow = 35.0f;
            }
            HealthManager.getInstance(getContext()).setHeartRateWarning(heartRateWarningHigh, heartRateWarningLow);
            HiLog.info(LABEL_LOG, "jjgao::enableAlertThreshold:heartRateWarningCnt:" + dataManager.getHeartRateWarningCnt());
            HealthManager.getInstance(getContext()).setHeartWarningCnt(dataManager.getHeartRateWarningCnt());
       
            HealthManager.getInstance(getContext()).setSpo2Warning(spo2Warning);
            HiLog.info(LABEL_LOG, "jjgao::enableAlertThreshold:spo2WarningCnt:" + dataManager.getSpo2WarningCnt());
            HealthManager.getInstance(getContext()).setSpo2WarningCnt(dataManager.getSpo2WarningCnt());
            HealthManager.getInstance(getContext()).setStressWarning(stressWarning);
         
            HealthManager.getInstance(getContext()).setBodyTemperatureWarning(temperatureWarningHigh, temperatureWarningLow);
            HealthManager.getInstance(getContext()).setBodyTemperatureWarningCnt(dataManager.getBodyTemperatureWarningCnt());

        } catch (ServiceStateException | GenericException e) {
            //System.out.println("jjgao::setAlertThreshold:error:" + e);
            HiLog.error(LABEL_LOG, "jjgao::setAlertThreshold:error:" + e);
        }
    }
    private void setMeasurePeriod(){
        try {
            if(dataManager.isSupportHeartRate()){
                long heartRateMeasurePeriod = dataManager.getHeartRateMeasurePeriod();
                if(heartRateMeasurePeriod <= 5){
                    heartRateMeasurePeriod = 5;
                }
                long heartRateMeasurePeriodMillis = heartRateMeasurePeriod * 1000L;
                HiLog.info(LABEL_LOG, "jjgao::setMeasurePeriod:heartRateMeasurePeriod:" + heartRateMeasurePeriod);
                HealthManager.getInstance(getContext()).setHeartRateMeasurePeriod(heartRateMeasurePeriodMillis,false);
            }
            if(dataManager.isSupportBloodOxygen()){
                long spo2MeasurePeriod = dataManager.getBloodOxygenMeasurePeriod();
                if(spo2MeasurePeriod <= 120){
                    spo2MeasurePeriod = 120;
                }
                long spo2MeasurePeriodMillis = spo2MeasurePeriod * 1000L;
                HiLog.info(LABEL_LOG, "jjgao::setMeasurePeriod:spo2MeasurePeriod:" + spo2MeasurePeriodMillis);
                HealthManager.getInstance(getContext()).setSpo2MeasurePeriod(spo2MeasurePeriodMillis, false);
            }
            if(dataManager.isSupportStress()){
                long stressMeasurePeriod = dataManager.getStressMeasurePeriod();
                if(stressMeasurePeriod <= 1800){
                    stressMeasurePeriod = 1800;
                }
                long stressMeasurePeriodMillis = stressMeasurePeriod * 1000L;
                HiLog.info(LABEL_LOG, "jjgao::setMeasurePeriod:stressMeasurePeriod:" + stressMeasurePeriodMillis);
                HealthManager.getInstance(getContext()).setStressMeasurePeriod(stressMeasurePeriodMillis,false);
            }
            if(dataManager.isSupportTemperature()){
                long temperatureMeasurePeriod = dataManager.getBodyTemperatureMeasurePeriod();
                if(temperatureMeasurePeriod <= 20){
                    temperatureMeasurePeriod = 20;
                }
                long temperatureMeasurePeriodMillis = temperatureMeasurePeriod * 1000L;
                HiLog.info(LABEL_LOG, "jjgao::setMeasurePeriod:temperatureMeasurePeriod:" + temperatureMeasurePeriodMillis);
                HealthManager.getInstance(getContext()).setBodyTemperaMeasurePeriod(temperatureMeasurePeriodMillis, false);
            }
        } catch (ServiceStateException | WrongStateException | GenericException e) {
            System.out.println("jjgao::setMeasurePeriod:error:" + e);
            HiLog.error(LABEL_LOG, "jjgao::setMeasurePeriod:error:" + e);
        }
    }
    private void disableAlert(){
        try {
            HealthManager.getInstance(getContext()).cancelHeartRateWarning();
            HealthManager.getInstance(getContext()).cancelSpo2Warning();
            HealthManager.getInstance(getContext()).cancelStressWarning();
            HealthManager.getInstance(getContext()).cancelBodyTemperatureWarning();

        } catch (ServiceStateException  e) {
            //System.out.println("jjgao::setAlertThreshold:error:" + e);
            HiLog.error(LABEL_LOG, "jjgao::setAlertThreshold:error:" + e);
        }
    }
    private void enableAutoMeasures(){
        //showNotification(1003, "HealthDataService", "enableAutoMeasures");
        try {

                HealthManager.getInstance(getContext()).switchOnBodyTemperatureAutoMeasure();     
                HealthManager.getInstance(getContext()).switchOnSpo2AutoMeasure();
                HealthManager.getInstance(getContext()).switchOnHeartRateContinueMeasure();
                float[] feature = new float[12];
                HealthManager.getInstance(getContext()).setStressInquiryData(60, System.currentTimeMillis(), feature);
                HealthManager.getInstance(getContext()).switchOnStressAutoMeasure();
            

        } catch (ServiceStateException | WrongStateException | GenericException e) {
            //System.out.println("jjgao::enableAutoMeasures:error:" + e);
            HiLog.error(LABEL_LOG, "jjgao::enableAutoMeasures:error:" + e);
        }
    }

    private void getParameterData(){
        String heartRemindParamJson = "";
     
        try {
            heartRemindParamJson = HealthManager.getInstance(getContext()).queryHeartRemindParam();
            HiLog.info(LABEL_LOG, "jjgao::heartRemindParamJson " + heartRemindParamJson);
            
        } catch (ServiceStateException | JSONException e) {
            HiLog.error(LABEL_LOG, "jjgao::getParameterData:error:" + e);
            throw new RuntimeException(e);
        }

        String spo2RemindParamJson = "";
     
        try {
            spo2RemindParamJson = HealthManager.getInstance(getContext()).querySpo2RemindParam();;
            HiLog.info(LABEL_LOG, "jjgao::spo2RemindParamJson " + spo2RemindParamJson);
            
        } catch (ServiceStateException | JSONException e) {
            HiLog.error(LABEL_LOG, "jjgao::getParameterData:error:" + e);
            throw new RuntimeException(e);
        }

        String temperatureRemindParamJson = "";
     
        try {
            temperatureRemindParamJson = HealthManager.getInstance(getContext()).queryTemperatureRemindParam();
            HiLog.info(LABEL_LOG, "jjgao::temperatureRemindParamJson " + temperatureRemindParamJson);
            
        } catch (ServiceStateException | JSONException e) {
            HiLog.error(LABEL_LOG, "jjgao::getParameterData:error:" + e);
            throw new RuntimeException(e);
        }


    }
    private void getDistanceData(long startTime, long endTime){
        String distancJson = "";
       
        try {
            distancJson = HealthManager.getInstance(getContext()).queryDistanceInRange(new DistanceQueryConfig.Builder().setStartTime(startTime).setEndTime(endTime).build());
            
            int distanceValue = (int) fetchFromJson(distancJson);
            HiLog.info(LABEL_LOG, "jjgao::distanceJson " + distanceValue) ;
            if (distanceValue != 0) {
                dataManager.setDistance(distanceValue);
            }

        } catch (ServiceStateException | JSONException e) {
            HiLog.error(LABEL_LOG, "jjgao::getDistanceData:error:" + e);
            throw new RuntimeException(e);
        }
    }
    
    private void getExerciseDailyData(long startTime, long endTime){
        String exerciseJson = "";
        try {
            exerciseJson = HealthManager.getInstance(getContext()).queryExerciseDailyRecord();
          
            HiLog.info(LABEL_LOG, "jjgao::getExerciseDailyData " + exerciseJson) ;
            
            dataManager.setExerciseDailyData(exerciseJson.toString());
            

        } catch (ServiceStateException | JSONException e) {
            HiLog.error(LABEL_LOG, "jjgao::getExerciseDailyData:error:" + e);
            throw new RuntimeException(e);
        }
    }

    private void getExerciseWeekData(long startTime, long endTime){
        String exerciseJson = "";
        try {
            exerciseJson = HealthManager.getInstance(getContext()).queryExerciseDailyWeekRecord();
            dataManager.setExerciseWeekData(exerciseJson.toString());
   
            HiLog.info(LABEL_LOG, "jjgao::getExerciseDailyWeekData " + exerciseJson);

        } catch (ServiceStateException | JSONException e) {
            HiLog.error(LABEL_LOG, "jjgao::getExerciseWeekData:error:" + e);
            throw new RuntimeException(e);
        }
    }

    private void getScientificSleepData(long startTime, long endTime){
        HealthManager.getInstance(getContext()).queryScientificSleepRecords(new SleepQueryConfig.Builder().setStartTime(startTime).setEndTime(endTime).build(), new ScientificSleepListener()
    {
        @Override
        public void onReceive(int i, String s) {
            dataManager.setScientificSleepData(s);
            HiLog.debug(LABEL_LOG, "onReceive i: " + i +" s: " + s);
            
        }
        @Override
        public void onError(int i) {
            HiLog.debug(LABEL_LOG, "onError i: " + i);
            }
        });
    }

    private void getWorkoutData(long startTime, long endTime){
        String workoutJson = "";
        
        try {
            workoutJson = HealthManager.getInstance(getContext()).queryWorkoutRecords(new WorkoutQueryConfig.Builder().build());
            //System.out.println("jjgao::workoutJson " + workoutJson) ;
            dataManager.setWorkoutData(workoutJson.toString());

        } catch (ServiceStateException | JSONException e) {
            HiLog.error(LABEL_LOG, "jjgao::getWorkoutData:error:" + e);
            throw new RuntimeException(e);
        }
    }


    private void getStepData(long startTime, long endTime){
        String stepJson = "";
        try {
            stepJson = HealthManager.getInstance(getContext()).queryStepsInRange(new StepsQueryConfig.Builder().setStartTime(startTime).setEndTime(endTime).build());
            //HiLog.info(LABEL_LOG, "jjgao::stepJson " + stepJson);
            int stepValue = (int) fetchFromJson(stepJson);
            //System.out.println("jjgao::stepJson " + stepValue) ;
            //HiLog.info(LABEL_LOG, "jjgao::stepJson " + stepValue) ;
            if (stepValue != 0) {
                dataManager.setStep(stepValue);
            }

        } catch (ServiceStateException | JSONException e) {
            HiLog.error(LABEL_LOG, "jjgao::getStepData:error:" + e);
            throw new RuntimeException(e);
        }
    }


    private void getSleepData(long startTime, long endTime) {
        
        try {
            String data = HealthManager.getInstance(getContext()).querySleepRecords(new SleepQueryConfig.Builder().setStartTime(startTime).setEndTime(endTime).setType(SleepQueryConfig.TYPE_SCIENCE).build());

            // Parse the JSON data
            JSONObject jsonObject = new JSONObject(data);
            HiLog.info(LABEL_LOG, "jjgao::getSleepData:jsonObject:" + jsonObject.toString());
            dataManager.setSleepData(jsonObject.toString());
            int code = jsonObject.getInt("code");
            //HiLog.info(LABEL_LOG, "jjgao::getSleepData:code:" + code);
            if (code == 0) {
                JSONArray dataArray = jsonObject.getJSONArray("data");
                //HiLog.info(LABEL_LOG, "jjgao::getSleepData:" + dataArray.toString());
                //dataManager.setSleepData(dataArray.toString());
                for (int i = 0; i < dataArray.length(); i++) {
                    JSONObject sleepRecord = dataArray.getJSONObject(i);
                    long startTimeStamp = sleepRecord.getLong("startTimeStamp");
                    long endTimeStamp = sleepRecord.getLong("endTimeStamp");
                    int type = sleepRecord.getInt("type");

                    // Process the sleep data as needed
                    //HiLog.info(LABEL_LOG, "Sleep Record: Start - " + startTimeStamp + ", End - " + endTimeStamp + ", Type - " + type);
                   
                }
            } else {
                HiLog.info(LABEL_LOG, "Error in fetching sleep data, code: " + code);
            }
        } catch (ServiceStateException | JSONException e) {
            HiLog.error(LABEL_LOG, "jjgao::getSleepData:error:" + e);
            throw new RuntimeException(e);
        }
    }


    private void getCalorieData(long startTime, long endTime){
        
        String calorieJson = "";
        try {
            calorieJson =  HealthManager.getInstance(getContext()).queryCalorieInRange (new CalorieQueryConfig.Builder().setStartTime(startTime).setEndTime(endTime).build());
            int calorieValue = (int) fetchFromJson(calorieJson);
            if (calorieValue != 0) {
                dataManager.setCalorie(calorieValue);
            }
            //System.out.println("jjgao::calorieJson " + calorieValue) ;
            //HiLog.info(LABEL_LOG, "jjgao::calorieJson " + calorieValue) ;

        } catch (ServiceStateException | JSONException e) {
            throw new RuntimeException(e);
        }
    }

    private void getStressData(long startTime, long endTime){
       
        String stressJson = "";
        try {
            stressJson =  HealthManager.getInstance(getContext()).queryStressRecords(new StressQueryConfig.Builder().
            setStartTime(startTime).
            setEndTime(endTime).
            build());
            //System.out.println("jjgao::stressJson history:" + (int) fetchFromJson(stressJson)) ;
          
            int stressValue = (int) fetchFromJson(stressJson);
            //HiLog.info(LABEL_LOG, "jjgao::stressJson history:" + stressValue) ;
            if (stressValue != 0) {
                dataManager.setStress(stressValue);
            }

        } catch (ServiceStateException | JSONException e) {
            throw new RuntimeException(e);
        }
    }


    private void getSpo2(long startTime, long endTime){

        String spo2Json = "";
        try {
            spo2Json = HealthManager.getInstance(getContext()).querySpo2Records(new Spo2QueryConfig.Builder().setStartTime(startTime).setEndTime(endTime).build());
            HiLog.info(LABEL_LOG, "jjgao::spo2Json " + spo2Json);
            int spo2Value = (int) fetchFromJson(spo2Json);
            if (spo2Value != 0) {
                dataManager.setBloodOxygen(spo2Value);
            }
            //System.out.println("jjgao::getSpo2:history" + dataManager.getBloodOxygen());
            //HiLog.info(LABEL_LOG, "jjgao::getSpo2:history" + spo2Value);
        } catch (ServiceStateException | JSONException e) {
            throw new RuntimeException(e);
        }
    }

    private void getHeartRate(long startTime, long endTime) {
        String heartRateJson = "";
        try {
            //HiLog.info(LABEL_LOG, "jjgao::getHeartRate:startTime:" + startTime + " endTime:" + endTime);
            heartRateJson = HealthManager.getInstance(getContext()).queryHeartRateRecords(new HeartRateQueryConfig.Builder().setStartTime(startTime).setEndTime(endTime).build());
            HiLog.info(LABEL_LOG, "jjgao::heart_rate:history" + heartRateJson) ;
            int heartRate = (int) fetchFromJson(heartRateJson);
            //System.out.println("jjgao::heart_rate:history" + heartRate) ;
            //HiLog.info(LABEL_LOG, "jjgao::heart_rate:history" + heartRate) ;
         
            if (heartRate != 0) {
                dataManager.setHeartRate(heartRate);
                calculateBloodPressure(heartRate);
            }
            
            
        } catch (ServiceStateException | JSONException e) {
            throw new RuntimeException(e);
        }
    }

    private void getTemperature(long startTime, long endTime) {
        String temperatureJson = "";
        
        try {
            temperatureJson = HealthManager.getInstance(getContext()).queryBodyTemperatureRecords(new BodyTemperatureQueryConfig.Builder().setStartTime(startTime).setEndTime(endTime).build());
            HiLog.info(LABEL_LOG, "jjgao::temperatureJson " + temperatureJson);
            double temperature = fetchFromJson(temperatureJson);
            //HiLog.info(LABEL_LOG, "jjgao::Temperature:history" + temperature);
            if (temperature != 0.0) {
                dataManager.setTemperature(temperature);
            }
        } catch (ServiceStateException | JSONException e) {
            throw new RuntimeException(e);
        }
    }

    private static final long INTERVAL = 5000L;

    private CategoryBodyAgent categoryBodyAgent = new CategoryBodyAgent();

    private ICategoryBodyDataCallback bodyDataCallback;

    private void getWearStatus(){
        bodyDataCallback = new ICategoryBodyDataCallback() {
            @Override
            public void onSensorDataModified(CategoryBodyData categoryBodyData) {

                int wearState = (int) categoryBodyData.getValues()[0];
                HiLog.info(LABEL_LOG, "jjgao::getWearStatus:wearState " + wearState);
                dataManager.setWearState(wearState);
                HiLog.info(LABEL_LOG, "jjgao::getWearStatus:wearState " + dataManager.getWearState());
                //HiLog.info(LABEL_LOG, "wearState " + wearState);
                if (wearState == 1) {
                    //HiLog.info(LABEL_LOG, "The watch is being worn.");
                } else {
                    //HiLog.info(LABEL_LOG, "The watch is not being worn.");
                }

            }

            @Override
            public void onAccuracyDataModified(CategoryBody categoryBody, int i) {

            }

            @Override
            public void onCommandCompleted(CategoryBody categoryBody) {

            }

        };

            // 获取传感器对象，并订阅传感器数据
        CategoryBody wearSensor = categoryBodyAgent.getSingleSensor(
                CategoryBody.SENSOR_TYPE_WEAR_DETECTION);
            if (wearSensor != null) {
                categoryBodyAgent.setSensorDataCallback(bodyDataCallback, wearSensor, INTERVAL);
            }
    }

    private static int notificationId = 1000;

    private void showNotification(String textContent) {
        //HiLog.info(LABEL_LOG, "showNotification" + textContent);
        NotificationRequest request = new NotificationRequest(notificationId++);
        NotificationRequest.NotificationNormalContent content = new NotificationRequest.NotificationNormalContent();
        content.setTitle(customerName)
                .setText(textContent);
        NotificationRequest.NotificationContent notificationContent = new NotificationRequest.NotificationContent(content);
        request.setContent(notificationContent);
        try {
            NotificationHelper.publishNotification(request);
            keepBackgroundRunning(notificationId, request);
        } catch (RemoteException ex) {
            ex.printStackTrace();
        }
    }
    public void startRealtimeHealthData() {
 
        HiLog.info(LABEL_LOG, "jjgao::startRealtimeHealthData:start");
        IBodySensorDataListener mListener = new IBodySensorDataListener() {
            @Override
            public void onSensorDataUpdate(int errCode, String s) {
                //System.out.println("jjgao::getRealtimeHealthData:errCode:" + errCode + " content " + s);
                //HiLog.info(LABEL_LOG, "jjgao::getRealtimeHealthData:errCode:" + errCode + " content " + s);
                if (errCode == HealthManager.ERR_SUCCESS) {
                    try {
                        JSONObject object = new JSONObject(s);
                        String name = object.getString("name").trim();
                        //System.out.println("jjgao::getRealtimeHealthData:name:" + name);
                        //HiLog.info(LABEL_LOG, "jjgao::getRealtimeHealthData:name:" + name);
                        JSONArray dataArray = object.getJSONArray("data");
                        if (dataArray.length() > 0) {
                            JSONObject dataObject = dataArray.getJSONObject(0);
                            int data = dataObject.getInt("data");
                            switch (name) {
                                case "heart_rate":
                                    if(dataManager.isHeartRateIsRealtime()){
                                        dataManager.setHeartRate(data);
                                        calculateBloodPressure(data);
                                        HiLog.info(LABEL_LOG, "jjgao::realtime heart_rate:" + data);
                                    }
                                    break;

                                case "spo2":
                                    if(dataManager.isBloodOxygenIsRealtime()){
                                        dataManager.setBloodOxygen(data);
                                        HiLog.info(LABEL_LOG, "jjgao::realtime spo2:" + data);
                                    }
                                    break;
                                case "temperature":
                                    if(dataManager.isBodyTemperatureIsRealtime()){
                               
                                        dataManager.setTemperature(dataObject.getDouble("data"));
                                        HiLog.info(LABEL_LOG, "jjgao::realtime temperature:" + data);
                                    }
                                    break;

                                case "stress":
                                    if(dataManager.isSupportStress() && dataManager.isStressIsRealtime()){
                                 
                                        dataManager.setStress(data);
                                        HiLog.info(LABEL_LOG, "jjgao::realtime stress:" + data);
                                    }
                                    break;

                            }
                            //HiLog.info(LABEL_LOG, "jjgao::Updated " + name + " to " + data);
                        }
                    } catch (JSONException e) {
                        //System.out.println("Error parsing sensor data: " + e.getMessage());
                        HiLog.error(LABEL_LOG, "Error parsing sensor data: " + e.getMessage());
                    }
                }
            }

            @Override
            public void onError(int errCode) {
                //System.out.println("Sensor error: " + errCode);
                HiLog.error(LABEL_LOG, "Sensor error: " + errCode);
            }
        };

        HealthManager.getInstance(getContext()).getHeartRateSensor().startMeasureHeartRate(mListener);    
        HealthManager.getInstance(getContext()).getSpo2Sensor().startMeasureSpo2(mListener);
        HealthManager.getInstance(getContext()).getBodyTemperatureSensor().startMeasureBodyTemperature(mListener);
        HealthManager.getInstance(getContext()).getStressSensor().startMeasureStress(mListener);
        //HealthManager.getInstance(getContext()).getMotionSensor().startMeasureMotion(mListener);

    }

    public void stopRealtimeHealthData() {
        HiLog.info(LABEL_LOG, "jjgao::stopRealtimeHealthData:start");
        IBodySensorDataListener mListener = new IBodySensorDataListener() {
            @Override
            public void onSensorDataUpdate(int errCode, String s) {
                //System.out.println("jjgao::getRealtimeHealthData:errCode:" + errCode + " content " + s);
                
            }
            @Override
            public void onError(int errCode) {
                HiLog.info(LABEL_LOG, "Sensor error: " + errCode);
            }
        };

        HealthManager.getInstance(getContext()).getHeartRateSensor().stopMeasureHeartRate(mListener);
       
        HealthManager.getInstance(getContext()).getSpo2Sensor().stopMeasureSpo2(mListener);
      
        HealthManager.getInstance(getContext()).getBodyTemperatureSensor().stopMeasureBodyTemperature(mListener);
       
        HealthManager.getInstance(getContext()).getStressSensor().stopMeasureStress(mListener);

        //HealthManager.getInstance(getContext()).getMotionSensor().stopMeasureMotion(mListener);
        
        disableAutoMeasures();
    }

    private int map(int x, int inMin, int inMax, int outMin, int outMax) {
        return (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin;
    }

    public  void calculateBloodPressureHistory(int heartRate) {
        if (heartRate < 0 || heartRate > 255) {
            throw new IllegalArgumentException("Heart rate must be between 0 and 255.");
        }

        // 定义心率到血压的映射范围
        int minSystolic = 40;  // 最低高压
        int maxSystolic = 300; // 最高高压
        int minDiastolic = 30;  // 最低低压
        int maxDiastolic = 200; // 最高低压

        // 计算高压和低压
        int systolic = map(heartRate, 0, 255, minSystolic, maxSystolic);
        int diastolic = map(heartRate, 0, 255, minDiastolic, maxDiastolic);
        dataManager.setPressureHighHistory(systolic);
        dataManager.setPressureLowHistory(diastolic);

    }

    public  void calculateBloodPressure(int heartRate) {
        if (heartRate < 0 || heartRate > 255) {
            throw new IllegalArgumentException("Heart rate must be between 0 and 255.");
        }

        // 定义心率到血压的映射范围
        int minSystolic = 40;  // 最低高压
        int maxSystolic = 300; // 最高高压
        int minDiastolic = 30;  // 最低低压
        int maxDiastolic = 200; // 最高低压

        // 计算高压和低压
        int systolic = map(heartRate, 0, 255, minSystolic, maxSystolic);
        int diastolic = map(heartRate, 0, 255, minDiastolic, maxDiastolic);
        dataManager.setPressureHigh(systolic);
        dataManager.setPressureLow(diastolic);

    }
    public double fetchFromJson(String json){
        double value = 0;
        JSONObject jsonObject = new JSONObject(json);
        String name = jsonObject.getString("name").trim();
        JSONArray dataArray = jsonObject.getJSONArray("data");
        //System.out.println("jjgao::ataArray.length()" + dataArray.length()) ;
        //System.out.println("jjgao::fetchFromJson" + dataArray.toString()) ;
        if (dataArray.length() > 0) {
            JSONObject latestDataObject = dataArray.getJSONObject(dataArray.length() - 1);
            //System.out.println("jjgao::fetchFromJson" + latestDataObject.toString()) ;
            if(name.equalsIgnoreCase("temperature")){
                value = latestDataObject.getDouble("data");
            }else{
                value = latestDataObject.getInt("data");
            }
            //System.out.println("First data value: " + value);
        }
        return value;
    }

    private void getCommonEvent() {
        HiLog.info(LABEL_LOG, "HealthDataService::getCommonEvent:start");
        MatchingSkills matchingSkills = new MatchingSkills();
        matchingSkills.addEvent("com.tdtech.ohos.action.WEAR_STATUS_CHANGED");
        matchingSkills.addEvent("com.tdtech.ohos.health.action.FALLDOWN_EVENT");
        matchingSkills.addEvent("com.tdtech.ohos.health.action.STRESS_HIGH_ALERT");
        matchingSkills.addEvent("com.tdtech.ohos.health.action.SPO2_LOW_ALERT");
        matchingSkills.addEvent("com.tdtech.ohos.health.action.HEARTRATE_HIGH_ALERT");
        matchingSkills.addEvent("com.tdtech.ohos.health.action.HEARTRATE_LOW_ALERT");
        matchingSkills.addEvent("com.tdtech.ohos.health.action.TEMPERATURE_HIGH_ALERT");
        matchingSkills.addEvent("com.tdtech.ohos.health.action.TEMPERATURE_LOW_ALERT");
        matchingSkills.addEvent("com.tdtech.ohos.health.action.PRESSURE_HIGH_ALERT");
        matchingSkills.addEvent("com.tdtech.ohos.health.action.PRESSURE_LOW_ALERT");
        matchingSkills.addEvent("com.tdtech.ohos.action.ONE_KEY_ALARM");
        matchingSkills.addEvent("com.tdtech.ohos.action.CALL_STATE");
        matchingSkills.addEvent("com.tdtech.ohos.action.BOOT_COMPLETED");
        matchingSkills.addEvent("com.tdtech.ohos.action.UI_SETTINGS_CHANGED");
        matchingSkills.addEvent("com.tdtech.ohos.action.FUN_DOUBLE_CLICK");
        matchingSkills.addEvent("com.tdtech.ohos.health.action.SOS_EVENT");

        CommonEventSubscribeInfo commonEventSubscribeInfo = new CommonEventSubscribeInfo(matchingSkills);
        try {
            CommonEventManager.subscribeCommonEvent(new CommonEventSubscriber(commonEventSubscribeInfo) {
                @Override
                public void onReceiveEvent(CommonEventData commonEventData) {
                    String commonEventType = commonEventData.getIntent().getAction();
                    
                    
                    HiLog.info(LABEL_LOG, "HealthDataService::getCommonEvent:action:" + commonEventType);
                    String value = "";
                    String deviceSn = dataManager.getDeviceSn();

                    switch (commonEventType) {
                        case "com.tdtech.ohos.action.WEAR_STATUS_CHANGED":
                            // Handle wear status changed
                            value = commonEventType + ":" + String.valueOf(commonEventData.getIntent().getIntParam("wear_status",0)+":" + deviceSn);
                            dataManager.setCommonEvent(value);
                            
                            break;
                        case "com.tdtech.ohos.health.action.FALLDOWN_EVENT":
                            // Handle fall down event
                            value = commonEventType + ":" + commonEventData.getIntent().getStringParam("alarmstate")+":" + deviceSn;

                            dataManager.setCommonEvent("value");
                            break;
                        case "com.tdtech.ohos.health.action.STRESS_HIGH_ALERT":
                            // Handle stress high alert
                            value = commonEventType + ":" +  commonEventData.getIntent().getStringParam("stress")+":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "Stress high alert: " + value);
                            break;
                        case "com.tdtech.ohos.health.action.SPO2_LOW_ALERT":
                            // Handle SPO2 low alert
                       
                            value = commonEventType + ":" +  commonEventData.getIntent().getStringParam("spo2")+":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "SPO2 low alert: " + value);
                            break;
                        case "com.tdtech.ohos.health.action.HEARTRATE_HIGH_ALERT":
                            // Handle heart rate high alert
                            value = commonEventType + ":" +  commonEventData.getIntent().getStringParam("heartRate")+":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "Heart rate high alert: " + value);
                            break;
                        case "com.tdtech.ohos.health.action.HEARTRATE_LOW_ALERT":
                            // Handle heart rate low alert
                            value = commonEventType + ":" +  commonEventData.getIntent().getStringParam("heartRate")+":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "Heart rate low alert: " + value);
                            break;
                        case "com.tdtech.ohos.health.action.TEMPERATURE_HIGH_ALERT":
                            // Handle temperature high alert
                            value = commonEventType + ":" +  commonEventData.getIntent().getStringParam("temperature")+":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "Temperature high alert: " + value);
                            break;
                        case "com.tdtech.ohos.health.action.TEMPERATURE_LOW_ALERT":
                            // Handle temperature low alert
                            value = commonEventType + ":" +  commonEventData.getIntent().getStringParam("temperature")+":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "Temperature low alert: " + value);
                            break;
                        case "com.tdtech.ohos.health.action.PRESSURE_HIGH_ALERT":
                            // Handle pressure high alert
                            value = commonEventType + ":" +  commonEventData.getIntent().getStringParam("pressure")+":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "Pressure high alert: " + value);
                            break;
                        case "com.tdtech.ohos.health.action.PRESSURE_LOW_ALERT":
                            // Handle pressure low alert
                            value = commonEventType + ":" +  commonEventData.getIntent().getStringParam("pressure")+":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "Pressure low alert: " + value);
                            break;
                        case "com.tdtech.ohos.action.ONE_KEY_ALARM":
                            // Handle one key alarm #一键报警事件处理，尝试多参数名并判空
                            value = commonEventType + ":" + deviceSn; //判空处理
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "One key alarm: " + value);
                            break;
                        case "com.tdtech.ohos.action.CALL_STATE":
                            // Handle call state
                            value = commonEventType +":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "Call state: " + value);
                            break;
                        case "com.tdtech.ohos.action.BOOT_COMPLETED":
                            // Handle boot completed
                            value = commonEventType + ":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "Boot completed: " + value);
                            break;
                        case "com.tdtech.ohos.action.UI_SETTINGS_CHANGED":
                            // Handle UI settings changed
                            value = commonEventType + ":" +  commonEventData.getIntent().getStringParam("location_service_switch")+":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "UI settings changed: " + value);
                            break;
                        case "com.tdtech.ohos.action.FUN_DOUBLE_CLICK":
                            // Handle fun double click
                            value = commonEventType +":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "Fun double click: " + value);
                            break;
                        case "com.tdtech.ohos.health.action.SOS_EVENT":
                            // Handle SOS event
                            value = commonEventType + ":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            HiLog.info(LABEL_LOG, "SOS event: " + value);
                            break;
                        default:
                            HiLog.info(LABEL_LOG, "Unknown event type: " + commonEventType);
                            value = commonEventType + ":" + deviceSn;
                            dataManager.setCommonEvent(value);
                            break;
                    }
                }
            });
        } catch (RemoteException e) {
            HiLog.error(LABEL_LOG, "HealthDataService::getCommonEvent:error:" + e);
        }
    }

    @Override
    public void onBackground() {
        super.onBackground();
        HiLog.info(LABEL_LOG, "HealthDataService::onBackground");
    }

    @Override
    public void onStop() {
        super.onStop();
        if (masterTimer != null) {
            masterTimer.cancel(); // 停止统一主定时器
        }
        stopHealthManager();
        showNotification( "退出健康数据服务");
    }

    @Override
    public void onCommand(Intent intent, boolean restart, int startId) {
        super.onCommand(intent, restart, startId);
        if(intent != null){
            HiLog.info(LABEL_LOG, "HealthDataService::onCommand" + intent.getAction());
            if(intent.getAction() != null){
                HiLog.info(LABEL_LOG, "HealthDataService::onCommand" + intent.getAction());
                if(intent.getAction().equals("com.tdtech.ohos.action.WEAR_STATUS_CHANGE")) {
                    int status = intent.getIntParam("wear_status",0);
                    HiLog.info(LABEL_LOG, "HealthDataService::onCommand:wear_status:" + status);
                }
            }

        }
    }
    @Override
    public IRemoteObject onConnect(Intent intent) {
        return null;
    }

    @Override
    public void onDisconnect(Intent intent) {
        super.onDisconnect(intent);
    }

    private String getCurrentFormattedTime() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        return sdf.format(new Date());
    }

    // Example usage within the class
    private void logCurrentTime() {
        String formattedTime = getCurrentFormattedTime();
        HiLog.info(LABEL_LOG, "Current Time: " + formattedTime);
    }

    // 缓存当前健康数据
    private void cacheCurrentHealthData() {
        try {
            String currentHealthInfo = Utils.getHealthInfo();
            if (currentHealthInfo != null && !currentHealthInfo.isEmpty()) {
                healthDataCache.addToCache(currentHealthInfo);
                HiLog.info(LABEL_LOG, "HealthDataService::cacheCurrentHealthData 健康数据已缓存");
            }
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "HealthDataService::cacheCurrentHealthData 缓存失败: " + e.getMessage());
        }
    }

    // 初始化所有缓存变量，避免定时器中重复计算（省电优化）
    private void initCachedVariables() {
        // 获取支持状态
        stepSupported = dataManager.isSupportStep();
        distanceSupported = dataManager.isSupportDistance();
        calorieSupported = dataManager.isSupportCalorie();
        temperatureSupported = dataManager.isSupportTemperature();
        bloodOxygenSupported = dataManager.isSupportBloodOxygen();
        stressSupported = dataManager.isSupportStress();
        sleepSupported = dataManager.isSupportSleep();
        exerciseDailySupported = dataManager.isSupportExerciseDaily();
        exerciseWeekSupported = dataManager.isSupportExerciseWeek();
        scientificSleepSupported = dataManager.isSupportScientificSleep();
        workoutSupported = dataManager.isSupportWorkout();

        // 获取采集周期（秒转毫秒）
        heartRatePeriod = dataManager.getHeartRateMeasurePeriod() * 1000L;
        stepPeriod = dataManager.getStepsMeasurePeriod() * 1000L;
        distancePeriod = dataManager.getDistanceMeasurePeriod() * 1000L;
        caloriePeriod = dataManager.getCalorieMeasurePeriod() * 1000L;
        temperaturePeriod = dataManager.getBodyTemperatureMeasurePeriod() * 1000L;
        bloodOxygenPeriod = dataManager.getBloodOxygenMeasurePeriod() * 1000L;
        stressPeriod = dataManager.getStressMeasurePeriod() * 1000L;
        sleepPeriod = dataManager.getSleepMeasurePeriod() * 1000L;
        exerciseDailyPeriod = dataManager.getExerciseDailyMeasurePeriod() * 1000L;
        exerciseWeekPeriod = dataManager.getExerciseWeekMeasurePeriod() * 1000L;
        scientificSleepPeriod = dataManager.getScientificSleepMeasurePeriod() * 1000L;
        workoutPeriod = dataManager.getWorkoutMeasurePeriod() * 1000L;

        // 计算定时器间隔（基于basePeriod）
        stepTickInterval = (int)(dataManager.getStepsMeasurePeriod() / basePeriod);
        distanceTickInterval = (int)(dataManager.getDistanceMeasurePeriod() / basePeriod);
        calorieTickInterval = (int)(dataManager.getCalorieMeasurePeriod() / basePeriod);
        temperatureTickInterval = (int)(dataManager.getBodyTemperatureMeasurePeriod() / basePeriod);
        bloodOxygenTickInterval = (int)(dataManager.getBloodOxygenMeasurePeriod() / basePeriod);
        stressTickInterval = (int)(dataManager.getStressMeasurePeriod() / basePeriod);
        sleepTickInterval = (int)(dataManager.getSleepMeasurePeriod() / basePeriod);
        exerciseDailyTickInterval = (int)(dataManager.getExerciseDailyMeasurePeriod() / basePeriod);
        exerciseWeekTickInterval = (int)(dataManager.getExerciseWeekMeasurePeriod() / basePeriod);
        scientificSleepTickInterval = (int)(dataManager.getScientificSleepMeasurePeriod() / basePeriod);
        workoutTickInterval = (int)(dataManager.getWorkoutMeasurePeriod() / basePeriod);

        HiLog.info(LABEL_LOG, "jjgao::initCachedVariables completed - 缓存变量初始化完成");
    }
}