/**
 * 地图增强功能 - 员工名字标签+美化信息框+个人大屏链接
 */

// 等待地图初始化完成后应用补丁
setTimeout(() => {
    // 备份原始函数
    window.originalShowCustomMapInfo = window.showCustomMapInfo;
    window.originalUpdateMapData = window.updateMapData;
    
    // 重写showCustomMapInfo函数 - 美化信息框+个人大屏链接
    window.showCustomMapInfo = function(f) {
        removeCustomMapInfo();
        const d = f.properties;
        const get = (...k) => k.map(x => d[x]).find(x => x !== undefined && x !== null && x !== '') || '-';
        const isAlert = !!(get('alert_id','alertId') && get('alert_type','alertType') && d.type !== 'health');
        const avatarUrl = d.avatar || '/static/images/avatar-tech.svg';
        const div = document.createElement('div');
        div.className = 'custom-map-info';
        div.style.cssText = 'position:absolute;z-index:9999;min-width:400px;max-width:460px;background:rgba(10,24,48,0.98);border:2px solid #00e4ff;border-radius:18px;box-shadow:0 0 32px rgba(0,228,255,0.5);padding:26px 32px 22px 32px;color:#fff;top:120px;left:50%;transform:translateX(-50%);font-size:15px;font-family:"Microsoft YaHei",Roboto,Arial,sans-serif;backdrop-filter:blur(8px);';
        
        if (!isAlert) { // 健康点美化版本
            const deviceSn = get('device_sn','deviceSn');
            div.innerHTML = `
                <div style="display:flex;align-items:center;gap:22px;margin-bottom:20px;">
                    <img src="${avatarUrl}" style="width:68px;height:68px;border-radius:50%;border:3px solid #00e4ff;box-shadow:0 0 18px rgba(0,228,255,0.7);object-fit:cover;background:#001529;">
                    <div style="flex:1;">
                        <div style="font-size:20px;font-weight:700;letter-spacing:1px;color:#00e4ff;margin-bottom:8px;">${get('dept_name','deptName')}</div>
                        <div style="font-size:18px;color:#ffffff;font-weight:600;">${get('user_name','userName')}</div>
                        <div style="font-size:13px;color:#7ecfff;margin-top:6px;">设备编号: ${deviceSn}</div>
                    </div>
                </div>
                
                <div style="background:rgba(0,228,255,0.08);border:1px solid rgba(0,228,255,0.25);border-radius:12px;padding:18px;margin-bottom:18px;">
                    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:15px;margin-bottom:12px;">
                        <div><span style="color:#7ecfff;font-size:14px;">心率：</span><span style="color:#fff;font-weight:600;font-size:16px;">${get('heartRate','heart_rate')} <span style="color:#bbb;font-size:12px;">bpm</span></span></div>
                        <div><span style="color:#7ecfff;font-size:14px;">血氧：</span><span style="color:#fff;font-weight:600;font-size:16px;">${get('bloodOxygen','blood_oxygen')} <span style="color:#bbb;font-size:12px;">%</span></span></div>
                        <div><span style="color:#7ecfff;font-size:14px;">血压：</span><span style="color:#fff;font-weight:600;font-size:16px;">${get('pressureHigh','pressure_high')}/${get('pressureLow','pressure_low')} <span style="color:#bbb;font-size:12px;">mmHg</span></span></div>
                        <div><span style="color:#7ecfff;font-size:14px;">体温：</span><span style="color:#fff;font-weight:600;font-size:16px;">${get('temperature','temp')} <span style="color:#bbb;font-size:12px;">℃</span></span></div>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
                        <div><span style="color:#7ecfff;font-size:13px;">步数：</span><span style="color:#fff;font-weight:500;">${get('step','steps')}</span></div>
                        <div><span style="color:#7ecfff;font-size:13px;">距离：</span><span style="color:#fff;font-weight:500;">${get('distance','distance')}m</span></div>
                        <div><span style="color:#7ecfff;font-size:13px;">卡路里：</span><span style="color:#fff;font-weight:500;">${get('calorie','calories')}</span></div>
                    </div>
                </div>
                
                <div style="margin-bottom:16px;">
                    <div style="color:#7ecfff;font-size:14px;margin-bottom:8px;">位置信息：</div>
                    <div id="locationInfo" style="color:#fff;font-size:14px;padding:12px;background:rgba(255,255,255,0.06);border-radius:8px;border:1px solid rgba(255,255,255,0.1);">正在获取...</div>
                </div>
                
                <div style="margin-bottom:18px;">
                    <span style="color:#7ecfff;font-size:14px;">采集时间：</span><span style="color:#fff;">${get('timestamp')}</span>
                </div>
                
                <div style="display:flex;gap:16px;align-items:center;">
                    <a href="personal?deviceSn=${deviceSn}" target="_blank" 
                       style="padding:12px 28px;background:linear-gradient(135deg,#00e4ff,#0099cc);color:#001529;text-decoration:none;border-radius:12px;font-weight:700;font-size:15px;box-shadow:0 6px 16px rgba(0,228,255,0.4);transition:all 0.3s ease;display:inline-flex;align-items:center;gap:10px;" 
                       onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 20px rgba(0,228,255,0.5)'" 
                       onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 6px 16px rgba(0,228,255,0.4)'">
                        📊 个人大屏
                    </a>
                    <span style="flex:1"></span>
                    <span style="color:#00e4ff;cursor:pointer;font-size:28px;font-weight:700;padding:8px;" onclick="removeCustomMapInfo()" title="关闭">×</span>
                </div>
            `;
        } else { // 告警点保持原样
            const level = get('severity_level','severityLevel');
            const levelColor = level === 'critical' ? '#ff4d4f' : level === 'high' ? '#ffbb00' : '#ffe066';
            div.innerHTML = `
                <div style="display:flex;align-items:center;gap:18px;margin-bottom:12px;">
                    <img src="${avatarUrl}" style="width:56px;height:56px;border-radius:50%;border:2px solid #00e4ff;box-shadow:0 0 8px #00e4ff44;object-fit:cover;background:#001529;">
                    <div>
                        <div style="font-size:18px;font-weight:700;letter-spacing:1px;">${get('dept_name','deptName')}</div>
                        <div style="font-size:16px;color:#00e4ff;font-weight:500;margin-top:2px;">${get('user_name','userName')}</div>
                    </div>
                </div>
                <div style="display:flex;gap:18px;flex-wrap:wrap;margin-bottom:8px;">
                    <div><span style="color:#7ecfff;">告警类别：</span><span style="color:${levelColor};font-weight:700;">${get('alert_type','alertType','-')}</span></div>
                    <div><span style="color:#7ecfff;">级别：</span><span style="color:${levelColor};font-weight:700;">${level||'-'}</span></div>
                    <div><span style="color:#7ecfff;">状态：</span><span style="color:#ff9c00;font-weight:700;">${get('alert_status','status','-')}</span></div>
                </div>
                <div style="margin-bottom:8px;">
                    <span style="color:#7ecfff;">位置信息：</span><span id="locationInfo">正在获取...</span>
                </div>
                <div style="margin-bottom:8px;">
                    <span style="color:#7ecfff;">告警时间：</span>${get('alert_timestamp','timestamp','-')}
                </div>
                <div style="display:flex;gap:18px;align-items:center;">
                    <button onclick="handleAlert('${get('alert_id','alertId')}')" style="padding:7px 22px;background:${levelColor};color:#001529;border:none;border-radius:6px;cursor:pointer;font-weight:700;box-shadow:0 2px 8px ${levelColor}44;transition:.2s;">一键处理</button>
                    <span style="flex:1"></span>
                    <span style="color:#00e4ff;cursor:pointer;font-size:22px;font-weight:700;" onclick="removeCustomMapInfo()">×</span>
                </div>
            `;
        }
        
        document.body.appendChild(div);
        
        // 获取位置信息
        const longitude = get('longitude');
        const latitude = get('latitude');
        if (longitude && latitude) {
            reverseGeocode(longitude, latitude)
                .then(address => {
                    const locationInfo = document.getElementById('locationInfo');
                    if (locationInfo) locationInfo.textContent = address || '未知位置';
                })
                .catch(error => {
                    const locationInfo = document.getElementById('locationInfo');
                    if (locationInfo) locationInfo.textContent = '获取位置信息失败';
                });
        }
    };
    
    // 重写updateMapData函数 - 添加用户标签数据
    window.updateMapData = function(data) {
        if (!data || !map || !loca) return;
        const {alerts, healths} = filterData(data);
        const f = [];
        
        alerts.forEach(a => {
            if ((a.longitude || a.longitude === 0) && (a.latitude || a.latitude === 0)) {
                f.push({
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [+a.longitude, +a.latitude]},
                    properties: {...a, type: 'alert'}
                });
            }
        });
        
        healths.forEach(h => { // 为健康数据添加user_label字段
            if ((h.longitude || h.longitude === 0) && (h.latitude || h.latitude === 0)) {
                f.push({
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [+h.longitude, +h.latitude]},
                    properties: {
                        ...h,
                        user_label: `${h.deptName||'未知部门'}-${h.userName||'未知用户'}`, // 文字标签
                        type: 'health'
                    }
                });
            }
        });
        
        const geoJSON = {type: 'FeatureCollection', features: f};
        const criticalAlerts = {type: 'FeatureCollection', features: geoJSON.features.filter(f => f.properties.severity_level === 'critical')};
        const highAlerts = {type: 'FeatureCollection', features: geoJSON.features.filter(f => f.properties.severity_level === 'high' || f.properties.severity_level === 'medium')};
        const healthData = {type: 'FeatureCollection', features: geoJSON.features.filter(f => f.properties.type === 'health')};
        
        breathRed.setSource(new Loca.GeoJSONSource({data: criticalAlerts}));
        breathYellow.setSource(new Loca.GeoJSONSource({data: highAlerts}));
        breathGreen.setSource(new Loca.GeoJSONSource({data: healthData}));
        
        // 创建/更新文字标签图层
        if (!window.breathGreenText && healthData.features.length > 0) {
            window.breathGreenText = new Loca.TextLayer({
                loca,
                zIndex: 114, // 高于圆点层
                opacity: 1,
                visible: true,
                zooms: [13, 22], // 只在较大缩放级别显示
            });
            
            window.breathGreenText.setSource(new Loca.GeoJSONSource({data: healthData}));
            window.breathGreenText.setStyle({
                text: {
                    field: 'user_label',
                    style: {
                        fontSize: 11,
                        fontFamily: '"Microsoft YaHei", Arial, sans-serif',
                        fontWeight: 'bold',
                        fillColor: '#ffffff',
                        strokeColor: '#1f4e79',
                        strokeWidth: 2,
                    }
                },
                offset: [0, -22], // 显示在圆点上方
                selectStyle: {
                    text: {
                        style: {
                            fillColor: '#00e4ff',
                            fontSize: 12,
                        }
                    }
                }
            });
            
            loca.add(window.breathGreenText);
        } else if (window.breathGreenText) {
            window.breathGreenText.setSource(new Loca.GeoJSONSource({data: healthData}));
        }
        
        // 设置地图中心
        if (f.length > 0) {
            const findFirst = (arr, cond) => {
                for (let item of arr) {
                    if (cond(item)) return item;
                }
                return null;
            };
            
            const center = findFirst(f, item => item.geometry && item.geometry.coordinates);
            if (center) {
                const [lng, lat] = center.geometry.coordinates;
                map.setCenter([lng, lat]);
            }
        }
    };
    
    console.log('✓ 地图增强功能已应用：员工标签+美化信息框+个人大屏链接');
}, 3000); // 延迟3秒确保地图完全加载 