package com.hg.watch;
import com.tdtech.ohos.mdm.DeviceManager;
import com.hg.watch.utils.Utils;
import com.hg.watch.utils.JsonUtil;
import com.hg.watch.utils.BleProtocolEncoder;
import com.hg.watch.utils.BleProtocolDecoder;
import ohos.aafwk.ability.Ability;
import ohos.aafwk.content.Intent;
import ohos.app.Context;

import ohos.data.DatabaseHelper;
import ohos.data.preferences.Preferences;
import ohos.event.notification.NotificationHelper;
import ohos.event.notification.NotificationRequest;
import ohos.rpc.IRemoteObject;
import ohos.hiviewdfx.HiLog;
import ohos.hiviewdfx.HiLogLabel;
import ohos.bluetooth.ble.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import com.hg.watch.utils.DataManager;

import ohos.utils.SequenceUuid;
import ohos.rpc.RemoteException;
import org.json.JSONObject;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;
import java.text.SimpleDateFormat;
import java.util.Date;

public class BluetoothService extends Ability implements BleConstants {
    private static final HiLogLabel LABEL_LOG = new HiLogLabel(3, 0xD001100, "ljwx-log");

    // UUID常量
    private static final UUID SERVICE_UUID = UUID.fromString("00001887-0000-1000-8000-00805f9b34fb");
    private static final UUID DATA_CHAR_UUID = UUID.fromString("0000FD10-0000-1000-8000-00805F9B34FB");
    private static final UUID CMD_CHAR_UUID = UUID.fromString("0000FD11-0000-1000-8000-00805F9B34FB");
    private static final UUID CCCD_UUID = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");

    // GATT 服务变更相关常量
    private static final UUID GENERIC_ATTRIBUTE_SERVICE_UUID = UUID.fromString("00001801-0000-1000-8000-00805f9b34fb");
    private static final UUID SERVICE_CHANGED_CHAR_UUID = UUID.fromString("00002A05-0000-1000-8000-00805f9b34fb");

    // 权限和属性常量
    private static final int GATT_PERM = 16;
    private static final int PROP_NOTIFY = 0x10;
    private static final int PROP_INDICATE = 0x20;
    private static final int MAX_RETRIES = 3;
    private static final long RETRY_DELAY_MS = 100;

    // 数据类型常量
    private static final String TYPE_HEALTH = "health";
    private static final String TYPE_DEVICE = "device";
    private static final String TYPE_COMMON_EVENT = "commonEvent";
    private static final String TYPE_MESSAGE_RESPONSE = "message_response";
    private static final String TYPE_PROBE_RESPONSE = "probe_response";

    // 命令类型常量
    private static final String CMD_MESSAGE = "message";
    private static final String CMD_CONFIG = "config";
    private static final String CMD_DISCONNECT = "disconnect";
    private static final String CMD_MTU = "mtu";
    private static final String CMD_PROTOCOL_PROBE = "protocol_probe";
    private static final String CMD_HEALTH_DATA_ACK = "health_data_ack";

    private BlePeripheralDevice peripheralDevice = null;
    private boolean isConnected = false;
    private boolean isAdvertising = false;
    private DataManager dataManager = DataManager.getInstance();
    private DeviceManager deviceManager = null;
    private static int notificationId = 3000;

    // 线程池相关
    private ScheduledExecutorService scheduler;
    private ExecutorService pushExecutor;
    private BlockingQueue<ChunkData> pushQueue;
    private ScheduledFuture<?> healthTask;
    private ScheduledFuture<?> deviceTask;

    // MTU相关
    private int mtu = DEFAULT_MTU;
    private GattCharacteristic serviceChangeChar = null;

    private static final Map<String, String> MESSAGE_TYPE_MAP = new HashMap<>();
    static {
        MESSAGE_TYPE_MAP.put("announcement", "公告");
        MESSAGE_TYPE_MAP.put("notification", "个人通知");
        MESSAGE_TYPE_MAP.put("warning", "告警");
        MESSAGE_TYPE_MAP.put("job", "作业指引");
        MESSAGE_TYPE_MAP.put("task", "任务管理");
    }

    private volatile boolean isServiceRunning = false; // 服务运行状态标志
    private final Object restartLock = new Object(); // 同步锁防止并发重启
    private static final Object GLOBAL_BLE_LOCK = new Object(); // 全局BLE操作锁
    private static int serviceInstanceCount = 0; // 服务实例计数
    private final Set<String> sentPacketIds = Collections.synchronizedSet(new HashSet<>()); // 已发送数据包ID集合
    private final String deviceBroadcastId = UUID.randomUUID().toString().substring(0, 8); // 设备唯一广播ID

    // 其他必要的字段
    private BlePeripheralManagerCallback peripheralManagerCallback = null;
    private BlePeripheralManager blePeripheralManager;
    private GattCharacteristic dataChar;
    private GattCharacteristic cmdChar;
    private BleAdvertiseData advertiseData;
    private BleAdvertiseSettings advertiseSettings;
    private MyBleAdvertiseCallback advertiseCallback = new MyBleAdvertiseCallback();
    private BleAdvertiser advertiser;

    // 添加事件队列保存未能立即发送的事件
    private final Queue<String> pendingCommonEvents = new ConcurrentLinkedQueue<>();
    private ScheduledFuture<?> eventRetryTask = null;

    private static String lastHealthInfo;
    private static String lastDeviceInfo;
    private static String lastBTHealthInfo;
    private static String lastBTDeviceInfo;
    private static long lastHealthUpdateTime;
    private static long lastDeviceUpdateTime;
    private static final long HEALTH_CACHE_DURATION = 5000; // 5秒缓存
    private static final long DEVICE_CACHE_DURATION = 60000; // 1分钟缓存

    // 添加协议编码器实例
    private BleProtocolDecoder protocolDecoder = new BleProtocolDecoder();
    
    // 添加初始设备信息发送控制
    private volatile long lastInitialDeviceDataTime = 0; // 最后一次初始设备信息发送时间
    private static final long INITIAL_DEVICE_DATA_INTERVAL = 30000; // 30秒间隔避免重复发送

    // 添加发送流量控制变量
    private volatile boolean isWriting = false; // 标记是否正在写入
    private final Object writeLock = new Object(); // 写入同步锁
    private volatile long lastWriteTime = 0; // 最后一次写入时间
    private static final long MIN_WRITE_INTERVAL = 20; // 最小写入间隔(毫秒)

    // 添加推送循环状态控制变量，防止多次notify启用导致重复推送
    private volatile boolean isPushLoopRunning = false; // 推送循环运行状态
    private final Object pushLoopLock = new Object(); // 推送循环控制锁
    private volatile long lastNotifyEnableTime = 0; // 最后一次启用notify的时间
    private static final long MIN_NOTIFY_ENABLE_INTERVAL = 5000; // 最小notify启用间隔5秒

    // 添加描述符写入状态控制变量
    private volatile long lastDescriptorWriteTime = 0; // 最后一次描述符写入时间
    private static final long MIN_DESCRIPTOR_WRITE_INTERVAL = 1000; // 最小描述符写入间隔1秒
    private final Set<String> processedDescriptorWrites = Collections.synchronizedSet(new HashSet<>()); // 已处理的描述符写入请求

    // 修改ChunkData类以支持二进制数据
    private static class ChunkData {
        final String messageId;
        final int totalChunks;
        final int index;
        final byte[] data; // 改为byte[]支持二进制数据
        final boolean isBinary; // 标识是否为二进制数据

        ChunkData(String messageId, int totalChunks, int index, byte[] data, boolean isBinary) {
            this.messageId = messageId;
            this.totalChunks = totalChunks;
            this.index = index;
            this.data = data;
            this.isBinary = isBinary;
        }
        
        // 兼容旧的字符串构造函数
        ChunkData(String messageId, int totalChunks, int index, String chunk) {
            this.messageId = messageId;
            this.totalChunks = totalChunks;
            this.index = index;
            this.data = chunk.getBytes(StandardCharsets.UTF_8);
            this.isBinary = false;
        }
    }

