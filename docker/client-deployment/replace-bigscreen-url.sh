#!/bin/bash
# 替换前端应用中的大屏URL #动态替换硬编码的localhost:8001

set -e

echo "🔄 替换前端应用中的大屏URL..."

# 加载配置文件 #CentOS兼容的配置加载方式
CONFIG_FILE=${1:-"custom-config.env"}
if [ -f "$CONFIG_FILE" ]; then
    . "$CONFIG_FILE"  #使用POSIX兼容的点号加载方式
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

# 等待容器完全启动 #确保容器服务可用
echo "⏳ 等待ljwx-admin容器完全启动..."
for i in $(seq 1 30); do  #CentOS兼容的序列生成
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "ljwx-admin.*Up"; then
        echo "✅ ljwx-admin容器已启动"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ 错误: ljwx-admin容器启动超时"
        exit 1
    fi
    sleep 2
done

# 再等待几秒确保nginx完全加载
sleep 5

# 获取容器ID
CONTAINER_ID=$(docker ps -q -f name=ljwx-admin)
if [ -z "$CONTAINER_ID" ]; then
    echo "❌ 错误: ljwx-admin 容器未运行"
    exit 1
fi

# 提取新URL的主机和端口部分，正确处理http://前缀
NEW_URL=$(echo "$VITE_BIGSCREEN_URL" | sed 's|^http://||' | sed 's|^https://||')
echo "   原地址: localhost:8001"
echo "   新地址: $NEW_URL"

# 转义特殊字符以防止sed错误 #处理IP地址中的点号等特殊字符
ESCAPED_NEW_URL=$(echo "$NEW_URL" | sed 's/\./\\./g' | sed 's/:/\\:/g')

# 检查容器中是否存在目标目录
if ! docker exec "$CONTAINER_ID" test -d "/usr/share/nginx/html/assets"; then
    echo "❌ 错误: /usr/share/nginx/html/assets 目录不存在"
    exit 1
fi

# 在容器中替换所有JavaScript文件中的localhost:8001 #使用更安全的替换方式
echo "🔄 正在替换JavaScript文件中的URL..."
docker exec "$CONTAINER_ID" sh -c "
    # 查找并替换所有JS文件中的localhost:8001
    find /usr/share/nginx/html/assets -name '*.js' -type f | while read file; do
        if grep -q 'localhost:8001' \"\$file\" 2>/dev/null; then
            # 创建临时文件进行替换
            sed 's|localhost:8001|$NEW_URL|g' \"\$file\" > \"\$file.tmp\" && mv \"\$file.tmp\" \"\$file\"
            echo \"✅ 已替换文件: \$file\"
        fi
    done
    
    # 同时检查index.html中是否有需要替换的内容
    if [ -f '/usr/share/nginx/html/index.html' ]; then
        if grep -q 'localhost:8001' '/usr/share/nginx/html/index.html' 2>/dev/null; then
            sed 's|localhost:8001|$NEW_URL|g' '/usr/share/nginx/html/index.html' > '/usr/share/nginx/html/index.html.tmp' && mv '/usr/share/nginx/html/index.html.tmp' '/usr/share/nginx/html/index.html'
            echo \"✅ 已替换index.html\"
        fi
    fi
    
    echo \"✅ 所有文件替换完成\"
"

# 验证替换结果
REPLACED_COUNT=$(docker exec "$CONTAINER_ID" sh -c "find /usr/share/nginx/html -name '*.js' -o -name '*.html' | xargs grep -l '$NEW_URL' 2>/dev/null | wc -l")
if [ "$REPLACED_COUNT" -gt 0 ]; then
    echo "✅ 成功替换了 $REPLACED_COUNT 个文件中的URL"
else
    echo "⚠️  警告: 没有找到需要替换的文件，可能URL已经是正确的"
fi

# 重新加载nginx配置 #确保配置生效
if docker exec "$CONTAINER_ID" nginx -t >/dev/null 2>&1; then
    docker exec "$CONTAINER_ID" nginx -s reload
    echo "✅ Nginx配置已重新加载"
else
    echo "⚠️  警告: Nginx配置测试失败，跳过重新加载"
fi

echo ""
echo "🎉 大屏URL替换完成！"
echo "💡 现在访问管理界面，大屏链接将跳转到: $VITE_BIGSCREEN_URL"
echo "📝 建议清除浏览器缓存以确保更改生效" 