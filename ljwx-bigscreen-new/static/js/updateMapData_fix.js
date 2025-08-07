window.updateMapData = function(data) {
  console.log('updateMapData.data', data);
  if (!data || !map || !loca) {
      console.warn('地图未初始化或数据为空');
      return;
  }
  
  const {alerts, healths} = filterData(data);
  
  function isValidCoordinate(lng, lat) {
      try {
          const longitude = parseFloat(lng);
          const latitude = parseFloat(lat);
          return !isNaN(longitude) && !isNaN(latitude) && 
                 isFinite(longitude) && isFinite(latitude) &&
                 longitude >= -180 && longitude <= 180 && 
                 latitude >= -90 && latitude <= 90 &&
                 longitude !== 0 && latitude !== 0;
      } catch (e) {
          console.warn('坐标验证错误:', e);
          return false;
      }
  }
  
  const validHealths = healths.filter(h => {
      const isValid = isValidCoordinate(h.longitude, h.latitude);
      if (!isValid) {
          console.log('无效健康点坐标被过滤:', h.userName, h.longitude, h.latitude);
      }
      return isValid;
  });
  
  const healthFeatures = validHealths.map(h => ({
      type: 'Feature',
      geometry: {type: 'Point', coordinates: [parseFloat(h.longitude), parseFloat(h.latitude)]},
      properties: {
          ...h,
          dept_name: h.deptName || '未知部门',
          user_name: h.userName || '未知员工',
          label: `${h.deptName || '未知部门'}-${h.userName || '未知员工'}`,
          type: 'health'
      }
  }));
  
  const validAlerts = alerts.filter(a => isValidCoordinate(a.longitude, a.latitude));
  
  const alertFeatures = validAlerts.map(a => ({
      type: 'Feature',
      geometry: {type: 'Point', coordinates: [parseFloat(a.longitude), parseFloat(a.latitude)]},
      properties: {
          ...a,
          label: `⚠️${a.dept_name || '未知部门'}-${a.user_name || '未知员工'}`,
          type: 'alert'
      }
  }));
  
  const criticalAlerts = {type: 'FeatureCollection', features: alertFeatures.filter(f => f.properties.severity_level === 'critical')};
  const highAlerts = {type: 'FeatureCollection', features: alertFeatures.filter(f => f.properties.severity_level === 'high')};
  const healthData = {type: 'FeatureCollection', features: healthFeatures};
  
  console.log(`处理数据: ${healthFeatures.length}个有效健康点, ${alertFeatures.length}个有效告警点`);
  
  try {
      breathRed.setSource(new Loca.GeoJSONSource({data: criticalAlerts}));
      breathYellow.setSource(new Loca.GeoJSONSource({data: highAlerts}));
      breathGreen.setSource(new Loca.GeoJSONSource({data: healthData}));
      
      const allValidFeatures = [...alertFeatures, ...healthFeatures];
      if (allValidFeatures.length > 0) {
          const firstFeature = allValidFeatures[0];
          const [lng, lat] = firstFeature.geometry.coordinates;
          map.setCenter([lng, lat]);
          console.log(`地图中心设置为: [${lng}, ${lat}]`);
      } else {
          map.setCenter([114.01508952, 22.54036796]);
      }
      
      console.log('✅ 地图更新完成');
  } catch (error) {
      console.error('❌ 地图更新失败:', error);
  }
}; 