    public BluetoothService() {
        dataManager.addPropertyChangeListener(evt -> {
            if ("deviceName".equals(evt.getPropertyName())) {
                HiLog.info(LABEL_LOG, "bluetooth::begin to connect to:" + evt.getNewValue());
            } else if("commonEvent".equals(evt.getPropertyName())) {
                String commonEvent = dataManager.getCommonEvent();
                HiLog.info(LABEL_LOG, "BluetoothService::onPropertyChange commonEvent: " + commonEvent);
                pushCommonEvent(commonEvent);
            }else if("isHealthServiceReady".equals(evt.getPropertyName())){
                HiLog.info(LABEL_LOG, "BluetoothService::onPropertyChange isHealthServiceReady: " + evt.getNewValue());  
            }
        });
        
        // 主动检查健康服务状态，防止错过初始化事件
        boolean currentHealthStatus = dataManager.getIsHealthServiceReady();
        HiLog.info(LABEL_LOG, "BluetoothService::构造函数::当前健康服务状态: " + currentHealthStatus);

        // 设置全局异常处理器
        Thread.setDefaultUncaughtExceptionHandler((thread, throwable) -> {
            HiLog.error(LABEL_LOG, "Uncaught exception in thread " + thread.getName() + ": " + throwable.getMessage());

            // 检查异常是否为服务断开异常
            if (throwable instanceof Exception && throwable.getMessage() != null &&
                    throwable.getMessage().contains("Service is disconnected")) {
                HiLog.warn(LABEL_LOG, "Health service disconnected, not restarting advertising");
                return; // 不重启广播
            }

            // 检查服务是否运行
            if (!isServiceRunning) {
                HiLog.warn(LABEL_LOG, "Service not running, not restarting advertising");
                return; // 服务已停止，不重启广播
            }

            // 避免多线程并发重启，使用延迟执行
            new Thread(() -> {
                try {
                    Thread.sleep(1000); // 延迟1秒
                    if (isServiceRunning) { // 再次检查服务状态
                        restartAdvertising();
                    }
                } catch (Exception e) {
                    HiLog.error(LABEL_LOG, "Error in delayed restart: " + e.getMessage());
                }
            }).start();
        });
    }

