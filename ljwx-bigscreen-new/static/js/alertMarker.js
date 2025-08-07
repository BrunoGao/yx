// 告警标记管理类
class AlertMarkerManager {
    constructor(map) {
        this.map = map;
        this.markers = new Map(); // 存储所有告警标记
        this.initStyles();
    }

    // 初始化样式
    initStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .alert-marker {
                position: absolute;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                pointer-events: none;
                transform: translate(-50%, -50%);
            }

            .alert-marker::before {
                content: '';
                position: absolute;
                width: 100%;
                height: 100%;
                border-radius: 50%;
            }

            .alert-critical {
                background-color: rgba(255, 0, 0, 0.8);
                animation: pulse-critical 2s infinite;
            }

            .alert-high {
                background-color: rgba(255, 165, 0, 0.8);
                animation: pulse-high 2s infinite;
            }

            .alert-medium {
                background-color: rgba(255, 255, 0, 0.8);
                animation: pulse-medium 2s infinite;
            }

            .alert-low {
                background-color: rgba(0, 255, 0, 0.8);
                animation: pulse-low 2s infinite;
            }

            @keyframes pulse-critical {
                0% {
                    transform: translate(-50%, -50%) scale(0.95);
                    box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7);
                }
                70% {
                    transform: translate(-50%, -50%) scale(1);
                    box-shadow: 0 0 0 20px rgba(255, 0, 0, 0);
                }
                100% {
                    transform: translate(-50%, -50%) scale(0.95);
                    box-shadow: 0 0 0 0 rgba(255, 0, 0, 0);
                }
            }

            @keyframes pulse-high {
                0% {
                    transform: translate(-50%, -50%) scale(0.95);
                    box-shadow: 0 0 0 0 rgba(255, 165, 0, 0.7);
                }
                70% {
                    transform: translate(-50%, -50%) scale(1);
                    box-shadow: 0 0 0 15px rgba(255, 165, 0, 0);
                }
                100% {
                    transform: translate(-50%, -50%) scale(0.95);
                    box-shadow: 0 0 0 0 rgba(255, 165, 0, 0);
                }
            }

            @keyframes pulse-medium {
                0% {
                    transform: translate(-50%, -50%) scale(0.95);
                    box-shadow: 0 0 0 0 rgba(255, 255, 0, 0.7);
                }
                70% {
                    transform: translate(-50%, -50%) scale(1);
                    box-shadow: 0 0 0 10px rgba(255, 255, 0, 0);
                }
                100% {
                    transform: translate(-50%, -50%) scale(0.95);
                    box-shadow: 0 0 0 0 rgba(255, 255, 0, 0);
                }
            }

            @keyframes pulse-low {
                0% {
                    transform: translate(-50%, -50%) scale(0.95);
                    box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);
                }
                70% {
                    transform: translate(-50%, -50%) scale(1);
                    box-shadow: 0 0 0 5px rgba(0, 255, 0, 0);
                }
                100% {
                    transform: translate(-50%, -50%) scale(0.95);
                    box-shadow: 0 0 0 0 rgba(0, 255, 0, 0);
                }
            }
        `;
        document.head.appendChild(style);
    }

    // 添加告警标记
    addAlertMarker(alert) {
        const { alert_id, latitude, longitude, severity_level, alert_type, alert_desc } = alert;
        
        // 如果已存在该告警，先移除
        if (this.markers.has(alert_id)) {
            this.removeAlertMarker(alert_id);
        }

        // 创建标记元素
        const marker = document.createElement('div');
        marker.className = `alert-marker alert-${severity_level}`;
        marker.setAttribute('data-alert-id', alert_id);
        
        // 添加提示信息
        marker.title = `${alert_type}: ${alert_desc}`;

        // 计算标记位置
        const position = [parseFloat(longitude), parseFloat(latitude)];
        const pixel = this.map.lngLatToContainer(position);
        
        // 设置标记位置
        marker.style.left = pixel.x + 'px';
        marker.style.top = pixel.y + 'px';
        
        // 将标记添加到地图容器
        this.map.getContainer().appendChild(marker);
        
        // 存储标记信息
        this.markers.set(alert_id, {
            element: marker,
            position: position,
            data: alert
        });
    }

    // 移除告警标记
    removeAlertMarker(alertId) {
        const marker = this.markers.get(alertId);
        if (marker) {
            marker.element.remove();
            this.markers.delete(alertId);
        }
    }

    // 更新所有标记位置（地图移动时调用）
    updateMarkerPositions() {
        this.markers.forEach((marker, alertId) => {
            const pixel = this.map.lngLatToContainer(marker.position);
            marker.element.style.left = pixel.x + 'px';
            marker.element.style.top = pixel.y + 'px';
        });
    }

    // 更新告警数据
    updateAlerts(alerts) {
        // 记录新的告警ID
        const newAlertIds = new Set(alerts.map(alert => alert.alert_id));
        
        // 移除已不存在的告警
        this.markers.forEach((marker, alertId) => {
            if (!newAlertIds.has(alertId)) {
                this.removeAlertMarker(alertId);
            }
        });
        
        // 添加或更新告警
        alerts.forEach(alert => {
            this.addAlertMarker(alert);
        });
    }

    // 清除所有标记
    clearAllMarkers() {
        this.markers.forEach((marker, alertId) => {
            this.removeAlertMarker(alertId);
        });
    }
} 