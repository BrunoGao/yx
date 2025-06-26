#!/bin/bash
# 强制清除浏览器缓存脚本 #解决浏览器缓存导致的URL未更新问题

set -e

echo "🔄 强制清除浏览器缓存..."

# 检查容器是否运行
if ! docker ps -q -f name=ljwx-admin > /dev/null; then
    echo "❌ ljwx-admin 容器未运行"
    exit 1
fi

# 为静态文件添加缓存控制头
echo "📋 配置nginx缓存控制..."
docker exec ljwx-admin sh -c "
cat > /etc/nginx/conf.d/cache-control.conf << 'EOF'
# 强制不缓存HTML和JS文件
location ~* \.(html|js|css)$ {
    add_header Cache-Control 'no-cache, no-store, must-revalidate';
    add_header Pragma 'no-cache';
    add_header Expires '0';
    try_files \$uri \$uri/ /index.html;
}

# 为静态资源添加版本号
location /assets/ {
    add_header Cache-Control 'no-cache, no-store, must-revalidate';
    add_header Pragma 'no-cache';
    add_header Expires '0';
    try_files \$uri =404;
}
EOF
"

# 重新加载nginx配置
docker exec ljwx-admin nginx -s reload
echo "✅ Nginx配置已更新"

# 修改index.html文件，添加缓存破坏参数
TIMESTAMP=$(date +%s)
docker exec ljwx-admin sh -c "
sed -i 's/\(src=\"\.\/assets\/[^\"]*\)/\1?v=$TIMESTAMP/g' /usr/share/nginx/html/index.html
sed -i 's/\(href=\"\.\/assets\/[^\"]*\)/\1?v=$TIMESTAMP/g' /usr/share/nginx/html/index.html
echo '✅ 已添加缓存破坏参数: $TIMESTAMP'
"

echo "🎉 缓存清除完成！"
echo ""
echo "💡 解决浏览器缓存的方法："
echo "   1. 硬刷新页面：Ctrl+F5 (Windows) 或 Cmd+Shift+R (Mac)"
echo "   2. 开发者工具：F12 -> Network -> Disable cache"
echo "   3. 隐私模式：使用浏览器隐私/无痕模式访问"
echo ""
echo "🌐 访问地址: http://localhost:8080/#/home" 
