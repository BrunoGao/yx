/**
 * 智能健康大屏 - 3D地图模块
 * 作者: AI助手
 * 版本: 1.0.0
 * 功能: 3D地图展示健康点、告警点，支持实时数据更新
 */

// ============ 全局变量定义 ============
let map, loca, scatterLayer, alertLayer, mapCenter, mapBounds;
let mapData = { healthPoints: [], alertPoints: [] };
let currentDeptId = null, currentUserId = null;
let mapReady = false;

// ============ 地图配置 ============
const mapStyle = 'amap://styles/blue';
const mapConfig = {
    container: 'map-container',
    style: mapStyle,
    center: [116.397428, 39.90923], // 默认北京
    zoom: 10,
    pitch: 60, // 3D倾斜角度
    rotation: 0,
    viewMode: '3D',
    expandZoomRange: true,
    zooms: [3, 20],
    features: ['bg', 'road', 'building'],
    mapStyle: 'amap://styles/darkblue'
};

// ============ 图层样式配置 ============
const layerStyles = {
    health: {
        unit: 'meter',
        size: [20, 30],
        animate: true,
        opacity: [0.6, 1],
        duration: 3000
    },
    alert: {
        unit: 'meter', 
        size: [25, 35],
        animate: true,
        opacity: [0.8, 1],
        duration: 2000
    }
};

// ============ 信息框HTML模板 ============
const infoWindowTemplates = {
    health: (data) => `
        <div class="health-info-window">
            <div class="info-header">
                <div class="user-avatar">👤</div>
                <div class="user-title">
                    <h3>${data.userName || '未知用户'}</h3>
                    <p>${data.deptName || '未知部门'}</p>
                </div>
            </div>
            <div class="info-content">
                <div class="health-metrics">
                    <div class="metric-item">
                        <span class="label">心率:</span>
                        <span class="value ${getHealthStatus(data.heartRate)}">${data.heartRate || '--'} BPM</span>
                    </div>
                    <div class="metric-item">
                        <span class="label">血氧:</span>
                        <span class="value ${getHealthStatus(data.bloodOxygen)}">${data.bloodOxygen || '--'}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="label">血压:</span>
                        <span class="value">${data.pressureHigh || '--'}/${data.pressureLow || '--'} mmHg</span>
                    </div>
                    <div class="metric-item">
                        <span class="label">体温:</span>
                        <span class="value">${data.temperature || '--'}°C</span>
                    </div>
                </div>
                <div class="action-buttons">
                    <button class="btn-primary" onclick="openPersonalScreen('${data.deviceSn}')">
                        🏥 查看健康大屏
                    </button>
                </div>
            </div>
        </div>
    `,
    alert: (data) => `
        <div class="alert-info-window">
            <div class="info-header alert">
                <div class="alert-icon">⚠️</div>
                <div class="alert-title">
                    <h3>告警信息</h3>
                    <p class="alert-level level-${data.alertLevel}">${getAlertLevelText(data.alertLevel)}</p>
                </div>
            </div>
            <div class="info-content">
                <div class="alert-details">
                    <div class="detail-item">
                        <span class="label">员工:</span>
                        <span class="value">${data.userName || '未知'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">部门:</span>
                        <span class="value">${data.deptName || '未知'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">告警类型:</span>
                        <span class="value">${data.alertType || '未知'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">告警时间:</span>
                        <span class="value">${formatTime(data.alertTime)}</span>
                    </div>
                </div>
                <div class="action-buttons">
                    <button class="btn-danger" onclick="openPersonalScreen('${data.deviceSn}')">
                        📊 查看健康详情
                    </button>
                </div>
            </div>
        </div>
    `
};

// ============ 主要功能函数 ============

/**
 * 地图初始化函数
 * @param {string} deptId - 部门ID
 * @param {string} userId - 用户ID
 */
function initializeMap(deptId, userId) {
    console.log('🗺️ 初始化3D地图模块...');
    currentDeptId = deptId;
    currentUserId = userId;

    try {
        // 创建地图实例
        map = new AMap.Map('map-container', mapConfig);
        
        // 地图加载完成事件
        map.on('complete', () => {
            console.log('✅ 地图加载完成，创建Loca场景...');
            
            // 创建Loca场景
            loca = new Loca.Container({ map });
            
            // 创建图层
            createMapLayers();
            
            // 标记地图准备就绪
            mapReady = true;
            console.log('✅ 地图模块初始化完成');
            
            // 首次加载数据
            updateMapData();
        });

        // 地图错误处理
        map.on('error', (error) => {
            console.error('❌ 地图加载错误:', error);
        });

    } catch (error) {
        console.error('❌ 地图初始化失败:', error);
    }
}

/**
 * 创建地图图层
 */
