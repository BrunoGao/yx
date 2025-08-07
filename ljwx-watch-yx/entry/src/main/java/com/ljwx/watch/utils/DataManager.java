package com.ljwx.watch.utils;

import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentLinkedQueue;
import org.json.JSONObject; // Added import statement
import java.math.BigDecimal; // Added import statement

import ohos.bluetooth.ble.BlePeripheralDevice;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
public class DataManager {
    private static DataManager instance;

    private double ch4;
    private double o2;
    private double co;
    private double co2;
    private double h2s;
    private int heartRate;
    private int bloodOxygen;
    private double temperature;
    private int step;
    private int pressureHigh;
    private int pressureLow;
    private double distance; // New field for distance
    private double calorie;  // New field for calorie
    private int stress; 
    private BigDecimal latitude;  // Changed type to BigDecimal
    private BigDecimal longitude; // Changed type to BigDecimal
    private BigDecimal altitude; // Changed type to BigDecimal

    boolean isheartRateExceeded = false;
    boolean isScanning = false;
    boolean isConnected = false;
    boolean isGasDataReady = false;
    String deviceName = "";
    private String deviceAddress = "";

    private boolean simpleMode = false;
    private boolean fullMode = true;

    private PropertyChangeSupport support;
    public ConcurrentLinkedQueue<String> dataQueue = new ConcurrentLinkedQueue<>();
    private List<DataChangeListener> listeners = new ArrayList<>();
    private List<String> deviceNames = new ArrayList<>();


    private Map<String, BlePeripheralDevice> deviceList = new HashMap<>();

    private BlePeripheralDevice defaultDevice;

    private String deviceInfo; // Changed type to JSONObject

