
// 内网部署前端配置
window.INTRANET_CONFIG = {
    mapConfig: {'offline_mode': True, 'fallback_enabled': True, 'network_timeout': 5000, 'api_check_interval': 30000},
    apiConfig: {'external_apis_enabled': False, 'local_data_cache': True, 'cache_duration': 3600},
    networkConfig: {'proxy_enabled': False, 'proxy_host': '', 'proxy_port': '', 'dns_servers': ['8.8.8.8', '114.114.114.114'], 'connection_check_urls': ['https://webapi.amap.com/favicon.ico', 'https://api.map.baidu.com/favicon.ico']},
    offlineResources: {'maps': {'enabled': True, 'tiles_path': './static/map-tiles/', 'geojson_path': './static/geojson/'}, 'icons': {'enabled': True, 'path': './static/icons/'}, 'fonts': {'enabled': True, 'path': './static/fonts/'}}
};

// 网络状态检测函数
window.checkNetworkStatus = function() {
    return new Promise((resolve) => {
        const urls = ['https://webapi.amap.com/favicon.ico', 'https://api.map.baidu.com/favicon.ico'];
        let checkedUrls = 0;
        
        urls.forEach(url => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => {
                checkedUrls++;
                if (checkedUrls >= urls.length) {
                    resolve(false);
                }
            };
            img.src = url + '?' + Date.now();
        });
        
        setTimeout(() => resolve(false), 5000);
    });
};

// 自动应用配置
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 内网配置已加载');
    if (window.INTRANET_CONFIG.mapConfig.offline_mode) {
        console.log('📱 内网离线模式已启用');
    }
});