function createMapLayers() {
    try {
        // 健康点图层
        scatterLayer = new Loca.ScatterLayer({
            map: map,
            loca: loca,
            zIndex: 10,
            opacity: 1,
            visible: true,
            zooms: [3, 20]
        });

        // 告警点图层
        alertLayer = new Loca.ScatterLayer({
            map: map,
            loca: loca,
            zIndex: 15,
            opacity: 1,
            visible: true,
            zooms: [3, 20]
        });

        console.log('✅ 地图图层创建成功');
    } catch (error) {
        console.error('❌ 图层创建失败:', error);
    }
}

/**
 * 更新地图数据
 */
function updateMapData() {
    if (!mapReady || !window.lastTotalInfo) return;

    console.log('🔄 更新地图数据...');
    
    try {
        // 解析健康数据
        const healthPoints = parseHealthData(window.lastTotalInfo.health_data);
        const alertPoints = parseAlertData(window.lastTotalInfo.alert_info);

        // 过滤数据
        const filteredHealthPoints = filterDataByDeptUser(healthPoints, currentDeptId, currentUserId);
        const filteredAlertPoints = filterDataByDeptUser(alertPoints, currentDeptId, currentUserId);

        console.log(`📊 健康点: ${filteredHealthPoints.length}, 告警点: ${filteredAlertPoints.length}`);

        // 更新图层数据
        updateHealthLayer(filteredHealthPoints);
        updateAlertLayer(filteredAlertPoints);

        // 调整地图中心
        adjustMapCenter(filteredAlertPoints, filteredHealthPoints);

        // 存储数据供其他函数使用
        mapData = {
            healthPoints: filteredHealthPoints,
            alertPoints: filteredAlertPoints
        };

    } catch (error) {
        console.error('❌ 地图数据更新失败:', error);
    }
}

/**
 * 解析健康数据
 * @param {Object} healthData - 健康数据
 * @returns {Array} 解析后的健康点数组
 */
function parseHealthData(healthData) {
    if (!healthData || !healthData.data) return [];
    
    return healthData.data.filter(item => 
        item.longitude && item.latitude && 
        !isNaN(parseFloat(item.longitude)) && !isNaN(parseFloat(item.latitude))
    ).map(item => ({
        coordinates: [parseFloat(item.longitude), parseFloat(item.latitude)],
        userId: item.user_id,
        userName: item.user_name || '未知用户',
        deptName: item.dept_name || '未知部门',
        deviceSn: item.device_sn,
        heartRate: item.heart_rate,
        bloodOxygen: item.blood_oxygen,
        pressureHigh: item.pressure_high,
        pressureLow: item.pressure_low,
        temperature: item.temperature,
        healthScore: item.health_score || 0,
        type: 'health'
    }));
}

/**
 * 解析告警数据
 * @param {Object} alertData - 告警数据
 * @returns {Array} 解析后的告警点数组
 */
function parseAlertData(alertData) {
    if (!alertData || !alertData.data) return [];
    
    return alertData.data.filter(item => 
        item.longitude && item.latitude && 
        !isNaN(parseFloat(item.longitude)) && !isNaN(parseFloat(item.latitude))
    ).map(item => ({
        coordinates: [parseFloat(item.longitude), parseFloat(item.latitude)],
        userId: item.user_id,
        userName: item.user_name || '未知用户',
        deptName: item.dept_name || '未知部门',
        deviceSn: item.device_sn,
        alertType: item.alert_type,
        alertLevel: item.alert_level || 1,
        alertTime: item.alert_time,
        alertMessage: item.alert_message,
        type: 'alert'
    }));
}

/**
 * 数据过滤
 * @param {Array} data - 数据数组
 * @param {string} deptId - 部门ID
 * @param {string} userId - 用户ID
 * @returns {Array} 过滤后的数据
 */
function filterDataByDeptUser(data, deptId, userId) {
    if (userId && userId !== '-1') {
        return data.filter(item => item.userId == userId);
    }
    if (deptId && deptId !== '-1') {
        return data.filter(item => item.deptId == deptId);
    }
    return data;
}

/**
 * 更新健康点图层
 * @param {Array} healthPoints - 健康点数据
 */
