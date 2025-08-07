// 内网离线地图解决方案
// 支持无网络环境下的地图功能

class OfflineMapManager {
    constructor() {
        this.isOnline = false; // 网络状态
        this.fallbackMap = null; // 离线替代地图
        this.mapContainer = null; // 地图容器
        this.dataPoints = []; // 数据点
        this.init();
    }

    // 检测网络状态
    checkNetworkStatus() {
        return new Promise((resolve) => {
            // 尝试加载高德地图API
            const testImg = new Image();
            testImg.onload = () => {
                this.isOnline = true;
                resolve(true);
            };
            testImg.onerror = () => {
                this.isOnline = false;
                resolve(false);
            };
            testImg.src = 'https://webapi.amap.com/favicon.ico?' + Date.now();
            
            // 超时处理
            setTimeout(() => {
                this.isOnline = false;
                resolve(false);
            }, 5000);
        });
    }

    // 初始化地图
    async init() {
        const networkStatus = await this.checkNetworkStatus();
        console.log(`🌐 网络状态: ${networkStatus ? '在线' : '离线'}`);
        
        if (networkStatus) {
            this.initOnlineMap();
        } else {
            this.initOfflineMap();
        }
    }

    // 在线地图初始化（原有方案）
    initOnlineMap() {
        console.log('🗺️ 加载在线地图');
        // 保持原有的高德地图实现
        if (typeof initializeMap === 'function') {
            initializeMap(window.currentDeptId, window.currentUserId);
        }
    }

    // 离线地图初始化
    initOfflineMap() {
        console.log('📱 启用离线地图模式');
        const container = document.getElementById('map-container');
        if (!container) return;

        // 清空容器
        container.innerHTML = '';
        
        // 创建离线地图容器
        const offlineContainer = document.createElement('div');
        offlineContainer.style.cssText = `
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        `;

        // 添加状态提示
        const statusDiv = document.createElement('div');
        statusDiv.innerHTML = `
            <div style="color: #4CAF50; font-size: 16px; margin-bottom: 20px; text-align: center;">
                <i class="fas fa-wifi" style="color: #f44336; margin-right: 8px;"></i>
                离线模式 - 使用本地数据展示
            </div>
        `;
        offlineContainer.appendChild(statusDiv);

        // 创建SVG地图
        this.createSVGMap(offlineContainer);
        
        container.appendChild(offlineContainer);
        
        // 加载离线数据
        this.loadOfflineData();
    }

