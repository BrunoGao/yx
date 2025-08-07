#!/bin/bash
# 测试本地镜像服务器配置
# Created: $(date)

echo "🧪 测试本地镜像服务器配置"
echo "=================================="

# 测试本地镜像服务器连接
echo "1. 测试本地镜像服务器连接..."
if curl -f -s "http://14.127.218.229:5001/v2/" > /dev/null; then
    echo "   ✅ 本地镜像服务器 14.127.218.229:5001 连接成功"
else
    echo "   ⚠️ 本地镜像服务器 14.127.218.229:5001 当前无法访问"
    echo "   💡 这可能是因为镜像服务器未启动，配置测试将继续进行"
fi

# 检查 Docker 配置
echo ""
echo "2. 检查 Docker 配置..."
if [ -f ~/.docker/daemon.json ]; then
    if grep -q "14.127.218.229:5001" ~/.docker/daemon.json; then
        echo "   ✅ Docker daemon.json 已配置本地镜像服务器"
    else
        echo "   ❌ Docker daemon.json 未配置本地镜像服务器"
    fi
else
    echo "   ⚠️ Docker daemon.json 不存在"
fi

# 检查 OrbStack 配置
echo ""
echo "3. 检查 OrbStack 配置..."
if [ -f ~/.orbstack/config/docker.json ]; then
    if grep -q "14.127.218.229:5001" ~/.orbstack/config/docker.json; then
        echo "   ✅ OrbStack 已配置本地镜像服务器"
    else
        echo "   ❌ OrbStack 未配置本地镜像服务器"
    fi
else
    echo "   ⚠️ OrbStack docker.json 不存在"
fi

echo ""
echo "4. 显示构建脚本使用方法..."
echo "   默认推送到本地镜像服务器:"
echo "   ./build-and-push.sh bigscreen"
echo ""
echo "   推送到阿里云镜像仓库:"
echo "   USE_LOCAL_REGISTRY=false ./build-and-push.sh bigscreen"
echo ""
echo "   查看镜像仓库内容:"
echo "   curl -s http://14.127.218.229:5001/v2/_catalog | jq"

echo ""
echo "🎉 配置检查完成！"