function updateHealthLayer(healthPoints) {
    if (!scatterLayer || !healthPoints.length) return;

    // 构建GeoJSON数据
    const geoData = {
        type: 'FeatureCollection',
        features: healthPoints.map(point => ({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: point.coordinates
            },
            properties: { ...point }
        }))
    };

    // 设置数据源
    scatterLayer.setData(geoData, {
        lnglat: 'coordinates'
    });

    // 设置样式
    scatterLayer.setStyle({
        unit: 'meter',
        size: [15, 25],
        color: (feature) => getHealthPointColor(feature.properties.healthScore),
        opacity: 0.8,
        borderWidth: 2,
        borderColor: '#00e4ff'
    });

    // 添加标签
    scatterLayer.setLabels({
        enable: true,
        field: (feature) => `${feature.properties.deptName || ''}\n${feature.properties.userName || ''}`,
        style: {
            fontSize: 11,
            color: '#ffffff',
            strokeColor: '#001529',
            strokeWidth: 2,
            offset: [0, -40],
            backgroundColor: 'rgba(0, 21, 41, 0.7)',
            borderRadius: 4,
            padding: [4, 8]
        }
    });

    // 添加点击事件
    scatterLayer.on('click', (event) => {
        const properties = event.feature.properties;
        showInfoWindow(event.lnglat, properties, 'health');
    });

    console.log(`✅ 健康点图层更新完成: ${healthPoints.length}个点`);
}

/**
 * 更新告警点图层
 * @param {Array} alertPoints - 告警点数据
 */
function updateAlertLayer(alertPoints) {
    if (!alertLayer || !alertPoints.length) return;

    // 构建GeoJSON数据
    const geoData = {
        type: 'FeatureCollection',
        features: alertPoints.map(point => ({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: point.coordinates
            },
            properties: { ...point }
        }))
    };

    // 设置数据源
    alertLayer.setData(geoData, {
        lnglat: 'coordinates'
    });

    // 设置样式
    alertLayer.setStyle({
        unit: 'meter',
        size: [20, 30],
        color: (feature) => getAlertPointColor(feature.properties.alertLevel),
        opacity: 0.9,
        borderWidth: 3,
        borderColor: '#ff4d4f',
        animate: true,
        duration: 2000
    });

    // 添加标签
    alertLayer.setLabels({
        enable: true,
        field: (feature) => `⚠️ ${feature.properties.deptName || ''}\n${feature.properties.userName || ''}`,
        style: {
            fontSize: 11,
            color: '#ff4d4f',
            strokeColor: '#001529',
            strokeWidth: 2,
            offset: [0, -45],
            backgroundColor: 'rgba(255, 77, 79, 0.2)',
            borderRadius: 4,
            padding: [4, 8]
        }
    });

    // 添加点击事件
    alertLayer.on('click', (event) => {
        const properties = event.feature.properties;
        showInfoWindow(event.lnglat, properties, 'alert');
    });

    console.log(`✅ 告警点图层更新完成: ${alertPoints.length}个点`);
}

/**
 * 调整地图中心
 * @param {Array} alertPoints - 告警点数据
 * @param {Array} healthPoints - 健康点数据
 */
function adjustMapCenter(alertPoints, healthPoints) {
    let centerCoords = null;

    // 优先以最高优先级告警点为中心
    if (alertPoints.length > 0) {
        const highestAlert = alertPoints.reduce((prev, current) => 
            (current.alertLevel > prev.alertLevel) ? current : prev
        );
        centerCoords = highestAlert.coordinates;
        console.log('🎯 以最高优先级告警点为地图中心');
    } 
    // 无告警时以第一个健康点为中心
    else if (healthPoints.length > 0) {
        centerCoords = healthPoints[0].coordinates;
        console.log('🎯 以第一个健康点为地图中心');
    }

    // 设置地图中心和缩放级别
    if (centerCoords && map) {
        map.setCenter(centerCoords);
        
        // 根据点的数量调整缩放级别
        const totalPoints = alertPoints.length + healthPoints.length;
        let zoom = 12;
        if (totalPoints > 100) zoom = 10;
        if (totalPoints > 500) zoom = 9;
        if (totalPoints > 1000) zoom = 8;
        
        map.setZoom(zoom);
    }
}

/**
 * 显示信息窗口
 * @param {Array} position - 坐标位置
 * @param {Object} data - 数据对象
 * @param {string} type - 类型(health/alert)
 */
function showInfoWindow(position, data, type) {
    // 移除现有信息窗口
    if (window.currentInfoWindow) {
        window.currentInfoWindow.close();
    }

    // 创建新的信息窗口
    const infoWindow = new AMap.InfoWindow({
        content: infoWindowTemplates[type](data),
        offset: new AMap.Pixel(0, -30),
        closeWhenClickMap: true
    });

    // 显示信息窗口
    infoWindow.open(map, position);
    window.currentInfoWindow = infoWindow;
}

// ============ 工具函数 ============

/**
 * 获取健康点颜色
 * @param {number} score - 健康评分
 * @returns {string} 颜色值
 */
function getHealthPointColor(score) {
    if (score >= 80) return '#52c41a'; // 绿色-健康
    if (score >= 60) return '#faad14'; // 黄色-注意
    return '#ff4d4f'; // 红色-异常
}