    private String serialNumber;
    private String defaultDeviceName = "";

    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "nfky");

    private String systemSoftwareVersion;
    private String wifiAddress;
    private String bluetoothAddress;
    private String ipAddress;
    private int networkAccessMode;
    private String imei;
    private String sleepData;

    private int spo2Warning;
    private int stressWarning;
    private int uploadInterval;

    private JSONObject config; // New field for config

    private String uploadCommonEventUrl;

    private boolean isHealthServiceReady;

    // Variables

    private int heartRateWarningCnt;
    private int spo2WarningCnt;
    private int bodyTemperatureWarningCnt;
    private int stressWarningCnt;

    private double bodyTemperatureWarningHigh;
    private double bodyTemperatureWarningLow;
    private int heartRateWarningHigh;
    private int heartRateWarningLow;
    private int spo2WarningHigh;
    private int spo2WarningLow;
    private int stressWarningHigh;
    private int stressWarningLow;

    // New fields for support flags and measure periods
    private boolean supportHeartRate = true;
    private boolean supportBloodOxygen = true;
    private boolean supportTemperature = true;
    private boolean supportStress = false;
    private boolean supportCalorie = false;
    private boolean supportDistance = false;
    private boolean supportEcg = false;
    private boolean supportLocation = false;
    private boolean supportSleep = false;
    private boolean supportSteps = false;
    private boolean supportMessage = false;
    private boolean supportBatteryInfo = false;
    private boolean supportWearInfo = false;

    private long heartRateMeasurePeriod;
    private long bloodOxygenMeasurePeriod;
    private long calorieMeasurePeriod;
    private long distanceMeasurePeriod;
    private long ecgMeasurePeriod;
    private int locationMeasurePeriod;
    private long sleepMeasurePeriod;
    private long stepsMeasurePeriod;
    private long spo2MeasurePeriod;
    private long stressMeasurePeriod;
    private long bodyTemperatureMeasurePeriod;
    private long scientificSleepMeasurePeriod;
    private long exerciseDailyMeasurePeriod;
    private long exerciseWeekMeasurePeriod;
    private long workoutMeasurePeriod;
    private int messageMeasurePeriod;
    private int batteryInfoMeasurePeriod;
    private int wearInfoMeasurePeriod;



    private String customerName;
    private String platformUrl;
    private String uploadMethod;



    private String commonEvent;



    private int licenseCnt;
    private int wearState;

    private String exerciseDailyData;
    private String workoutData;

    private boolean supportScientificSleep;
    private String scientificSleepData;
    private boolean licenseExceeded;
    private boolean supportExerciseDaily;

    private boolean supportExerciseWeek;
    private String exerciseWeekData;
    private boolean supportWear;
    private boolean supportWorkout;



    private int uploadHealthInterval;
    private int uploadDeviceInterval;
    private int fetchMessageInterval;
    private int fetchConfigInterval;
    private int uploadCommonEventInterval;

    private String uploadHealthDataUrl;
    private String uploadDeviceInfoUrl;
    private String fetchMessageUrl;
    private String fetchConfigUrl;
    private String configUrl;
    private int stepHistory;
    private double temperatureHistory;
    private int bloodOxygenHistory;
    private int heartRateHistory;
    private int pressureHighHistory;
    private int pressureLowHistory;

    private boolean supportStep;


    private boolean heartRateIsRealtime;
    private boolean bodyTemperatureIsRealtime;
    private boolean stressIsRealtime;
    private boolean bloodOxygenIsRealtime;

    private boolean isSupportLicense;
    private String appStatus;

    private int licenseKey;
    private String deviceSn;
    private String apiAuthorization;
    private String apiId;

    // 断点上传配置
    private boolean enableResume;
    private int uploadRetryCount;
    private int uploadRetryInterval;
    private int cacheMaxCount;

    // 二进制协议配置
    private boolean useBinaryProtocol = true; // 默认启用二进制协议

    public interface DataChangeListener {
        void onDataChanged();
    }

    public void addDataChangeListener(DataChangeListener listener) {
        listeners.add(listener);
    }

    public void removeDataChangeListener(DataChangeListener listener) {
        listeners.remove(listener);
    }

    protected void notifyDataChange() {
        for (DataChangeListener listener : listeners) {
            listener.onDataChanged();
        }
    }

    private DataManager() {
        support = new PropertyChangeSupport(this);
    }

    public static DataManager getInstance() {
        if (instance == null) {
            instance = new DataManager();
        }
        return instance;
    }

    public void addPropertyChangeListener(PropertyChangeListener pcl) {
        support.addPropertyChangeListener(pcl);
    }

    public void removePropertyChangeListener(PropertyChangeListener pcl) {
        support.removePropertyChangeListener(pcl);
    }

    public boolean getIsheartRateExceeded() {
        return isheartRateExceeded;
    }


    public void setIsheartRateExceeded(boolean isheartRateExceeded) {
        boolean old = this.isheartRateExceeded;
        this.isheartRateExceeded = isheartRateExceeded;
        notifyDataChange();
        support.firePropertyChange("isheartRateExceeded", old, isheartRateExceeded);
    }

    public boolean getScanStatus() {
        return isScanning;
    }


    public void setScanStatus(boolean isScanning) {
        boolean old = this.isScanning;
        this.isScanning = isScanning;
        notifyDataChange();
        support.firePropertyChange("isScanning", old, isScanning);
    }

    public boolean getConnectStatus() {
        return isConnected;
    }


    public void setConnectStatus(boolean isConnected) {
        boolean old = this.isConnected;
        this.isConnected = isConnected;
        notifyDataChange();
        support.firePropertyChange("isConnected", old, isConnected);
    }

    public String getAppStatus() {
        return appStatus;
    }


    public void setAppStatus(String appStatus) {
        String old = this.appStatus;
        this.appStatus = appStatus;
        notifyDataChange();
        support.firePropertyChange("appStatus", old, appStatus);
    }



    public boolean getGasDataReady() {
        return isGasDataReady;
    }


    public void setGasDataReady(boolean isGasDataReady) {
        boolean old = this.isGasDataReady;
        this.isGasDataReady = isGasDataReady;
        notifyDataChange();
        support.firePropertyChange("isGasDataReady", old, isGasDataReady);
    }


    public String getDeviceAddress() {
        return deviceAddress;
    }


    public void setDeviceAddress(String deviceAddress) {
        // String old = this.deviceName;
        //保证设备名字有变动，触发监听

        String old = "old";
        HiLog.info(LABEL_LOG, "setDeviceName: " + deviceAddress);
        this.deviceAddress = deviceAddress;
        support.firePropertyChange("deviceAddress", old, deviceAddress);
        notifyDataChange();

    }
    public boolean getIsHealthServiceReady() {
        return isHealthServiceReady;
    }
    public void setIsHealthServiceReady(boolean isHealthServiceReady) {
        boolean old = this.isHealthServiceReady;
        this.isHealthServiceReady = isHealthServiceReady;
        support.firePropertyChange("isHealthServiceReady", old, isHealthServiceReady);
        notifyDataChange();
    }


    public String getDeviceName() {
        return deviceName;
    }


    public void setDeviceName(String deviceName) {
       // String old = this.deviceName;
        //保证设备名字有变动，发监听器
      
        String old = "old";
        HiLog.info(LABEL_LOG, "setDeviceName: " + deviceName);
        this.deviceName = deviceName;
        support.firePropertyChange("deviceName", old, deviceName);
        notifyDataChange(); 

    }

    public Map getDeviceList() {
        return deviceList;
    }


    public void setDeviceList(Map deviceList) {
        // String old = this.deviceName;
        Map old = this.deviceList;

        this.deviceList = deviceList;
        support.firePropertyChange("deviceList", old, deviceList);
        notifyDataChange();

    }

    public int getHeartRate() {
        return heartRate;
    }

    public void setHeartRate(int heartRate) {
        int old = this.heartRate;
        if (old != heartRate) {
            this.heartRate = heartRate;
            support.firePropertyChange("heartRate", old, heartRate);
        }
    }
    public int getBloodOxygen() {
        return bloodOxygen;
    }
    public void setBloodOxygen(int bloodbloodOxygen) {
        int old = this.bloodOxygen;
        if (old != bloodbloodOxygen) {
            this.bloodOxygen = bloodbloodOxygen;
            support.firePropertyChange("bloodOxygen", old, bloodOxygen);
        }
    }
    public double getTemperature() {
        return temperature;
    }
    public void setTemperature(double temperature) {
        double old = this.temperature;
        if (Double.compare(old, temperature) != 0) {
            this.temperature = temperature;
            support.firePropertyChange("temperature", old, temperature);
        }
    }
    public int getStep() {
        return step;
    }
    public void setStep(int step) {
        int old = this.step;
        if (old != step) {
            this.step = step;
            support.firePropertyChange("step", old, step);
        }
    }
    public int getPressureHigh() {
        return pressureHigh;
    }
    public void setPressureHigh(int pressureHigh) {
        int old = this.pressureHigh;
        if (old != pressureHigh) {
            this.pressureHigh = pressureHigh;
            support.firePropertyChange("pressureHigh", old, pressureHigh);
        }
    }
    public int getPressureLow() {
        return pressureLow;
    }
    public void setPressureLow(int pressureLow) {
        int old = this.pressureLow;
        if (old != pressureLow) {
            this.pressureLow = pressureLow;
            support.firePropertyChange("pressureLow", old, pressureLow);
        }
    }
    public double getCh4() {
        return ch4;
    }

    public void setCh4(double ch4) {
        double old = this.ch4;
        if (Double.compare(old, ch4) != 0) {
            this.ch4 = ch4;
            support.firePropertyChange("ch4", old, ch4);
        }
    }

    public double getO2() {
        return o2;
    }

    public void setO2(double o2) {
        double old = this.o2;
        if (Double.compare(old, o2) != 0) {
            this.o2 = o2;
            support.firePropertyChange("o2", old, o2);
        }
    }
    public double getCo() {
        return co;
    }

    public void setCo(double co) {
        double old = this.co;
        if (Double.compare(old, co) != 0) {
            this.co = co;
            support.firePropertyChange("co", old, co);
        }
    }
    public double getCo2() {
        return co2;
    }

    public void setCo2(double co2) {
        double old = this.co2;
        if (Double.compare(old, co2) != 0) {
            this.co2 = co2;
            support.firePropertyChange("co2", old, co2);
        }
    }
    public double getH2s() {
        return h2s;
    }

    public void setH2s(double h2s) {
        double old = this.h2s;
        if (Double.compare(old, h2s) != 0) {
            this.h2s = h2s;
            support.firePropertyChange("h2s", old, h2s);
        }
    }

    public double getDistance() {
        return distance;
    }

    public void setDistance(double distance) {
        double old = this.distance;
        if (Double.compare(old, distance) != 0) {
            this.distance = distance;
            support.firePropertyChange("distance", old, distance);
            notifyDataChange();
        }
    }

    public double getCalorie() {
        return calorie;
    }

    public void setCalorie(double calorie) {
        double old = this.calorie;
        if (Double.compare(old, calorie) != 0) {
            this.calorie = calorie;
            support.firePropertyChange("calorie", old, calorie);
            notifyDataChange();
        }
    }

    public void setDeviceNames(List<String> names) {
        List old = this.deviceNames;
        this.deviceNames = names;
        support.firePropertyChange("deviceNames", old, names);
        notifyDataChange();
    }

    public List<String> getDeviceNames() {
        return this.deviceNames;
    }

    public boolean isSimpleMode() {
        return simpleMode;
    }

    public void setSimpleMode(boolean simpleMode) {
        boolean old = this.simpleMode;
        this.simpleMode = simpleMode;
        support.firePropertyChange("simpleMode", old, simpleMode);
        notifyDataChange();
    }

    public boolean isFullMode() {
        return fullMode;
    }

    public void setFullMode(boolean fullMode) {
        boolean old = this.fullMode;
        this.fullMode = fullMode;
        support.firePropertyChange("fullMode", old, fullMode);
        notifyDataChange();
    }

    public BlePeripheralDevice getDefaultDevice() {
        return defaultDevice;
    }

    public void setDefaultDevice(BlePeripheralDevice defaultDevice) {
        BlePeripheralDevice old = this.defaultDevice;
        this.defaultDevice = defaultDevice;
        support.firePropertyChange("defaultDevice", old, defaultDevice);
        notifyDataChange();
    }

    public String getDefaultDeviceName() {
        return defaultDeviceName;
    }

    public void setDefaultDeviceName(String defaultDeviceName) {
        String old = this.defaultDeviceName;
        this.defaultDeviceName = defaultDeviceName;
        support.firePropertyChange("defaultDeviceName", old, defaultDeviceName);
        notifyDataChange();
    }

    public String getSerialNumber() {
        return serialNumber;
    }

    public void setSerialNumber(String serialNumber) {
        String old = this.serialNumber;
        this.serialNumber = serialNumber;
        support.firePropertyChange("serialNumber", old, serialNumber);
        notifyDataChange();
    }

    public String getDeviceInfo() {
        return deviceInfo;
    }

    public void setDeviceInfo(String deviceInfo) {
        String old = this.deviceInfo;
        this.deviceInfo = deviceInfo;
        support.firePropertyChange("deviceInfo", old, deviceInfo);
        notifyDataChange();
    }

    public String getSystemSoftwareVersion() {
        return systemSoftwareVersion;
    }

    public void setSystemSoftwareVersion(String systemSoftwareVersion) {
        String old = this.systemSoftwareVersion;
        this.systemSoftwareVersion = systemSoftwareVersion;
        support.firePropertyChange("systemSoftwareVersion", old, systemSoftwareVersion);
        notifyDataChange();
    }

    public String getWifiAddress() {
        return wifiAddress;
    }

    public void setWifiAddress(String wifiAddress) {
        String old = this.wifiAddress;
        this.wifiAddress = wifiAddress;
        support.firePropertyChange("wifiAddress", old, wifiAddress);
        notifyDataChange();
    }

    public String getBluetoothAddress() {
        return bluetoothAddress;
    }

    public void setBluetoothAddress(String bluetoothAddress) {
        String old = this.bluetoothAddress;
        this.bluetoothAddress = bluetoothAddress;
        support.firePropertyChange("bluetoothAddress", old, bluetoothAddress);
        notifyDataChange();
    }

    public String getIpAddress() {
        return ipAddress;
    }

    public void setIpAddress(String ipAddress) {
        String old = this.ipAddress;
        this.ipAddress = ipAddress;
        support.firePropertyChange("ipAddress", old, ipAddress);
        notifyDataChange();
    }

    public int getNetworkAccessMode() {
        return networkAccessMode;
    }

    public void setNetworkAccessMode(int networkAccessMode) {
        int old = this.networkAccessMode;
        this.networkAccessMode = networkAccessMode;
        support.firePropertyChange("networkAccessMode", old, networkAccessMode);
        notifyDataChange();
    }


    public String getImei() {
        return imei;
    }

    public void setImei(String imei) {
        String old = this.imei;
        this.imei = imei;
        support.firePropertyChange("imei", old, imei);
        notifyDataChange();
    }
    public int getStress() {
        return stress;
    }

    public void setStress(int stress) {
        int old = this.stress;
        if (old != stress) {
            this.stress = stress;
            support.firePropertyChange("stress", old, stress);
            notifyDataChange();
        }
    }

    public void setSpo2MeasurePeriod(long period) {
        this.spo2MeasurePeriod = period;
    }

    public long getSpo2MeasurePeriod() {
        return spo2MeasurePeriod;
    }



    public int getSpo2Warning() {
        return spo2Warning;
    }

    public void setStressWarning(int warning) {
        this.stressWarning = warning;
    }

    public int getStressWarning() {
        return stressWarning;
    }

    

    public void setCustomerName(String customerName) {
        String old = this.customerName;
        this.customerName = customerName;
        support.firePropertyChange("customerName", old, customerName);
        notifyDataChange();
    }

    public BigDecimal getLatitude() {
        return latitude;
    }

    public void setLatitude(BigDecimal latitude) {
        BigDecimal old = this.latitude;
        if (old == null || old != latitude) {
            this.latitude = latitude;
            support.firePropertyChange("latitude", old, latitude);
            notifyDataChange();
        }
    }

    public BigDecimal getLongitude() {
        return longitude;
    }

    public void setLongitude(BigDecimal longitude) {
        BigDecimal old = this.longitude;
        if (old == null || old != longitude) {
            this.longitude = longitude;
            support.firePropertyChange("longitude", old, longitude);
            notifyDataChange();
        }
    }

    public JSONObject getConfig() {
        return config;
    }

    public void setConfig(JSONObject config) {
        JSONObject old = this.config;
        this.config = config;
        support.firePropertyChange("config", old, config);
        notifyDataChange();
    }

    public boolean getIsSupportLicense() {
        return isSupportLicense;
    }

    public void setIsSupportLicense(boolean isSupportLicense) {
        this.isSupportLicense = isSupportLicense;
    }

    public int getLicenseKey() {
        return licenseKey;
    }

    public void setLicenseKey(int licenseKey) {      
        this.licenseKey = licenseKey;
    }

    public void setHeartRateMeasurePeriod(long heartRateMeasurePeriod) {
        this.heartRateMeasurePeriod = heartRateMeasurePeriod;
    }

    // Getter and Setter methods for support flags




    public void setSupportBloodOxygen(boolean supportBloodOxygen) {
        this.supportBloodOxygen = supportBloodOxygen;
    }

    

    public void setSupportTemperature(boolean supportTemperature) {
        this.supportTemperature = supportTemperature;
    }


    public void setSupportStress(boolean supportStress) {
        this.supportStress = supportStress;
    }

    public boolean isSupportCalorie() {
        return supportCalorie;
    }

    public void setSupportCalorie(boolean supportCalorie) {
        this.supportCalorie = supportCalorie;
    }

    public boolean isSupportDistance() {
        return supportDistance;
    }

    public void setSupportDistance(boolean supportDistance) {
        this.supportDistance = supportDistance;
    }

    public boolean isSupportEcg() {
        return supportEcg;
    }

    public void setSupportEcg(boolean supportEcg) {
        this.supportEcg = supportEcg;
    }

    public BigDecimal getAltitude() {
        return altitude;
    }

    public void setAltitude(BigDecimal altitude) {
        this.altitude = altitude;
    }

    public boolean isSupportLocation() {
        return supportLocation;
    }

    public void setSupportLocation(boolean supportLocation) {
        boolean old = this.supportLocation;
        if (old != supportLocation) {
            this.supportLocation = supportLocation;
            support.firePropertyChange("supportLocation", old, supportLocation);
            notifyDataChange();
        }
    }

    public boolean isSupportSleep() {
        return supportSleep;
    }

    public void setSupportSleep(boolean supportSleep) {
        this.supportSleep = supportSleep;
    }


    // Getter and Setter methods for measure periods
    public long getBloodOxygenMeasurePeriod() {
        return bloodOxygenMeasurePeriod;
    }


    public long getCalorieMeasurePeriod() {
        return calorieMeasurePeriod;
    }

    public void setCalorieMeasurePeriod(long calorieMeasurePeriod) {
        this.calorieMeasurePeriod = calorieMeasurePeriod;
    }

    public long getDistanceMeasurePeriod() {
        return distanceMeasurePeriod;
    }

    public void setDistanceMeasurePeriod(long distanceMeasurePeriod) {
        this.distanceMeasurePeriod = distanceMeasurePeriod;
    }

    public long getEcgMeasurePeriod() {
        return ecgMeasurePeriod;
    }

    public void setEcgMeasurePeriod(long ecgMeasurePeriod) {
        this.ecgMeasurePeriod = ecgMeasurePeriod;
    }

    public int getLocationMeasurePeriod() {
        return locationMeasurePeriod;
    }

    public void setLocationMeasurePeriod(int locationMeasurePeriod) {
        this.locationMeasurePeriod = locationMeasurePeriod;
    }

    public long getSleepMeasurePeriod() {
        return sleepMeasurePeriod;
    }

    public void setSleepMeasurePeriod(long sleepMeasurePeriod) {
        this.sleepMeasurePeriod = sleepMeasurePeriod;
    }

    public long getStepsMeasurePeriod() {
        return stepsMeasurePeriod;
    }

    public void setStepsMeasurePeriod(long stepsMeasurePeriod) {
        this.stepsMeasurePeriod = stepsMeasurePeriod;
    }

    public String getCustomerName() {
        return customerName;
    }

    public String getPlatformUrl() {
        return platformUrl;
    }

    public String getUploadMethod() {
        return uploadMethod;
    }


    public void setPlatformUrl(String platformUrl) {
        this.platformUrl = platformUrl;
    }

    public void setUploadMethod(String uploadMethod) {
        String old = this.uploadMethod;
        this.uploadMethod = uploadMethod;
        support.firePropertyChange("uploadMethod", old, uploadMethod);
        notifyDataChange();
    }

    public void setSupportMessage(boolean supportMessage) {
        this.supportMessage = supportMessage;
    }

    public void setMessageMeasurePeriod(int messageMeasurePeriod) {
        this.messageMeasurePeriod = messageMeasurePeriod;
    }

    public void setSupportBatteryInfo(boolean supportBatteryInfo) {
        this.supportBatteryInfo = supportBatteryInfo;
    }

    public void setBatteryInfoMeasurePeriod(int batteryInfoMeasurePeriod) {
        this.batteryInfoMeasurePeriod = batteryInfoMeasurePeriod;
    }

    public void setSupportWearInfo(boolean supportWearInfo) {
        this.supportWearInfo = supportWearInfo;
    }

    public void setWearInfoMeasurePeriod(int wearInfoMeasurePeriod) {
        this.wearInfoMeasurePeriod = wearInfoMeasurePeriod;
    }

    public boolean isSupportMessage() {
        return supportMessage;
    }

    public int getMessageMeasurePeriod() {
        return messageMeasurePeriod;
    }

    public boolean isSupportBatteryInfo() {
        return supportBatteryInfo;
    }

    public int getBatteryInfoMeasurePeriod() {
        return batteryInfoMeasurePeriod;
    }

    public boolean isSupportWearInfo() {
        return supportWearInfo;
    }

    public int getWearInfoMeasurePeriod() {
        return wearInfoMeasurePeriod;
    }

    public String getSleepData() {
        return sleepData;
    }

    public void setSleepData(String sleepData) {
        this.sleepData = sleepData;
    }

    public int getWearState() {
        return wearState;
    }

    public void setWearState(int wearState) {
        int old = this.wearState;
        this.wearState = wearState;
        support.firePropertyChange("wearState", old, wearState);
        notifyDataChange();
    }

    public String getExerciseDailyData() {
        return exerciseDailyData;
    }

    public void setExerciseDailyData(String exerciseDailyData) {
        this.exerciseDailyData = exerciseDailyData;
    }

    // Getters and Setters for Heart Rate
    public boolean isSupportHeartRate() {
        return supportHeartRate;
    }

    public void setSupportHeartRate(boolean supportHeartRate) {
        this.supportHeartRate = supportHeartRate;
    }

    public long getHeartRateMeasurePeriod() {
        return heartRateMeasurePeriod;
    }

    public void setHeartRateMeasurePeriod(int heartRateMeasurePeriod) {
        this.heartRateMeasurePeriod = heartRateMeasurePeriod;
    }

    public int getHeartRateWarningHigh() {
        return heartRateWarningHigh;
    }
    public String getDeviceSn() {
        return deviceSn;
    }
    public void setDeviceSn(String deviceSn) {
        this.deviceSn = deviceSn;
    }

    public void setHeartRateWarningHigh(int heartRateWarningHigh) {
        this.heartRateWarningHigh = heartRateWarningHigh;
    }

    public int getHeartRateWarningLow() {
        return heartRateWarningLow; 
    }

    public void setHeartRateWarningLow(int heartRateWarningLow) {
        this.heartRateWarningLow = heartRateWarningLow;
    }

    public int getHeartRateWarningCnt() {
        return heartRateWarningCnt;
    }

    public void setHeartRateWarningCnt(int heartRateWarningCnt) {
        this.heartRateWarningCnt = heartRateWarningCnt;
    }

    // Getters and Setter methods for Temperature
    public boolean isSupportTemperature() {
        return supportTemperature;
    }


    public long getBodyTemperatureMeasurePeriod() {
        return bodyTemperatureMeasurePeriod;
    }

    public void setBodyTemperatureMeasurePeriod(long bodyTemperatureMeasurePeriod) {
        this.bodyTemperatureMeasurePeriod = bodyTemperatureMeasurePeriod;
    }

    public double getBodyTemperatureWarningHigh() {
        return bodyTemperatureWarningHigh;
    }

    public void setBodyTemperatureWarningHigh(double bodyTemperatureWarningHigh) {
        this.bodyTemperatureWarningHigh = bodyTemperatureWarningHigh;
    }

    public double getBodyTemperatureWarningLow() {
        return bodyTemperatureWarningLow;
    }

    public void setBodyTemperatureWarningLow(double bodyTemperatureWarningLow) {
        this.bodyTemperatureWarningLow = bodyTemperatureWarningLow;
    }

    public int getBodyTemperatureWarningCnt() {
        return bodyTemperatureWarningCnt;
    }

    public void setBodyTemperatureWarningCnt(int bodyTemperatureWarningCnt) {
        this.bodyTemperatureWarningCnt = bodyTemperatureWarningCnt;
    }

    // Getters and Setter methods for Stress
    public boolean isSupportStress() {
        return supportStress;
    }


    public long getStressMeasurePeriod() {
        return stressMeasurePeriod;
    }

    public void setStressMeasurePeriod(long stressMeasurePeriod) {
        this.stressMeasurePeriod = stressMeasurePeriod;
    }

    public long getScientificSleepMeasurePeriod() {
        return scientificSleepMeasurePeriod;
    }

    public void setScientificSleepMeasurePeriod(long scientificSleepMeasurePeriod) {
        this.scientificSleepMeasurePeriod = scientificSleepMeasurePeriod;
    }

    public long getExerciseDailyMeasurePeriod() {
        return exerciseDailyMeasurePeriod;
    }

    public void setExerciseDailyMeasurePeriod(long exerciseDailyMeasurePeriod) {
        this.exerciseDailyMeasurePeriod = exerciseDailyMeasurePeriod;
    }

    public long getExerciseWeekMeasurePeriod() {
        return exerciseWeekMeasurePeriod;
    }

    public void setExerciseWeekMeasurePeriod(long exerciseWeekMeasurePeriod) {
        this.exerciseWeekMeasurePeriod = exerciseWeekMeasurePeriod;
    }

    public long getWorkoutMeasurePeriod() {
        return workoutMeasurePeriod;
    }

    public void setWorkoutMeasurePeriod(long workoutMeasurePeriod) {
        this.workoutMeasurePeriod = workoutMeasurePeriod;
    }
    
    public int getStressWarningHigh() {
        return stressWarningHigh;
    }

    public void setStressWarningHigh(int stressWarningHigh) {
        this.stressWarningHigh = stressWarningHigh;
    }

    public int getStressWarningLow() {
        return stressWarningLow;
    }

    public void setStressWarningLow(int stressWarningLow) {
        this.stressWarningLow = stressWarningLow;
    }

    public int getStressWarningCnt() {
        return stressWarningCnt;
    }

    public void setStressWarningCnt(int stressWarningCnt) {
        this.stressWarningCnt = stressWarningCnt;
    }

    // Getters and Setter methods for Blood Oxygen
    public boolean isSupportBloodOxygen() {
        return supportBloodOxygen;
    }


    public void setBloodOxygenMeasurePeriod(long bloodOxygenMeasurePeriod) {
        this.bloodOxygenMeasurePeriod = bloodOxygenMeasurePeriod;
    }

    public int getSpo2WarningHigh() {
        return spo2WarningHigh;
    }

    public int getSpo2WarningLow() {
        return spo2WarningLow;
    }

    public void setSpo2Warning(int spo2WarningLow) {
        this.spo2Warning = spo2WarningLow;
    }


    public int getSpo2WarningCnt() {
        return spo2WarningCnt;
    }

    public void setSpo2WarningCnt(int spo2WarningCnt) {
        this.spo2WarningCnt = spo2WarningCnt;
    }

    public int getLicenseCnt() {
        return licenseCnt;
    }

    public void setLicenseCnt(int licenseCnt) {
        this.licenseCnt = licenseCnt;
    }

    public boolean isLicenseExceeded() {
        return licenseExceeded;
    }

    public void setLicenseExceeded(boolean licenseExceeded) {
        boolean old = this.licenseExceeded;
        this.licenseExceeded = licenseExceeded;
        support.firePropertyChange("licenseExceeded", old, licenseExceeded);
        notifyDataChange();
    }

    public boolean isSupportWear() {
        return supportWear;
    }

    public void setSupportWear(boolean supportWear) {
        this.supportWear = supportWear;
    }

    public boolean isSupportWorkout() {
        return supportWorkout;
    }

    public void setSupportWorkout(boolean supportWorkout) {
        this.supportWorkout = supportWorkout;
    }

    public boolean isSupportExerciseDaily() {
        return supportExerciseDaily;
    }

    public void setSupportExerciseDaily(boolean supportExerciseDaily) {
        this.supportExerciseDaily = supportExerciseDaily;
    }

    public boolean isSupportExerciseWeek() {
        return supportExerciseWeek;
    }

    public void setSupportExerciseWeek(boolean supportExerciseWeek) {
        this.supportExerciseWeek = supportExerciseWeek;
    }

    public boolean isSupportScientificSleep() {
        return supportScientificSleep;
    }

    public void setSupportScientificSleep(boolean supportScientificSleep) {
        this.supportScientificSleep = supportScientificSleep;
    }

    public int getUploadInterval() {
        return uploadInterval;
    }

    public void setUploadInterval(int uploadInterval) {
        this.uploadInterval = uploadInterval;
    }

    public int getUploadHealthInterval() {
        return uploadHealthInterval;
    }

    public void setUploadHealthInterval(int uploadHealthInterval) {
        int old = this.uploadHealthInterval;
        this.uploadHealthInterval = uploadHealthInterval;
        support.firePropertyChange("uploadHealthInterval", old, uploadHealthInterval);
        notifyDataChange();
    }

    public String getUploadHealthDataUrl() {
        return uploadHealthDataUrl;
    }

    public void setUploadHealthDataUrl(String uploadHealthDataUrl) {
        this.uploadHealthDataUrl = uploadHealthDataUrl;
    }
    public int getUploadDeviceInterval() {
        return uploadDeviceInterval;
    }

    public void setUploadDeviceInterval(int uploadDeviceInterval) {
        this.uploadDeviceInterval = uploadDeviceInterval;
    }

    public String getUploadDeviceInfoUrl() {
        return uploadDeviceInfoUrl;
    }

    public void setUploadDeviceInfoUrl(String uploadDeviceInfoUrl) {
        this.uploadDeviceInfoUrl = uploadDeviceInfoUrl;
    }

    public String getApiAuthorization() {
        return apiAuthorization;
    }

    public void setApiAuthorization(String apiAuthorization) {
        this.apiAuthorization = apiAuthorization;
    }

    public String getApiId() {
        return apiId;
    }

    public void setApiId(String apiId) {
        this.apiId = apiId;
    }
    

    public int getFetchMessageInterval() {
        return fetchMessageInterval;
    }

    public void setFetchMessageInterval(int fetchMessageInterval) {
        this.fetchMessageInterval = fetchMessageInterval;
    }

    public String getFetchMessageUrl() {
        return fetchMessageUrl;
    }

    public void setFetchMessageUrl(String fetchMessageUrl) {
        this.fetchMessageUrl = fetchMessageUrl;
    }


    public String getFetchConfigUrl() {
        return fetchConfigUrl;
    }

    public void setFetchConfigUrl(String fetchConfigUrl) {
        this.fetchConfigUrl = fetchConfigUrl;
    }
    
    



    public String getWorkoutData() {
        return workoutData;
    }

    public void setWorkoutData(String workoutData) {
        this.workoutData = workoutData;
    }


    public String getExerciseWeekData() {
        return exerciseWeekData;
    }

    public void setExerciseWeekData(String exerciseWeekData) {
        this.exerciseWeekData = exerciseWeekData;
    }

    public String getScientificSleepData() {
        return scientificSleepData;
    }

    public void setScientificSleepData(String scientificSleepData) {
        this.scientificSleepData = scientificSleepData;
    }

    public int getStepHistory() {
        return stepHistory;
    }

    public void setStepHistory(int stepHistory) {
        this.stepHistory = stepHistory;
    }

    public double getTemperatureHistory() {
        return temperatureHistory;
    }

    public void setTemperatureHistory(double temperatureHistory) {
        this.temperatureHistory = temperatureHistory;
    }

    public int getBloodOxygenHistory() {
        return bloodOxygenHistory;
    }

    public void setBloodOxygenHistory(int bloodOxygenHistory) {
        this.bloodOxygenHistory = bloodOxygenHistory;
    }

    public int getHeartRateHistory() {
        return heartRateHistory;
    }

    public void setHeartRateHistory(int heartRateHistory) {
        this.heartRateHistory = heartRateHistory;
    }

    public int getPressureHighHistory() {
        return pressureHighHistory;
    }

    public void setPressureHighHistory(int pressureHighHistory) {
        this.pressureHighHistory = pressureHighHistory;
    }

    public int getPressureLowHistory() {
        return pressureLowHistory;
    }

    public void setPressureLowHistory(int pressureLowHistory) {
        this.pressureLowHistory = pressureLowHistory;
    }

    public boolean isSupportStep() {
        return supportStep;
    }

    public void setSupportStep(boolean supportStep) {
        this.supportStep = supportStep;
    }

    public boolean isHeartRateIsRealtime() {
        return heartRateIsRealtime;
    }

    public void setHeartRateIsRealtime(boolean heartRateIsRealtime) {
        this.heartRateIsRealtime = heartRateIsRealtime;
    }

    public boolean isBodyTemperatureIsRealtime() {
        return bodyTemperatureIsRealtime;
    }

    public void setBodyTemperatureIsRealtime(boolean bodyTemperatureIsRealtime) {
        this.bodyTemperatureIsRealtime = bodyTemperatureIsRealtime;
    }

    public boolean isStressIsRealtime() {
        return stressIsRealtime;
    }

    public void setStressIsRealtime(boolean stressIsRealtime) {
        this.stressIsRealtime = stressIsRealtime;
    }

    public boolean isBloodOxygenIsRealtime() {
        return bloodOxygenIsRealtime;
    }

    public void setBloodOxygenIsRealtime(boolean bloodOxygenIsRealtime) {
        this.bloodOxygenIsRealtime = bloodOxygenIsRealtime;
    }

    public void setUploadCommonEventUrl(String uploadCommonEventUrl) {
        String old = this.uploadCommonEventUrl;
        this.uploadCommonEventUrl = uploadCommonEventUrl;
        support.firePropertyChange("uploadCommonEventUrl", old, uploadCommonEventUrl);
        notifyDataChange();
    }

    public String getUploadCommonEventUrl() {
        return uploadCommonEventUrl;
    }

    public void setUploadCommonEventInterval(int uploadCommonEventInterval) {
        this.uploadCommonEventInterval = uploadCommonEventInterval;
    }

    public int getUploadCommonEventInterval() {
        return uploadCommonEventInterval;
    }

    public void setCommonEvent(String commonEvent) {
        String old = this.commonEvent;
        this.commonEvent = commonEvent;
        support.firePropertyChange("commonEvent", old, commonEvent);
        notifyDataChange();
    }

    public String getCommonEvent() {
        return commonEvent;
    }

    public int getFetchConfigInterval() {
        return fetchConfigInterval;
    }

    public void setFetchConfigInterval(int fetchConfigInterval) {
        this.fetchConfigInterval = fetchConfigInterval;
    }

    public void setConfigUrl(String configUrl) {
        this.configUrl = configUrl;
    }

    public String getConfigUrl() {
        return configUrl;
    }

    public boolean isEnableResume() {
        return enableResume;
    }

    public void setEnableResume(boolean enableResume) {
        boolean old = this.enableResume;
        this.enableResume = enableResume;
        support.firePropertyChange("enableResume", old, enableResume);
        notifyDataChange();
    }

    public int getUploadRetryCount() {
        return uploadRetryCount;
    }

    public void setUploadRetryCount(int uploadRetryCount) {
        this.uploadRetryCount = uploadRetryCount;
    }

    public int getUploadRetryInterval() {
        return uploadRetryInterval;
    }

    public void setUploadRetryInterval(int uploadRetryInterval) {
        this.uploadRetryInterval = uploadRetryInterval;
    }

    public int getCacheMaxCount() {
        return cacheMaxCount;
    }

    public void setCacheMaxCount(int cacheMaxCount) {
        this.cacheMaxCount = cacheMaxCount;
    }

    // 二进制协议配置方法
    public boolean getUseBinaryProtocol() {
        return useBinaryProtocol;
    }

    public void setUseBinaryProtocol(boolean useBinaryProtocol) {
        this.useBinaryProtocol = useBinaryProtocol;
    }

}