    @Override
    public void onStart(Intent intent) {
        HiLog.info(LABEL_LOG, "BluetoothService::onStart");
        super.onStart(intent);

        try {
            // 标记服务已启动
            isServiceRunning = true;
            Utils.init(getContext());
            setupBackgroundNotification();
            deviceManager = DeviceManager.getInstance(getContext());
            initNotificationId();

            if (dataManager.getUploadMethod().equals("bluetooth")) {
                // 使用全局锁确保线程安全
                synchronized (GLOBAL_BLE_LOCK) {
                    // 清理可能存在的旧服务
                    if (hasActiveGattService()) {
                        HiLog.warn(LABEL_LOG, "Active GATT service found on start, destroying it");
                        destroyGattService();
                        Thread.sleep(500);
                    }

                    // 初始化外设管理器
                    peripheralManagerCallback = new MyBlePeripheralManagerCallback();

                    // 初始化广播器，确保不为null
                    advertiser = new BleAdvertiser(this, new BleAdvertiseCallback() {
                        @Override
                        public void startResultEvent(int result) {
                            if (result == BleAdvertiseCallback.RESULT_SUCC) {
                                HiLog.info(LABEL_LOG, "Advertising started successfully");
                            } else {
                                HiLog.error(LABEL_LOG, "Failed to start advertising, result: " + result);

                                // 尝试重新初始化广播
                                new Thread(() -> {
                                    try {
                                        Thread.sleep(2000);
                                        if (isServiceRunning && !isAdvertising) {
                                            synchronized (GLOBAL_BLE_LOCK) {
                                                HiLog.info(LABEL_LOG, "Retrying advertising start");
                                                startAdvertising();
                                            }
                                        }
                                    } catch (Exception e) {
                                        HiLog.error(LABEL_LOG, "Error in retry advertising: " + e.getMessage());
                                    }
                                }).start();
                            }
                        }
                    });
                    Thread.sleep(200);

                    // 创建服务
                    if (!createGattService()) {
                        throw new RuntimeException("Failed to create GATT service");
                    }
                    Thread.sleep(300);

                    // 启动广播
                    startAdvertising();

                    // 为确保服务已正确添加，强制执行GC以清理旧对象
                    System.gc();
                    Thread.sleep(200);
                }
            }
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "Error in onStart: " + e.getMessage(), e);
            // 延迟重启，避免死循环
            if (isServiceRunning) {
                new Thread(() -> {
                    try {
                        Thread.sleep(3000); // 增加延迟时间
                        synchronized (GLOBAL_BLE_LOCK) {
                            if (isServiceRunning && !hasActiveGattService()) {
                                restartAdvertising();
                            }
                        }
                    } catch (Exception ex) {
                        HiLog.error(LABEL_LOG, "Error in delayed restart: " + ex.getMessage());
                    }
                }).start();
            }
        }
    }

    private void setupBackgroundNotification() {
        NotificationRequest request = new NotificationRequest(1003);
        NotificationRequest.NotificationNormalContent content = new NotificationRequest.NotificationNormalContent();
        content.setTitle("BluetoothService").setText("keepServiceAlive");
        NotificationRequest.NotificationContent notificationContent = new NotificationRequest.NotificationContent(content);
        request.setContent(notificationContent);
        keepBackgroundRunning(1003, request);
        showNotification("启动蓝牙服务");
    }

    private void initNotificationId() {
        String storedNotificationId = fetchValue("notificationId");
        if (storedNotificationId.isEmpty()) {
            notificationId = 3000;
            storeValue("notificationId", String.valueOf(notificationId));
        } else {
            notificationId = Integer.parseInt(storedNotificationId);
        }
    }

    private class MyBlePeripheralManagerCallback extends BlePeripheralManagerCallback {
        @Override
        public void connectionStateChangeEvent(
                BlePeripheralDevice device, int interval, int latency, int timeout, int status) {
            if (status == BlePeripheralDevice.OPERATION_SUCC) {
                isConnected = true;
                peripheralDevice = device;
                HiLog.info(LABEL_LOG, "设备 " + device.getDeviceAddr() + " 已连接");

                // 连接成功后主动发送设备信息
                new Thread(() -> {
                    try {
                        Thread.sleep(1000); // 等待足够时间确保连接稳定
                        
                        // 确保推送队列已初始化
                        if (pushQueue == null) {
                            pushQueue = new LinkedBlockingQueue<>();
                        }

                        // 检查是否需要发送初始设备信息（避免重复发送）
                        long currentTime = System.currentTimeMillis();
                        if (currentTime - lastInitialDeviceDataTime > INITIAL_DEVICE_DATA_INTERVAL) {
                            String deviceInfo = Utils.getDeviceInfo();
                            if (deviceInfo != null && !deviceInfo.isEmpty()) {
                                try {
                                    JSONObject deviceJson = JsonUtil.parse(deviceInfo);
                                    pushPacket(TYPE_DEVICE, deviceJson);
                                    lastInitialDeviceDataTime = currentTime; // 更新发送时间
                                    HiLog.info(LABEL_LOG, "已发送初始设备信息");
                                } catch (Exception e) {
                                    HiLog.error(LABEL_LOG, "发送初始设备信息失败: " + e.getMessage());
                                }
                            }
                        } else {
                            HiLog.debug(LABEL_LOG, "跳过初始设备信息发送，距离上次发送时间过短");
                        }
                    } catch (Exception e) {
                        HiLog.error(LABEL_LOG, "连接后处理异常: " + e.getMessage());
                    }
                }).start();
            } else {
                // 仅在之前已连接的情况下才可能需要重启广播
                boolean wasConnected = isConnected;
                isConnected = false;
                peripheralDevice = null;

                if (wasConnected && isServiceRunning) {
                    HiLog.info(LABEL_LOG, "Device disconnected, checking if restart needed");
                    // 使用延迟执行，避免在回调中直接重启
                    new Thread(() -> {
                        try {
                            Thread.sleep(2000); // 等待2秒确保系统状态稳定
                            synchronized (GLOBAL_BLE_LOCK) {
                                // 双重检查服务状态和连接状态
                                if (isServiceRunning && !isConnected && !isAdvertising) {
                                    HiLog.info(LABEL_LOG, "Restarting advertising after disconnect");
                                    restartAdvertising();
                                }
                            }
                        } catch (Exception e) {
                            HiLog.error(LABEL_LOG, "Error in delayed restart: " + e.getMessage());
                        }
                    }).start();
                }
            }
        }

        /**
         * HarmonyOS 外设收到 Central 的 MTU 请求之后，
         * 底层会回调这个方法，你一定要 override 并且调用 super，
         * 否则系统不会把响应发回去，Central 就一直等 timeout。
         */
        @Override
        public void mtuUpdateEvent(BlePeripheralDevice device, int newMtu) {
            super.mtuUpdateEvent(device, newMtu);
            HiLog.info(LABEL_LOG, "外设 MTU 已更新: " + newMtu);
            mtu = newMtu;  // 更新一下你自己的 mtu 变量
        }

        @Override
        public void receiveDescriptorWriteRequestEvent(
                BlePeripheralDevice device,
                int transId,
                GattDescriptor descriptor,
                boolean isPrep,
                boolean needRsp,
                int offset,
                byte[] value) {
            
            long currentTime = System.currentTimeMillis();
            String deviceAddr = device.getDeviceAddr();
            String descriptorId = deviceAddr + ":" + descriptor.getUuid().toString() + ":" + transId;
            
            // 1. 检查是否为重复的描述符写入请求
            if (processedDescriptorWrites.contains(descriptorId)) {
                HiLog.warn(LABEL_LOG, String.format("忽略重复的描述符写入请求: 设备=%s, UUID=%s, transId=%d", 
                    deviceAddr, descriptor.getUuid().toString(), transId));
                return;
            }
            
            // 2. 检查写入频率，防止过度频繁的请求
            if (currentTime - lastDescriptorWriteTime < MIN_DESCRIPTOR_WRITE_INTERVAL) {
                HiLog.warn(LABEL_LOG, String.format("描述符写入过于频繁，忽略请求: 距离上次仅%dms", 
                    currentTime - lastDescriptorWriteTime));
                return;
            }
            
            // 3. 验证描述符是否为CCCD
            if (!CCCD_UUID.equals(descriptor.getUuid())) {
                HiLog.warn(LABEL_LOG, "非CCCD描述符写入请求，忽略: " + descriptor.getUuid().toString());
                if (needRsp && blePeripheralManager != null) {
                    // 对非CCCD描述符，发送错误响应
                    blePeripheralManager.sendResponse(device, transId, 1, 0, null); // status=1表示错误
                }
                return;
            }
            
            // 4. 验证value的有效性
            if (value == null || value.length == 0) {
                HiLog.warn(LABEL_LOG, "描述符写入值为空，忽略");
                if (needRsp && blePeripheralManager != null) {
                    blePeripheralManager.sendResponse(device, transId, 1, 0, null); // 发送错误响应
                }
                return;
            }
            
            // 5. 只有在真正需要且条件满足时才发送响应
            boolean responseResult = false;
            if (needRsp && blePeripheralManager != null && isServiceRunning) {
                try {
                    // 发送成功响应，echo回原始value
                    responseResult = blePeripheralManager.sendResponse(device, transId, 0, 0, value);
                    if (responseResult) {
                        HiLog.info(LABEL_LOG, String.format("CCCD描述符写响应成功: 设备=%s, 值=%s", 
                            deviceAddr, java.util.Arrays.toString(value)));
                        
                        // 记录已处理的请求，防重复
                        processedDescriptorWrites.add(descriptorId);
                        if (processedDescriptorWrites.size() > 100) { // 防止内存泄漏
                            processedDescriptorWrites.clear();
                        }
                        
                        lastDescriptorWriteTime = currentTime;
                    } else {
                        HiLog.error(LABEL_LOG, "CCCD描述符写响应失败");
                    }
                } catch (Exception e) {
                    HiLog.error(LABEL_LOG, "发送描述符写响应异常: " + e.getMessage());
                }
            }

            // 6. 异步处理CCCD逻辑，避免阻塞GATT操作，且只在响应成功后处理
            if (responseResult && CCCD_UUID.equals(descriptor.getUuid())) {
                new Thread(() -> {
                    try {
                        // 等待一小段时间确保响应已发送
                        Thread.sleep(50);
                        
                        boolean notificationsEnabled = (value.length > 0 && (value[0] == 0x01 || value[0] == 0x02));
                        UUID charUuid = descriptor.getCharacteristic().getUuid();
                        
                        HiLog.info(LABEL_LOG, String.format("设备 %s %s notifications for characteristic %s",
                                deviceAddr,
                                notificationsEnabled ? "启用" : "禁用",
                                charUuid.toString()));

                        // 只处理数据特性的notify状态变化
                        if (DATA_CHAR_UUID.equals(charUuid)) {
                            if (notificationsEnabled) {
                                // 防止短时间内多次启用notify导致重复推送
                                long currentTime2 = System.currentTimeMillis();
                                if (currentTime2 - lastNotifyEnableTime < MIN_NOTIFY_ENABLE_INTERVAL) {
                                    HiLog.warn(LABEL_LOG, String.format("忽略重复的notify启用请求，距离上次启用仅%dms", 
                                        currentTime2 - lastNotifyEnableTime));
                                    return;
                                }
                                lastNotifyEnableTime = currentTime2;
                                
                                HiLog.info(LABEL_LOG, "客户端请求启用数据通知");
                                
                                // 延迟启动推送循环，确保连接稳定
                                Thread.sleep(200);
                                startPushLoop();
                            } else {
                                HiLog.info(LABEL_LOG, "客户端禁用数据通知");
                                stopPushLoop();
                            }
                        }
                        
                        // 完全移除服务变更特性的处理，避免循环重连问题
                        
                    } catch (Exception e) {
                        HiLog.error(LABEL_LOG, "处理CCCD描述符写入异常: " + e.getMessage());
                    }
                }).start();
            }
        }

        @Override
        public void notificationSentEvent(BlePeripheralDevice device, int status) {
            if (status == BlePeripheralDevice.OPERATION_SUCC) {
                HiLog.debug(LABEL_LOG, String.format("Notification sent to device %s", device.getDeviceAddr()));
            } else {
                HiLog.error(LABEL_LOG, String.format("Failed to send notification to device %s, status: %d",
                        device.getDeviceAddr(), status));
            }
        }

        @Override
        public void receiveCharacteristicWriteEvent(
                BlePeripheralDevice device,
                int transId,
                GattCharacteristic characteristic,
                boolean isPrep,
                boolean needRsp,
                int offset,
                byte[] value) {
            
            // 首先立即发送GATT响应，避免客户端超时
            if (needRsp && blePeripheralManager != null) {
                boolean responseResult = blePeripheralManager.sendResponse(device, transId, 0, 0, null);
                HiLog.debug(LABEL_LOG, "GATT写响应发送" + (responseResult ? "成功" : "失败"));
            }
            
            // 异步处理命令，避免阻塞GATT响应
            if (CMD_CHAR_UUID.equals(characteristic.getUuid()) && value != null && value.length > 0) {
                String command = new String(value, StandardCharsets.UTF_8);
                
                // 使用单独线程处理命令，确保不阻塞GATT操作
                new Thread(() -> {
                    try {
                        handleCommand(device, command);
                    } catch (Exception e) {
                        HiLog.error(LABEL_LOG, "异步处理命令失败: " + e.getMessage());
                    }
                }).start();
            }
        }
    }

    private void handleCommand(BlePeripheralDevice device, String command) {
        try {
            // 增加输入验证和清理
            if (command == null || command.trim().isEmpty()) {
                HiLog.warn(LABEL_LOG, "接收到空命令，忽略");
                return;
            }
            
            // 清理可能的控制字符和无效字节
            String cleanCommand = command.trim().replaceAll("[\\x00-\\x1F\\x7F]", "");
            HiLog.debug(LABEL_LOG, "接收命令长度: " + command.length() + ", 清理后: " + cleanCommand.length());
            
            // 检查是否为有效JSON格式
            if (!cleanCommand.startsWith("{") || !cleanCommand.endsWith("}")) {
                HiLog.warn(LABEL_LOG, "接收到非JSON格式命令，忽略: " + 
                    (cleanCommand.length() > 50 ? cleanCommand.substring(0, 50) + "..." : cleanCommand));
                return;
            }
            
            JSONObject cmdJson = JsonUtil.parse(cleanCommand);
            if (cmdJson == null) {
                HiLog.error(LABEL_LOG, "JSON解析失败: " + cleanCommand);
                return;
            }
            
            String cmdType = cmdJson.optString("type", "");
            if (cmdType.isEmpty()) {
                HiLog.warn(LABEL_LOG, "命令缺少type字段: " + cleanCommand);
                return;
            }

            switch (cmdType) {
                case CMD_MESSAGE:
                    handleMessageCommand(cmdJson);
                    break;
                case CMD_CONFIG:
                    handleConfigCommand(cmdJson);
                    break;
                case CMD_MTU:
                    handleMtuCommand(cmdJson);
                    break;
                case CMD_PROTOCOL_PROBE:
                    handleProbeCommand(cmdJson);
                    break;
                case CMD_HEALTH_DATA_ACK:
                    handleHealthDataAck(cmdJson);
                    break;
                case CMD_DISCONNECT:
                    isConnected = false;
                    peripheralDevice = null;
                    break;
                default:
                    HiLog.warn(LABEL_LOG, "未知命令类型: " + cmdType);
            }
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "处理命令出错: " + e.getMessage() + 
                ", 原始命令: " + (command != null ? 
                (command.length() > 100 ? command.substring(0, 100) + "..." : command) : "null"));
        }
    }

    private void handleProbeCommand(JSONObject cmdJson) {
        try {
            String probeType = cmdJson.optString("probe_type", "device_status");
            
            // 构建响应包
            JSONObject response = new JSONObject();
            response.put("type", "probe_response");
            response.put("probe_type", probeType);
            response.put("status", "active");
            response.put("service_running", isServiceRunning);
            response.put("health_ready", dataManager.getIsHealthServiceReady());
            response.put("timestamp", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
            
            // 使用BleDataProcessor发送事件数据，替代直接toString()
            HiLog.info(LABEL_LOG, "发送探测响应: " + probeType);
            pushPacket(TYPE_PROBE_RESPONSE, response);
            
            HiLog.info(LABEL_LOG, "已响应探测命令: " + probeType);
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "处理探测命令出错: " + e.getMessage());
        }
    }

    private void handleHealthDataAck(JSONObject cmdJson) {
        try {
            String action = cmdJson.optString("action", "");
            String transferId = cmdJson.optString("transfer_id", "");
            boolean success = cmdJson.optBoolean("success", false);
            
            if (action.equals("receive_ready")) {
                // 客户端准备好接收数据
                HiLog.info(LABEL_LOG, "客户端已准备好接收健康数据，传输ID: " + transferId);
            } else if (action.equals("receive_complete")) {
                // 客户端确认数据接收完成
                if (success) {
                    HiLog.info(LABEL_LOG, "客户端确认健康数据传输成功，传输ID: " + transferId);
                } else {
                    // 传输失败，可能需要重试
                    String error = cmdJson.optString("error", "未知错误");
                    HiLog.error(LABEL_LOG, "客户端报告健康数据传输失败: " + error + "，传输ID: " + transferId);
                    
                    // 如果需要，这里可以添加自动重试逻辑
                }
            }
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "处理健康数据确认出错: " + e.getMessage());
        }
    }

    private void handleMessageCommand(JSONObject cmdJson) {
        try {
            String messageType = cmdJson.getString("message_type");
            String translatedMessageType = MESSAGE_TYPE_MAP.getOrDefault(messageType, messageType);

            String messageContent = buildMessageContent(cmdJson, translatedMessageType);
            showNotification(messageContent);

            // 更新消息状态和接收时间
            cmdJson.put("message_status", "2"); // 更新消息状态为2
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
            String formattedTime = Instant.now().atZone(ZoneId.of("Asia/Shanghai")).format(formatter);
            cmdJson.put("received_time", formattedTime);

            JSONObject responseMessage = buildMessageResponse(cmdJson);
            pushPacket(TYPE_MESSAGE_RESPONSE, responseMessage);
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "Error handling message command: " + e.getMessage(), e);
        }
    }

    private String buildMessageContent(JSONObject cmdJson, String translatedMessageType) throws Exception {
        if (cmdJson.isNull("user_name") || cmdJson.getString("user_name").isEmpty()) {
            return String.format("平台在%s群发：%s, 内容为:%s (部门: %s)",
                    cmdJson.getString("sent_time"),
                    translatedMessageType,
                    cmdJson.getString("message"),
                    cmdJson.getString("department_name"));
        } else {
            return String.format("平台在%s发来：%s, 内容为:%s (来自: %s, 部门: %s)",
                    cmdJson.getString("sent_time"),
                    translatedMessageType,
                    cmdJson.getString("message"),
                    cmdJson.getString("user_name"),
                    cmdJson.getString("department_name"));
        }
    }

    private JSONObject buildMessageResponse(JSONObject cmdJson) throws Exception {
        JSONObject response = new JSONObject();
        response.put("type", TYPE_MESSAGE_RESPONSE);
        response.put("department_id", cmdJson.getString("department_id"));
        response.put("department_name", cmdJson.getString("department_name"));
        response.put("is_public", cmdJson.getBoolean("is_public"));
        response.put("message", cmdJson.getString("message"));
        response.put("message_id", cmdJson.getString("message_id"));
        response.put("message_type", cmdJson.getString("message_type"));
        response.put("sent_time", cmdJson.getString("sent_time"));
        response.put("user_id", cmdJson.getString("user_id"));
        response.put("user_name", cmdJson.getString("user_name"));
        response.put("sender_type", "device");
        response.put("receiver_type", "platform");
        response.put("device_sn", dataManager.getDeviceSn());

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String formattedTime = Instant.now().atZone(ZoneId.of("Asia/Shanghai")).format(formatter);
        response.put("received_time", formattedTime);
        response.put("message_status", "responded");

        return response;
    }

    private void handleConfigCommand(JSONObject cmdJson) {
        HiLog.info(LABEL_LOG, "Received config command: " + cmdJson.toString());
    }

    private void handleMtuCommand(JSONObject cmdJson) {
        int newMtu = cmdJson.optInt("mtu", DEFAULT_MTU);
        if (newMtu > DEFAULT_MTU) {
            this.mtu = newMtu;
            // 主动请求 MTU 更新

            HiLog.info(LABEL_LOG, "MTU updated to: " + newMtu);
            return;
        }
        HiLog.warn(LABEL_LOG, "MTU update failed: " + newMtu);
    }

    private void pushCommonEvent(String commonEvent) {
        // 先保存事件到队列
        pendingCommonEvents.offer(commonEvent);
        
        // 尝试立即发送
        processEventQueue();
        
        // 如果还没有重试任务，启动一个
        if (eventRetryTask == null && scheduler != null && !scheduler.isShutdown()) {
            eventRetryTask = scheduler.scheduleAtFixedRate(() -> {
                if (!pendingCommonEvents.isEmpty()) {
                    processEventQueue();
                } else if (eventRetryTask != null) {
                    eventRetryTask.cancel(false);
                    eventRetryTask = null;
                }
            }, 5, 5, TimeUnit.SECONDS);
        }
    }

    private void processEventQueue() {
        if (!isConnected || peripheralDevice == null || dataChar == null || blePeripheralManager == null) {
            HiLog.warn(LABEL_LOG, "无法推送公共事件：设备未连接或组件未初始化，事件将延迟发送");
            return;
        }
        
        while (!pendingCommonEvents.isEmpty()) {
            String event = pendingCommonEvents.peek();
            if (event == null) break;
            
            try {
                String[] parts = event.split(":");
                if (parts.length >= 3) {
                    JSONObject eventJson = new JSONObject();
                    eventJson.put("action", parts[0]);
                    eventJson.put("value", parts[1]);
                    eventJson.put("device_sn", parts[2]);
                    eventJson.put("timestamp", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
                    
                    HiLog.info(LABEL_LOG, "正在推送公共事件: " + eventJson.toString());
                    
                    // 使用诊断方法检查
                    String diagnosis = diagnosticJson(eventJson.toString());
                    if (!diagnosis.startsWith("Valid")) {
                        HiLog.error(LABEL_LOG, "无效的公共事件JSON: " + diagnosis);
                        pendingCommonEvents.poll(); // 移除无效事件
                        continue;
                    }
                    
                    // 直接使用pushPacket而不依赖其返回值
                    pushPacket(TYPE_COMMON_EVENT, eventJson);
                    // 成功送出请求后移除事件 (注意：这里不能保证实际发送成功)
                    pendingCommonEvents.poll();
                } else {
                    HiLog.error(LABEL_LOG, "无效的公共事件格式: " + event);
                    pendingCommonEvents.poll(); // 移除格式错误的事件
                }
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "推送公共事件出错: " + e.getMessage());
                break; // 出错时停止处理队列
            }
        }
    }

    private void pushPacket(String type, JSONObject body) {
        // 如果启用了新协议，使用二进制编码
        if (dataManager.getUseBinaryProtocol()) {
            byte binaryType;
            String jsonData = body.toString();
            
            switch (type) {
                case TYPE_HEALTH:
                    binaryType = BleProtocolEncoder.TYPE_HEALTH_DATA;
                    break;
                case TYPE_DEVICE:
                    binaryType = BleProtocolEncoder.TYPE_DEVICE_INFO;
                    break;
                case TYPE_COMMON_EVENT:
                    binaryType = BleProtocolEncoder.TYPE_COMMON_EVENT;
                    break;
                default:
                    // 对于其他类型，仍使用JSON格式
                    pushPacketLegacy(type, body);
                    return;
            }
            
            pushBinaryPacket(binaryType, jsonData);
            return;
        }
        
        // 回退到原有的JSON协议
        pushPacketLegacy(type, body);
    }

    // 保留原有的JSON推送逻辑
    private void pushPacketLegacy(String type, JSONObject body) {
        if (dataChar == null || blePeripheralManager == null || peripheralDevice == null) {
            HiLog.error(LABEL_LOG, "Cannot push packet: missing required components");
            return;
        }

        try {
            // 1. 添加唯一数据包ID和广播设备ID
            String packetId = UUID.randomUUID().toString();
            body.put("packet_id", packetId);
            body.put("device_broadcast_id", deviceBroadcastId);

            // 2. 构造完整包，不再需要类型转换
            JSONObject fullPacket = JsonUtil.createPacket(type, body);
            String jsonStr = fullPacket.toString();

            // 检查JSON有效性
            if (!JsonUtil.isValidJson(jsonStr)) {
                HiLog.error(LABEL_LOG, "Invalid JSON generated: " + jsonStr);
                return;
            }

            HiLog.info(LABEL_LOG, "Original JSON length: " + jsonStr.length());

            // 3. 计算可用空间
            int attMtu = this.mtu;
            int attOverhead = 3;  // ATT notification header
            int jsonOverhead = 120; // JSON包装的预估开销，增大以防止边界问题

            // 4. 尝试直接发送
            if (jsonStr.length() <= attMtu - attOverhead) {
                // 直接发送完整JSON，确保不重复发送
                if (sentPacketIds.contains(packetId)) {
                    HiLog.warn(LABEL_LOG, "Duplicate packet detected, skipping: " + packetId);
                    return;
                }
                sentPacketIds.add(packetId);
                if (sentPacketIds.size() > 100) { // 限制集合大小，防止内存泄漏
                    sentPacketIds.clear();
                }

                pushQueue.offer(new ChunkData("direct", 1, 0, jsonStr.getBytes(StandardCharsets.UTF_8), false));
                HiLog.debug(LABEL_LOG, "Direct sending packet: " + type);
                return;
            }

            // 5. 需要分块时，使用优化的分块算法
            sendChunkedPacket(jsonStr, packetId);
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "Error preparing packet: " + e.getMessage(), e);
        }
    }

    // 新增方法：优化的分块发送算法
    private void sendChunkedPacket(String jsonStr, String packetId) {
        try {
            // 先检查原始JSON格式
            String diagnosis = diagnosticJson(jsonStr);
            HiLog.info(LABEL_LOG, "JSON Diagnosis: " + diagnosis);

            // 如果JSON无效，尝试修复
            if (!diagnosis.startsWith("Valid")) {
                HiLog.warn(LABEL_LOG, "Attempting to fix invalid JSON");
                // 移除可能的多余转义
                jsonStr = JsonUtil.unescapeJson(jsonStr);
                // 再次检查
                diagnosis = diagnosticJson(jsonStr);
                HiLog.info(LABEL_LOG, "After fix diagnosis: " + diagnosis);

                if (!diagnosis.startsWith("Valid")) {
                    HiLog.error(LABEL_LOG, "Cannot fix invalid JSON, aborting chunked send");
                    return;
                }
            }

            // 计算可用空间
            int attMtu = this.mtu;
            int attOverhead = 3;  // ATT notification header
            int headerSize = 70;  // 包头大小预估
            int maxContentSize = attMtu - attOverhead - headerSize;

            if (maxContentSize <= 10) {
                HiLog.error(LABEL_LOG, "MTU too small for chunking");
                return;
            }

            // 使用不带转义的原始JSON字符串作为数据源
            byte[] jsonBytes = jsonStr.getBytes(StandardCharsets.UTF_8);

            // 计算分块数
            int totalChunks = (int) Math.ceil(jsonBytes.length / (double)maxContentSize);
            String messageId = UUID.randomUUID().toString();

            HiLog.info(LABEL_LOG, String.format("Sending %s in %d chunks (MTU=%d, maxContent=%d)",
                    packetId, totalChunks, attMtu, maxContentSize));

            // 将原始JSON分块发送
            for (int i = 0; i < totalChunks; i++) {
                int start = i * maxContentSize;
                int end = Math.min(start + maxContentSize, jsonBytes.length);

                // 提取当前分块
                byte[] chunkBytes = Arrays.copyOfRange(jsonBytes, start, end);
                String chunkContent = new String(chunkBytes, StandardCharsets.UTF_8);

                // 构建分块数据包
                JSONObject chunkPacket = new JSONObject();
                JSONObject header = new JSONObject();
                header.put("id", messageId);
                header.put("total", totalChunks);
                header.put("index", i);
                header.put("body", chunkContent);
                chunkPacket.put("packet", header);

                String packetStr = chunkPacket.toString();

                // 验证分块大小
                if (packetStr.getBytes(StandardCharsets.UTF_8).length > attMtu - attOverhead) {
                    HiLog.warn(LABEL_LOG, String.format("Chunk %d/%d exceeds MTU: %d bytes",
                            i+1, totalChunks, packetStr.getBytes(StandardCharsets.UTF_8).length));

                    // 动态调整分块大小，减小20%
                    maxContentSize = (int)(maxContentSize * 0.8);
                    i = -1; // 重新开始分块
                    totalChunks = (int) Math.ceil(jsonBytes.length / (double)maxContentSize);
                    HiLog.info(LABEL_LOG, String.format("Adjusted chunk size to %d, new total: %d",
                            maxContentSize, totalChunks));
                    continue;
                }

                // 加入发送队列
                pushQueue.offer(new ChunkData(messageId, totalChunks, i, chunkBytes, false));
                HiLog.debug(LABEL_LOG, String.format("Queued chunk %d/%d: %d bytes",
                        i+1, totalChunks, chunkBytes.length));
            }
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "Error in sendChunkedPacket: " + e.getMessage(), e);
        }
    }

    private void sendChunk(ChunkData chunk) {
        synchronized (writeLock) {
            try {
                // 避免发送空数据
                if (chunk.data == null || chunk.data.length == 0) {
                    HiLog.error(LABEL_LOG, "数据块为空，跳过发送");
                    return;
                }

                // 检查连接状态
                if (!isConnected || peripheralDevice == null || dataChar == null || blePeripheralManager == null) {
                    HiLog.error(LABEL_LOG, "连接状态异常，无法发送数据块");
                    return;
                }

                // 检查数据块大小
                if (chunk.data.length > mtu - MTU_OVERHEAD) {
                    HiLog.error(LABEL_LOG, String.format("数据块大小%d超出MTU限制%d",
                            chunk.data.length, mtu - MTU_OVERHEAD));
                    return;
                }

                // 等待之前的写入完成
                while (isWriting && isServiceRunning) {
                    Thread.sleep(10);
                }

                // 控制发送频率，防止GATT写入冲突
                long currentTime = System.currentTimeMillis();
                long timeSinceLastWrite = currentTime - lastWriteTime;
                if (timeSinceLastWrite < MIN_WRITE_INTERVAL) {
                    Thread.sleep(MIN_WRITE_INTERVAL - timeSinceLastWrite);
                }

                // 标记开始写入
                isWriting = true;
                lastWriteTime = System.currentTimeMillis();

                // 设置数据
                dataChar.setValue(chunk.data);

                boolean success = false;
                int retryCount = 0;

                while (!success && retryCount < MAX_RETRIES && isServiceRunning) {
                    // 再次检查连接状态
                    if (!isConnected || peripheralDevice == null) {
                        HiLog.error(LABEL_LOG, "发送过程中连接断开，停止重试");
                        break;
                    }

                    success = blePeripheralManager.notifyCharacteristicChanged(peripheralDevice, dataChar, false);

                    if (!success) {
                        retryCount++;
                        HiLog.warn(LABEL_LOG, String.format("数据块发送失败，重试%d/%d (可能是GATT忙碌)", 
                                retryCount, MAX_RETRIES));
                        
                        // 指数退避，给更多时间让GATT恢复
                        long backoffTime = RETRY_DELAY_MS * (1L << retryCount);
                        Thread.sleep(Math.min(backoffTime, 1000)); // 最大等待1秒
                    }
                }

                // 清除写入标记
                isWriting = false;

                if (!success) {
                    HiLog.error(LABEL_LOG, String.format("数据块%d/%d发送最终失败，已重试%d次 (GATT可能持续忙碌)",
                            chunk.index + 1, chunk.totalChunks, MAX_RETRIES));
                    
                    // 对于关键二进制数据，记录警告
                    if (chunk.isBinary) {
                        HiLog.warn(LABEL_LOG, "二进制数据发送失败，可能影响数据完整性");
                    }
                    return;
                }

                // 记录发送日志
                if (chunk.isBinary) {
                    HiLog.debug(LABEL_LOG, String.format("发送二进制分包 %d/%d [%d字节]",
                            chunk.index + 1, chunk.totalChunks, chunk.data.length));
                } else if (!"direct".equals(chunk.messageId)) {
                    HiLog.debug(LABEL_LOG, String.format("发送数据块 %d/%d [%d字节]",
                            chunk.index + 1, chunk.totalChunks, chunk.data.length));
                }

                // 发送成功后等待，避免GATT队列溢出
                Thread.sleep(30);
                
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                HiLog.warn(LABEL_LOG, "发送数据块被中断");
                isWriting = false; // 确保清除写入标记
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "发送数据块出错: " + e.getMessage());
                isWriting = false; // 确保清除写入标记
            }
        }
    }

    private void startPushLoop() {
        // 使用锁确保只有一个线程能启动推送循环
        synchronized (pushLoopLock) {
            // 如果推送循环已经在运行，直接返回
            if (isPushLoopRunning) {
                HiLog.warn(LABEL_LOG, "推送循环已在运行，忽略重复启动请求");
                return;
            }

            HiLog.info(LABEL_LOG, "Starting push loop");

            // 检查服务是否运行
            if (!isServiceRunning) {
                HiLog.warn(LABEL_LOG, "Service not running, skipping push loop start");
                return;
            }

            // 先停止已有的循环
            stopPushLoop();

            try {
                // 初始化线程池和队列
                scheduler = Executors.newScheduledThreadPool(2);
                pushExecutor = Executors.newSingleThreadExecutor();
                pushQueue = new LinkedBlockingQueue<>();

                // 启动推送线程
                pushExecutor.submit(() -> {
                    while (!Thread.currentThread().isInterrupted() && isServiceRunning) {
                        try {
                            ChunkData chunk = pushQueue.poll(1, TimeUnit.SECONDS);
                            if (chunk != null && isServiceRunning) {
                                sendChunk(chunk);
                            }
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                            break;
                        } catch (Exception e) {
                            HiLog.error(LABEL_LOG, "Error in push thread: " + e.getMessage(), e);
                            if (!isServiceRunning) {
                                break; // 服务已停止，退出循环
                            }
                        }
                    }
                    HiLog.info(LABEL_LOG, "Push thread exited");
                });

                // 获取配置的上传间隔，确保合理的默认值
                //int healthInterval = Math.max(dataManager.getUploadHealthInterval(), 60);
                //int deviceInterval = Math.max(dataManager.getUploadDeviceInterval(), 600);

                int healthInterval = dataManager.getUploadHealthInterval();
                int deviceInterval = dataManager.getUploadDeviceInterval();

                // 启动健康数据定时任务
                healthTask = scheduler.scheduleAtFixedRate(() -> {
                    if (!isServiceRunning) {
                        return; // 服务已停止，不执行
                    }

                    if (isConnected && peripheralDevice != null) {
                        try {
                            String currentHealth = safeGetHealthInfo();
                            if (currentHealth != null && !currentHealth.isEmpty()) {
                                JSONObject healthJson = JsonUtil.parse(currentHealth);
                                HiLog.info(LABEL_LOG, "推送健康数据: " + healthJson.toString());
                                pushPacket(TYPE_HEALTH, healthJson);
                            } else {
                                HiLog.warn(LABEL_LOG, "Health data is empty, skipping push");
                            }
                        } catch (Exception e) {
                            HiLog.error(LABEL_LOG, "Error pushing health data: " + e.getMessage(), e);
                        }
                    }
                }, 0, healthInterval, TimeUnit.SECONDS);

                // 启动设备数据定时任务
                deviceTask = scheduler.scheduleAtFixedRate(() -> {
                    if (!isServiceRunning) {
                        return; // 服务已停止，不执行
                    }

                    if (isConnected && peripheralDevice != null) {
                        try {
                            String currentDevice = safeGetDeviceInfo();

                            if (currentDevice != null && !currentDevice.isEmpty()) {
                                JSONObject deviceJson = JsonUtil.parse(currentDevice);
                                HiLog.info(LABEL_LOG, "推送设备数据: " + deviceJson.toString());
                                pushPacket(TYPE_DEVICE, deviceJson);
                                
                                // 同步更新初始设备信息发送时间，避免重复发送
                                lastInitialDeviceDataTime = System.currentTimeMillis();
                            } else {
                                HiLog.warn(LABEL_LOG, "Device data is empty, skipping push");
                            }
                        } catch (Exception e) {
                            HiLog.error(LABEL_LOG, "Error pushing device data: " + e.getMessage(), e);
                        }
                    }
                }, 0, deviceInterval, TimeUnit.SECONDS);

                // 添加心跳包定时任务(每30秒发送一次)
                if (dataManager.getUseBinaryProtocol()) {
                    scheduler.scheduleAtFixedRate(() -> {
                        if (!isServiceRunning) return;
                        if (isConnected && peripheralDevice != null) {
                            sendHeartbeat();
                        }
                    }, 30, 30, TimeUnit.SECONDS);
                }

                // 标记推送循环已启动
                isPushLoopRunning = true;
                HiLog.info(LABEL_LOG, "Push loop started successfully");
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "Error starting push loop: " + e.getMessage(), e);
                stopPushLoop(); // 发生错误时清理资源
            }
        }
    }

    private void stopPushLoop() {
        synchronized (pushLoopLock) {
            // 标记推送循环已停止
            isPushLoopRunning = false;
            
            // 使用标志防止重复停止
            if (healthTask != null) {
                try {
                    healthTask.cancel(true); // 允许中断
                } catch (Exception e) {
                    HiLog.warn(LABEL_LOG, "Error canceling health task: " + e.getMessage());
                } finally {
                    healthTask = null;
                }
            }

            if (deviceTask != null) {
                try {
                    deviceTask.cancel(true); // 允许中断
                } catch (Exception e) {
                    HiLog.warn(LABEL_LOG, "Error canceling device task: " + e.getMessage());
                } finally {
                    deviceTask = null;
                }
            }

            if (scheduler != null) {
                try {
                    scheduler.shutdownNow(); // 立即关闭所有任务
                    if (!scheduler.awaitTermination(1, TimeUnit.SECONDS)) {
                        HiLog.warn(LABEL_LOG, "Scheduler did not terminate in time");
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    HiLog.warn(LABEL_LOG, "Scheduler shutdown interrupted");
                } catch (Exception e) {
                    HiLog.warn(LABEL_LOG, "Error shutting down scheduler: " + e.getMessage());
                } finally {
                    scheduler = null;
                }
            }

            if (pushExecutor != null) {
                try {
                    pushExecutor.shutdownNow(); // 立即关闭
                    if (!pushExecutor.awaitTermination(1, TimeUnit.SECONDS)) {
                        HiLog.warn(LABEL_LOG, "Push executor did not terminate in time");
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    HiLog.warn(LABEL_LOG, "Push executor shutdown interrupted");
                } catch (Exception e) {
                    HiLog.warn(LABEL_LOG, "Error shutting down push executor: " + e.getMessage());
                } finally {
                    pushExecutor = null;
                }
            }

            if (pushQueue != null) {
                try {
                    pushQueue.clear();
                } catch (Exception e) {
                    HiLog.warn(LABEL_LOG, "Error clearing push queue: " + e.getMessage());
                } finally {
                    pushQueue = null;
                }
            }

            HiLog.info(LABEL_LOG, "All push tasks stopped");
        }
    }

    private void restartAdvertising() {
        // 使用全局锁确保BLE操作的线程安全
        synchronized (GLOBAL_BLE_LOCK) {
            // 检查服务是否正在运行
            if (!isServiceRunning) {
                HiLog.warn(LABEL_LOG, "Service not running, skipping advertising restart");
                return;
            }

            HiLog.warn(LABEL_LOG, "Restarting advertising");
            try {
                // 1. 停止推送任务
                stopPushLoop();

                // 2. 完全销毁现有服务
                destroyGattService();

                // 3. 睡眠一段时间确保清理完成
                Thread.sleep(500);

                // 4. 重建广播器
                advertiser = new BleAdvertiser(this, advertiseCallback);
                Thread.sleep(200);

                // 5. 创建新的服务
                boolean created = createGattService();
                if (!created) {
                    HiLog.error(LABEL_LOG, "Failed to create GATT service, aborting restart");
                    return;
                }
                Thread.sleep(300);

                // 6. 重新启动广播
                startAdvertising();

                HiLog.info(LABEL_LOG, "Advertising restarted successfully");
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "Error restarting advertising: " + e.getMessage(), e);
            }
        }
    }

    private class MyBleAdvertiseCallback extends BleAdvertiseCallback {
        @Override
        public void startResultEvent(int result) {
            if (result == BleAdvertiseCallback.RESULT_SUCC) {
                HiLog.info(LABEL_LOG, "startAdvertising success");
            }
        }
    }

    private boolean hasActiveGattService() {
        synchronized (GLOBAL_BLE_LOCK) {
            boolean hasMainService = blePeripheralManager != null && dataChar != null && cmdChar != null;
            // 即使没有服务变更特性，也认为健康服务存在就表示GATT服务激活
            return hasMainService;
        }
    }

    private void destroyGattService() {
        synchronized (GLOBAL_BLE_LOCK) {
            try {
                // 停止广播
                if (isAdvertising && advertiser != null) {
                    try {
                        advertiser.stopAdvertising();
                    } catch (Exception e) {
                        HiLog.error(LABEL_LOG, "Error stopping advertising: " + e.getMessage());
                    }
                    isAdvertising = false;
                }

                // 清理服务
                if (blePeripheralManager != null) {
                    try {
                        blePeripheralManager.clearServices();
                        HiLog.info(LABEL_LOG, "GATT services cleared");
                        Thread.sleep(500); // 给系统时间处理
                    } catch (Exception e) {
                        HiLog.error(LABEL_LOG, "Error clearing services: " + e.getMessage());
                    }

                    // 释放资源
                    blePeripheralManager = null;
                    dataChar = null;
                    cmdChar = null;
                    serviceChangeChar = null; // 清除服务变更特性

                    if (serviceInstanceCount > 0) {
                        serviceInstanceCount--;
                    }
                    HiLog.info(LABEL_LOG, "BLE service instance destroyed, count: " + serviceInstanceCount);
                }

                // 释放广播器
                advertiser = null;
                System.gc(); // 建议系统进行垃圾回收
                Thread.sleep(300);
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "Error in destroyGattService: " + e.getMessage());
            }
        }
    }

    private boolean createGattService() {
        synchronized (GLOBAL_BLE_LOCK) {
            if (hasActiveGattService()) {
                HiLog.warn(LABEL_LOG, "GATT服务已存在，先销毁");
                destroyGattService();
            }

            try {
                // 确保回调只创建一次
                if (peripheralManagerCallback == null) {
                    peripheralManagerCallback = new MyBlePeripheralManagerCallback();
                }
                
                // 创建外设管理器
                blePeripheralManager = new BlePeripheralManager(this, peripheralManagerCallback, 1);
                Thread.sleep(300); // 给初始化足够时间
                
                // 首先创建通用属性服务
                boolean gaSuccess = setupGenericAttributeService();
                if (!gaSuccess) {
                    HiLog.warn(LABEL_LOG, "Failed to setup Generic Attribute Service, continuing...");
                    // 继续执行，因为主服务更重要
                }

                Thread.sleep(100); // 等待服务注册

                // 构造Characteristic
                GattCharacteristic data = new GattCharacteristic(
                        DATA_CHAR_UUID,
                        GATT_PERM,
                        PROP_NOTIFY
                                | GattCharacteristic.PROPERTY_WRITE_NO_RESPONSE
                                | GattCharacteristic.PROPERTY_READ
                );

                GattCharacteristic cmd = new GattCharacteristic(
                        CMD_CHAR_UUID,
                        GATT_PERM,
                        GattCharacteristic.PROPERTY_WRITE
                                | GattCharacteristic.PROPERTY_READ
                );

                // 添加CCCD
                GattDescriptor cccd = new GattDescriptor(CCCD_UUID, GATT_PERM);
                data.addDescriptor(cccd);

                // 建立Service
                GattService svc = new GattService(SERVICE_UUID, true);
                svc.addCharacteristic(data);
                svc.addCharacteristic(cmd);

                // 注册服务
                boolean success = blePeripheralManager.addService(svc);
                if (!success) {
                    HiLog.error(LABEL_LOG, "Failed to add GATT service");
                    return false;
                }

                this.dataChar = data;
                this.cmdChar = cmd;
                serviceInstanceCount++;
                HiLog.info(LABEL_LOG, "BLE service instance created, count: " + serviceInstanceCount);
                return true;
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "Error in createGattService: " + e.getMessage());
                // 清理可能部分创建的资源
                if (blePeripheralManager != null) {
                    try {
                        blePeripheralManager.clearServices();
                    } catch (Exception ex) {
                        // 忽略清理异常
                    }
                    blePeripheralManager = null;
                }
                dataChar = null;
                cmdChar = null;
                serviceChangeChar = null;
                return false;
            }
        }
    }

    private void startAdvertising() {
        synchronized (GLOBAL_BLE_LOCK) {
            HiLog.info(LABEL_LOG, "Starting advertising");
            if (!isServiceRunning) {
                HiLog.warn(LABEL_LOG, "Service not running, skipping advertising start");
                return;
            }

            if (isAdvertising) {
                HiLog.warn(LABEL_LOG, "Already advertising, skipping");
                return;
            }

            if (!hasActiveGattService()) {
                HiLog.error(LABEL_LOG, "No active GATT service, cannot start advertising");
                return;
            }

            if (dataManager.getUploadMethod().equals("bluetooth")) {
                try {
                    // 检查advertiser是否为null
                    if (advertiser == null) {
                        HiLog.warn(LABEL_LOG, "Advertiser is null, recreating");
                        advertiser = new BleAdvertiser(this, advertiseCallback);
                        Thread.sleep(200); // 等待初始化
                    }

                    // 每次创建新的广播设置和数据
                    advertiseSettings = createAdvertiseSettings();
                    advertiseData = createAdvertiseData();

                    // 启动广播
                    advertiser.startAdvertising(advertiseSettings, advertiseData, null);
                    HiLog.info(LABEL_LOG, "advertiseData with ID: " + deviceBroadcastId);
                    isAdvertising = true;
                    HiLog.info(LABEL_LOG, "Advertising started successfully");
                } catch (Exception e) {
                    HiLog.error(LABEL_LOG, "Error starting advertising: " + e.getMessage(), e);
                }
            }
        }
    }

    // Preferences相关方法
    private Preferences getPreferences() {
        Context context = getContext();
        DatabaseHelper databaseHelper = new DatabaseHelper(context);
        String fileName = "pref";
        return databaseHelper.getPreferences(fileName);
    }

    public void storeValue(String key, String value) {
        Preferences preferences = getPreferences();
        preferences.putString(key, value);
        preferences.flush();
    }

    public String fetchValue(String key) {
        Preferences preferences = getPreferences();
        return preferences.getString(key,"");
    }

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

    @Override
    public void onBackground() {
        super.onBackground();
        HiLog.info(LABEL_LOG, "BluetoothService::onBackground");
    }

    @Override
    public void onStop() {
        try {
            HiLog.info(LABEL_LOG, "BluetoothService::onStop");

            // 先标记服务停止，防止新的任务执行
            isServiceRunning = false;

            super.onStop();

            // 停止任务
            stopPushLoop();

            // 销毁服务
            synchronized (GLOBAL_BLE_LOCK) {
                destroyGattService();
            }

            cancelBackgroundRunning();
            HiLog.info(LABEL_LOG, "BluetoothService::onStop completed, service count: " + serviceInstanceCount);
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "Error in onStop: " + e.getMessage(), e);
        }
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
        try {
            HiLog.info(LABEL_LOG, "BluetoothService::onDisconnect");

            // 先标记服务停止，防止新的任务执行
            isServiceRunning = false;

            // 停止任务
            stopPushLoop();

            // 销毁服务
            synchronized (GLOBAL_BLE_LOCK) {
                destroyGattService();
            }

            cancelBackgroundRunning();
            HiLog.info(LABEL_LOG, "BluetoothService::onDisconnect completed, service count: " + serviceInstanceCount);
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "Error in onDisconnect: " + e.getMessage(), e);
        }
    }

    // 安全获取健康数据的方法
    private String safeGetHealthInfo() {
        if (!isServiceRunning) {
            HiLog.warn(LABEL_LOG, "Service not running, skipping health data collection");
            return null;
        }

        try {
            return Utils.getHealthInfo();
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "Error getting health info: " + e.getMessage());
            return null;
        }
    }

    // 安全获取设备数据的方法
    private String safeGetDeviceInfo() {
        if (!isServiceRunning) {
            HiLog.warn(LABEL_LOG, "Service not running, skipping device data collection");
            return null;
        }

        try {
            return Utils.getDeviceInfo();
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "Error getting device info: " + e.getMessage());
            return null;
        }
    }

    private BleAdvertiseData createAdvertiseData() {
        // 每次创建新的广播数据，添加唯一设备ID
        try {
            // 创建包含唯一ID的广播数据
            return new BleAdvertiseData.Builder()
                    .addServiceUuid(SequenceUuid.uuidFromString(SERVICE_UUID.toString()))
                    .addManufacturerData(0xFFFF, deviceBroadcastId.getBytes(StandardCharsets.UTF_8)) // 添加制造商数据
                    .build();
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "Error creating advertise data: " + e.getMessage());
            // 使用简单的备用数据
            return new BleAdvertiseData.Builder()
                    .addServiceUuid(SequenceUuid.uuidFromString(SERVICE_UUID.toString()))
                    .build();
        }
    }

    private BleAdvertiseSettings createAdvertiseSettings() {
        return new BleAdvertiseSettings.Builder()
                .setConnectable(true)
                .setInterval(BleAdvertiseSettings.INTERVAL_SLOT_MIN)
                .setTxPower(BleAdvertiseSettings.TX_POWER_MAX)
                .build();
    }

    // 在类中添加这个辅助方法，用于诊断JSON格式
    private String diagnosticJson(String json) {
        if (json == null || json.isEmpty()) {
            return "Empty JSON";
        }

        // 检查基本格式
        if (!json.startsWith("{") || !json.endsWith("}")) {
            return "Invalid JSON format: must start with { and end with }";
        }

        // 检查转义字符
        int escapeCount = 0;
        for (int i = 0; i < json.length(); i++) {
            if (json.charAt(i) == '\\') {
                escapeCount++;
            }
        }

        if (escapeCount > json.length() / 10) { // 如果转义字符超过10%
            return "Too many escape characters: " + escapeCount;
        }

        // 检查JSON是否有效
        try {
            new JSONObject(json);
            return "Valid JSON";
        } catch (Exception e) {
            return "Invalid JSON: " + e.getMessage();
        }
    }

    // 在类中添加notifyServiceChanged方法
    private void notifyServiceChanged() {
        // 完全禁用Service Changed通知功能，因为会导致手机端循环重置连接
        HiLog.warn(LABEL_LOG, "Service Changed通知已被禁用，避免手机端循环重置连接问题");
        return;
        
        /*
        // 原有实现已被注释掉，因为Service Changed通知会导致手机端误认为需要重置notify
        // 添加延迟确保组件已初始化
        new Thread(() -> {
            try {
                // 等待所有组件就绪
                Thread.sleep(500);
                
                synchronized (GLOBAL_BLE_LOCK) {
                    if (peripheralDevice == null || serviceChangeChar == null || blePeripheralManager == null) {
                        HiLog.warn(LABEL_LOG, "无法发送服务变更通知：组件未就绪");
                        return;
                    }
                    
                    // 服务变更范围: 开始句柄和结束句柄
                    byte[] value = new byte[]{0x01, 0x00, (byte)0xFF, (byte)0xFF};
                    serviceChangeChar.setValue(value);
                    
                    // 发送Service Changed指示
                    boolean success = blePeripheralManager.notifyCharacteristicChanged(
                            peripheralDevice, serviceChangeChar, true);
                    
                    if (success) {
                        HiLog.info(LABEL_LOG, "服务变更通知发送成功");
                    } else {
                        HiLog.error(LABEL_LOG, "发送服务变更通知失败");
                    }
                }
            } catch (Exception e) {
                HiLog.error(LABEL_LOG, "发送服务变更通知时出错: " + e.getMessage());
            }
        }).start();
        */
    }

    // 添加setupGenericAttributeService方法实现
    private boolean setupGenericAttributeService() {
        // 完全禁用通用属性服务，避免Service Changed通知导致手机端重置连接
        HiLog.info(LABEL_LOG, "已禁用通用属性服务设置，避免Service Changed通知问题");
        return true; // 返回true表示"成功"(即成功地禁用了该功能)
        
        /*
        // 原有实现已被注释掉，因为Service Changed通知会导致手机端循环重置连接
        try {
            // 先检查是否已存在
            if (serviceChangeChar != null) {
                HiLog.info(LABEL_LOG, "通用属性服务已存在");
                return true;
            }

            // 创建Service Changed特性
            GattCharacteristic serviceChanged = new GattCharacteristic(
                    SERVICE_CHANGED_CHAR_UUID,
                    GATT_PERM,
                    PROP_INDICATE
            );

            // 添加CCCD描述符
            GattDescriptor cccd = new GattDescriptor(CCCD_UUID, GATT_PERM);
            serviceChanged.addDescriptor(cccd);

            // 创建Generic Attribute服务
            GattService gattService = new GattService(GENERIC_ATTRIBUTE_SERVICE_UUID, true);
            gattService.addCharacteristic(serviceChanged);

            // 注册服务前确保blePeripheralManager已初始化
            if (blePeripheralManager == null) {
                HiLog.error(LABEL_LOG, "无法添加通用属性服务：blePeripheralManager为空");
                return false;
            }

            // 注册服务
            boolean success = blePeripheralManager.addService(gattService);
            if (success) {
                this.serviceChangeChar = serviceChanged;
                HiLog.info(LABEL_LOG, "通用属性服务设置成功");
            } else {
                HiLog.error(LABEL_LOG, "添加通用属性服务失败");
            }

            return success;
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "设置通用属性服务时出错: " + e.getMessage());
            return false;
        }
        */
    }

    // 新增二进制数据推送方法
    private void pushBinaryPacket(byte type, String jsonData) {
        if (dataChar == null || blePeripheralManager == null || peripheralDevice == null) {
            HiLog.error(LABEL_LOG, "无法推送数据包:组件缺失");
            return;
        }

        try {
            List<BleProtocolEncoder.ProtocolPacket> packets;
            
            // 根据数据类型选择编码方法
            switch (type) {
                case BleProtocolEncoder.TYPE_HEALTH_DATA:
                    packets = BleProtocolEncoder.encodeHealthData(jsonData, mtu);
                    HiLog.info(LABEL_LOG, "编码健康数据完成,分包数:" + packets.size());
                    break;
                case BleProtocolEncoder.TYPE_DEVICE_INFO:
                    packets = BleProtocolEncoder.encodeDeviceInfo(jsonData, mtu);
                    HiLog.info(LABEL_LOG, "编码设备信息完成,分包数:" + packets.size());
                    break;
                case BleProtocolEncoder.TYPE_COMMON_EVENT:
                    packets = BleProtocolEncoder.encodeCommonEvent(jsonData, mtu);
                    HiLog.info(LABEL_LOG, "编码公共事件完成,分包数:" + packets.size());
                    break;
                case BleProtocolEncoder.TYPE_HEARTBEAT:
                    packets = BleProtocolEncoder.encodeHeartbeat(mtu);
                    HiLog.info(LABEL_LOG, "编码心跳包完成,分包数:" + packets.size());
                    break;
                default:
                    HiLog.error(LABEL_LOG, "不支持的数据类型:" + type);
                    return;
            }

            if (packets.isEmpty()) {
                HiLog.error(LABEL_LOG, "数据编码失败");
                return;
            }

            // 将协议包加入发送队列
            String packetId = UUID.randomUUID().toString();
            for (int i = 0; i < packets.size(); i++) {
                BleProtocolEncoder.ProtocolPacket packet = packets.get(i);
                ChunkData chunk = new ChunkData(packetId, packets.size(), i, packet.data, true);
                pushQueue.offer(chunk);
                HiLog.debug(LABEL_LOG, String.format("二进制包入队:类型=%d,分包=%d/%d,大小=%d字节",
                        type, i + 1, packets.size(), packet.data.length));
            }
        } catch (Exception e) {
            HiLog.error(LABEL_LOG, "推送二进制数据包失败:" + e.getMessage(), e);
        }
    }

    // 新增心跳包发送方法
    private void sendHeartbeat() {//发送心跳包
        if (isConnected && peripheralDevice != null && dataManager.getUseBinaryProtocol()) {
            pushBinaryPacket(BleProtocolEncoder.TYPE_HEARTBEAT, null);
            HiLog.debug(LABEL_LOG, "发送心跳包");
        }
    }

}