/**
 * 获取告警点颜色
 * @param {number} level - 告警级别
 * @returns {string} 颜色值
 */
function getAlertPointColor(level) {
    switch(level) {
        case 3: return '#ff1744'; // 高危红色
        case 2: return '#ff9800'; // 中危橙色
        case 1: return '#ffc107'; // 低危黄色
        default: return '#ff4d4f';
    }
}

/**
 * 获取健康状态样式类
 * @param {number} value - 健康指标值
 * @returns {string} CSS类名
 */
function getHealthStatus(value) {
    if (!value) return '';
    return 'normal'; // 简化处理
}

/**
 * 获取告警级别文本
 * @param {number} level - 告警级别
 * @returns {string} 级别文本
 */
function getAlertLevelText(level) {
    switch(level) {
        case 3: return '高危告警';
        case 2: return '中危告警';
        case 1: return '低危告警';
        default: return '未知级别';
    }
}

/**
 * 格式化时间
 * @param {string} timeStr - 时间字符串
 * @returns {string} 格式化后的时间
 */
function formatTime(timeStr) {
    if (!timeStr) return '未知时间';
    return new Date(timeStr).toLocaleString();
}

/**
 * 打开个人健康大屏
 * @param {string} deviceSn - 设备序列号
 */
function openPersonalScreen(deviceSn) {
    if (deviceSn) {
        window.open(`/personal?deviceSn=${deviceSn}`, '_blank');
    }
}

/**
 * 地图数据刷新 - 每5-10秒调用一次
 */
function refreshMapData() {
    if (mapReady) {
        updateMapData();
    }
}

// ============ 样式注入 ============
const mapStyleCSS = `
<style>
#map-container {
    width: 100%;
    height: 100%;
    border-radius: 4px;
    overflow: hidden;
    position: relative;
}

.health-info-window, .alert-info-window {
    background: rgba(0, 21, 41, 0.95);
    border: 1px solid rgba(0, 228, 255, 0.3);
    border-radius: 8px;
    color: #fff;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(10px);
    min-width: 280px;
    max-width: 350px;
}

.info-header {
    display: flex;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid rgba(0, 228, 255, 0.2);
}

.info-header.alert {
    border-bottom-color: rgba(255, 77, 79, 0.3);
}

.user-avatar, .alert-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(0, 228, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin-right: 12px;
}

.alert-icon {
    background: rgba(255, 77, 79, 0.2);
}

.user-title h3, .alert-title h3 {
    margin: 0;
    font-size: 16px;
    color: #00e4ff;
}

.user-title p, .alert-title p {
    margin: 2px 0 0 0;
    font-size: 12px;
    color: #8c8c8c;
}

.alert-level {
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: bold;
}

.level-1 { background: rgba(255, 193, 7, 0.3); color: #ffc107; }
.level-2 { background: rgba(255, 152, 0, 0.3); color: #ff9800; }
.level-3 { background: rgba(255, 23, 68, 0.3); color: #ff1744; }

.info-content {
    padding: 15px;
}

.health-metrics, .alert-details {
    margin-bottom: 15px;
}

.metric-item, .detail-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    padding: 4px 0;
}

.metric-item .label, .detail-item .label {
    color: #8c8c8c;
    font-size: 13px;
}

.metric-item .value, .detail-item .value {
    color: #fff;
    font-size: 13px;
    font-weight: 500;
}

.value.normal { color: #52c41a; }
.value.warning { color: #faad14; }
.value.danger { color: #ff4d4f; }

.action-buttons {
    display: flex;
    gap: 8px;
}

.btn-primary, .btn-danger {
    flex: 1;
    padding: 8px 12px;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}

.btn-primary {
    background: rgba(0, 228, 255, 0.2);
    color: #00e4ff;
    border: 1px solid rgba(0, 228, 255, 0.3);
}

.btn-primary:hover {
    background: rgba(0, 228, 255, 0.3);
}

.btn-danger {
    background: rgba(255, 77, 79, 0.2);
    color: #ff4d4f;
    border: 1px solid rgba(255, 77, 79, 0.3);
}

.btn-danger:hover {
    background: rgba(255, 77, 79, 0.3);
}
</style>
`;

// 将样式注入到页面
if (typeof document !== 'undefined') {
    document.head.insertAdjacentHTML('beforeend', mapStyleCSS);
}

// ============ 导出函数 ============
// 导出主要函数供外部调用
if (typeof window !== 'undefined') {
    window.initializeMap = initializeMap;
    window.updateMapData = updateMapData; 
    window.refreshMapData = refreshMapData;
    window.openPersonalScreen = openPersonalScreen;
}

console.log('✅ 3D地图模块加载完成 v1.0.0'); 