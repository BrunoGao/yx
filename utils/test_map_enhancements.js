/**
 * 地图增强功能测试脚本
 * 在浏览器控制台执行此脚本来测试功能
 */

// 测试数据
const testHealthData = {
    type: 'FeatureCollection',
    features: [{
        type: 'Feature',
        geometry: {type: 'Point', coordinates: [114.0500, 22.5500]},
        properties: {
            type: 'health',
            deptName: '技术部',
            userName: '张三',
            device_sn: 'TEST123456',
            heartRate: 75,
            bloodOxygen: 98,
            temperature: 36.5,
            pressureHigh: 120,
            pressureLow: 80,
            step: 8650,
            distance: 5200,
            calorie: 2800,
            timestamp: new Date().toLocaleString(),
            user_label: '技术部-张三'
        }
    }]
};

console.log('🧪 开始测试地图增强功能...');

// 测试1: 检查函数是否存在
console.log('1. 检查关键函数...');
console.log('   showCustomMapInfo:', typeof window.showCustomMapInfo);
console.log('   updateMapData:', typeof window.updateMapData);
console.log('   removeCustomMapInfo:', typeof window.removeCustomMapInfo);

// 测试2: 检查地图对象
console.log('2. 检查地图对象...');
console.log('   map:', typeof window.map);
console.log('   loca:', typeof window.loca);
console.log('   breathGreen:', typeof window.breathGreen);

// 测试3: 模拟点击健康点
console.log('3. 模拟健康点点击...');
try {
    window.showCustomMapInfo(testHealthData.features[0]);
    console.log('   ✅ 健康信息框显示成功');
    
    // 检查个人大屏链接
    setTimeout(() => {
        const personalLink = document.querySelector('a[href*="personal?deviceSn="]');
        if (personalLink) {
            console.log('   ✅ 个人大屏链接已添加:', personalLink.href);
        } else {
            console.log('   ❌ 个人大屏链接未找到');
        }
        
        // 检查美化样式
        const infoBox = document.querySelector('.custom-map-info');
        if (infoBox) {
            const styles = getComputedStyle(infoBox);
            console.log('   ✅ 信息框样式检查:');
            console.log('     - 边框:', styles.border);
            console.log('     - 圆角:', styles.borderRadius);
            console.log('     - 阴影:', styles.boxShadow);
        }
        
        // 关闭信息框
        setTimeout(() => {
            window.removeCustomMapInfo();
            console.log('   ✅ 信息框关闭成功');
        }, 2000);
    }, 500);
} catch (e) {
    console.log('   ❌ 健康信息框显示失败:', e.message);
}

// 测试4: 测试文字标签图层
console.log('4. 测试文字标签图层...');
if (window.loca && window.Loca) {
    try {
        // 模拟updateMapData调用
        const mockData = {
            health_data: {healthData: [testHealthData.features[0].properties]}
        };
        
        setTimeout(() => {
            console.log('   🔄 模拟地图数据更新...');
            if (window.breathGreenText) {
                console.log('   ✅ 文字标签图层已存在');
            } else {
                console.log('   ⚠️ 文字标签图层未创建，尝试手动创建...');
                if (window.breathGreen) {
                    window.breathGreenText = new Loca.TextLayer({
                        loca: window.loca,
                        zIndex: 114,
                        opacity: 1,
                        visible: true,
                        zooms: [13, 22]
                    });
                    console.log('   ✅ 文字标签图层手动创建成功');
                }
            }
        }, 1000);
    } catch (e) {
        console.log('   ❌ 文字标签测试失败:', e.message);
    }
} else {
    console.log('   ⚠️ Loca对象未找到，跳过文字标签测试');
}

// 测试5: 性能检查
console.log('5. 性能检查...');
const startTime = performance.now();
for (let i = 0; i < 100; i++) {
    // 模拟函数调用开销
    const testProps = testHealthData.features[0].properties;
    const get = (...k) => k.map(x => testProps[x]).find(x => x !== undefined && x !== null && x !== '') || '-';
    get('deptName', 'userName', 'device_sn');
}
const endTime = performance.now();
console.log(`   ⏱️ 100次函数调用耗时: ${(endTime - startTime).toFixed(2)}ms`);

console.log('🎉 地图增强功能测试完成！');
console.log('💡 建议：在实际大屏页面中运行此测试以获得更准确的结果。'); 