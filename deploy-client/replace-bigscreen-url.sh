#!/bin/bash
# 替换前端应用中的大屏URL #动态替换硬编码的localhost:8001

set -e

# 加载配置文件
CONFIG_FILE=${1:-"custom-config.env"}
if [ -f "$CONFIG_FILE" ]; then
    source $CONFIG_FILE
    echo "📋 已加载配置文件: $CONFIG_FILE"
else
    echo "❌ 错误: 配置文件 $CONFIG_FILE 不存在"
    exit 1
fi

# 检查环境变量
if [ -z "$VITE_BIGSCREEN_URL" ]; then
    echo "❌ 错误: VITE_BIGSCREEN_URL 环境变量未设置"
    exit 1
fi

echo "🔄 开始替换前端应用中的大屏URL..."
echo "   原地址: localhost:8001"
echo "   新地址: ${VITE_BIGSCREEN_URL#http://}"

# 获取容器ID
CONTAINER_ID=$(docker ps -q -f name=ljwx-admin)
if [ -z "$CONTAINER_ID" ]; then
    echo "❌ 错误: ljwx-admin 容器未运行"
    exit 1
fi

# 提取新URL的主机和端口部分
NEW_URL=${VITE_BIGSCREEN_URL#http://}

# 在容器中替换所有JavaScript文件中的localhost:8001
docker exec $CONTAINER_ID sh -c "
    find /usr/share/nginx/html/assets -name '*.js' -exec sed -i 's/localhost:8001/$NEW_URL/g' {} \;
    echo '✅ 已替换所有JavaScript文件中的URL'
"

# 重新加载nginx配置
docker exec $CONTAINER_ID nginx -s reload
echo "✅ Nginx配置已重新加载"

echo "🎉 URL替换完成！"
echo "💡 现在访问 http://localhost:8080/#/home 页面，大屏链接将跳转到 $VITE_BIGSCREEN_URL" 