    // 创建SVG矢量地图
    createSVGMap(container) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '80%');
        svg.setAttribute('viewBox', '0 0 800 600');
        svg.style.border = '1px solid #333';
        svg.style.backgroundColor = '#1e3a5f';

        // 绘制区域轮廓
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M100,100 L700,100 L700,500 L100,500 Z M200,200 L300,150 L500,180 L600,200 L500,300 L400,350 L300,300 L200,250 Z');
        path.setAttribute('fill', '#2c5aa0');
        path.setAttribute('stroke', '#4CAF50');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('opacity', '0.3');
        svg.appendChild(path);

        // 添加网格线
        for (let i = 100; i <= 700; i += 100) {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', i);
            line.setAttribute('y1', '100');
            line.setAttribute('x2', i);
            line.setAttribute('y2', '500');
            line.setAttribute('stroke', '#333');
            line.setAttribute('stroke-width', '0.5');
            line.setAttribute('opacity', '0.3');
            svg.appendChild(line);
        }

        for (let i = 100; i <= 500; i += 50) {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', '100');
            line.setAttribute('y1', i);
            line.setAttribute('x2', '700');
            line.setAttribute('y2', i);
            line.setAttribute('stroke', '#333');
            line.setAttribute('stroke-width', '0.5');
            line.setAttribute('opacity', '0.3');
            svg.appendChild(line);
        }

        container.appendChild(svg);
        this.mapContainer = svg;
    }

    // 加载离线数据并显示点位
    async loadOfflineData() {
        try {
            // 模拟数据点（实际应从本地存储或内网API获取）
            const mockData = [
                { id: 1, x: 250, y: 200, type: 'critical', name: '设备001', status: '异常' },
                { id: 2, x: 350, y: 250, type: 'high', name: '设备002', status: '告警' },
                { id: 3, x: 450, y: 300, type: 'medium', name: '设备003', status: '注意' },
                { id: 4, x: 550, y: 180, type: 'normal', name: '设备004', status: '正常' },
                { id: 5, x: 300, y: 350, type: 'normal', name: '设备005', status: '正常' }
            ];

            // 如果有真实数据API，使用真实数据
            const realData = await this.fetchLocalData();
            const dataPoints = realData.length > 0 ? realData : mockData;

            this.renderDataPoints(dataPoints);
        } catch (error) {
            console.warn('加载离线数据失败，使用默认数据', error);
        }
    }

    // 获取本地数据
    async fetchLocalData() {
        try {
            const deptId = window.currentDeptId || 'default';
            const userId = window.currentUserId || 'default';
            
            // 尝试从内网API获取数据
            const responses = await Promise.allSettled([
                fetch(`./generateAlertJson?customerId=${deptId}&userId=${userId}&severityLevel=critical`),
                fetch(`./generateAlertJson?customerId=${deptId}&userId=${userId}&severityLevel=high`),
                fetch(`./generateAlertJson?customerId=${deptId}&userId=${userId}&severityLevel=medium`),
                fetch(`./generateHealthJson?customerId=${deptId}&userId=${userId}`)
            ]);

            const data = [];
            for (let i = 0; i < responses.length; i++) {
                if (responses[i].status === 'fulfilled' && responses[i].value.ok) {
                    const json = await responses[i].value.json();
                    if (json.features) {
                        json.features.forEach(feature => {
                            data.push({
                                id: feature.properties.id || Math.random(),
                                x: 100 + Math.random() * 600, // 随机位置
                                y: 100 + Math.random() * 400,
                                type: ['critical', 'high', 'medium', 'normal'][i],
                                name: feature.properties.name || `设备${feature.properties.id}`,
                                status: feature.properties.status || '未知'
                            });
                        });
                    }
                }
            }
            return data;
        } catch (error) {
            console.warn('获取本地数据失败:', error);
            return [];
        }
    }

    // 渲染数据点
    renderDataPoints(dataPoints) {
        if (!this.mapContainer) return;

        const colors = {
            critical: '#ff4444',
            high: '#ff8800',
            medium: '#ffaa00',
            normal: '#44ff44'
        };

        dataPoints.forEach(point => {
            // 创建点位圆圈
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', point.x);
            circle.setAttribute('cy', point.y);
            circle.setAttribute('r', '8');
            circle.setAttribute('fill', colors[point.type] || '#44ff44');
            circle.setAttribute('stroke', '#fff');
            circle.setAttribute('stroke-width', '2');
            circle.setAttribute('opacity', '0.8');
            circle.style.cursor = 'pointer';

            // 添加动画效果
            const animate = document.createElementNS('http://www.w3.org/2000/svg', 'animate');
            animate.setAttribute('attributeName', 'r');
            animate.setAttribute('values', '8;12;8');
            animate.setAttribute('dur', '2s');
            animate.setAttribute('repeatCount', 'indefinite');
            circle.appendChild(animate);

            // 添加点击事件
            circle.addEventListener('click', () => {
                this.showPointInfo(point);
            });

            this.mapContainer.appendChild(circle);

            // 添加文字标签
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', point.x);
            text.setAttribute('y', point.y - 15);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', '#fff');
            text.setAttribute('font-size', '12');
            text.setAttribute('font-family', 'Arial, sans-serif');
            text.textContent = point.name;
            this.mapContainer.appendChild(text);
        });
    }

    // 显示点位信息
    showPointInfo(point) {
        // 创建信息弹窗
        const infoWindow = document.createElement('div');
        infoWindow.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #4CAF50;
            z-index: 10000;
            min-width: 200px;
        `;

        infoWindow.innerHTML = `
            <div style="text-align: center;">
                <h3 style="margin: 0 0 10px 0; color: #4CAF50;">${point.name}</h3>
                <p style="margin: 5px 0;"><strong>状态:</strong> ${point.status}</p>
                <p style="margin: 5px 0;"><strong>类型:</strong> ${point.type}</p>
                <p style="margin: 5px 0;"><strong>ID:</strong> ${point.id}</p>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="margin-top: 15px; padding: 5px 15px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    关闭
                </button>
            </div>
        `;

        document.body.appendChild(infoWindow);

        // 3秒后自动关闭
        setTimeout(() => {
            if (infoWindow.parentElement) {
                infoWindow.remove();
            }
        }, 5000);
    }
}

// 网络状态变化监听
window.addEventListener('online', () => {
    console.log('🌐 网络已连接，可以切换到在线模式');
    if (confirm('检测到网络连接，是否切换到在线地图模式？')) {
        location.reload();
    }
});

window.addEventListener('offline', () => {
    console.log('📱 网络已断开，建议使用离线模式');
});

// 全局初始化函数
function initMapWithFallback() {
    console.log('🚀 启动智能地图初始化');
    window.offlineMapManager = new OfflineMapManager();
}

// 导出到全局
window.OfflineMapManager = OfflineMapManager;
window.initMapWithFallback = initMapWithFallback; 