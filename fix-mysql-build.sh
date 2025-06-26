#!/bin/bash
# MySQL构建问题快速修复脚本 v1.0.1
# 修复阿里云镜像源访问问题

set -e

echo "🔧 MySQL构建问题快速修复工具"
echo "========================================="

# 检查Docker状态
echo "1. 检查Docker服务状态..."
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker服务未运行，请先启动Docker"
    exit 1
fi
echo "✅ Docker服务正常"

# 测试镜像源可用性
echo "2. 测试MySQL镜像源可用性..."
mysql_images=(
    "mysql:8.0"
    "docker.mirrors.ustc.edu.cn/library/mysql:8.0"
    "hub-mirror.c.163.com/library/mysql:8.0"
    "registry.docker-cn.com/library/mysql:8.0"
    "dockerhub.azk8s.cn/library/mysql:8.0"
)

working_image=""
for img in "${mysql_images[@]}"; do
    echo "   测试: $img"
    if timeout 10 docker manifest inspect "$img" >/dev/null 2>&1; then
        echo "   ✅ 可用: $img"
        working_image="$img"
        break
    else
        echo "   ❌ 不可用: $img"
    fi
done

if [ -z "$working_image" ]; then
    echo "❌ 所有镜像源都不可用，请检查网络连接"
    exit 1
fi

echo "🎯 选择镜像源: $working_image"

# 备份原Dockerfile
echo "3. 备份原始Dockerfile..."
if [ -f "docker/mysql/Dockerfile" ]; then
    cp docker/mysql/Dockerfile "docker/mysql/Dockerfile.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ 已备份原始Dockerfile"
fi

# 更新Dockerfile使用可工作的镜像源
echo "4. 更新Dockerfile..."
sed -i.bak "s|FROM.*mysql.*|FROM $working_image|g" docker/mysql/Dockerfile
echo "✅ 已更新Dockerfile使用: $working_image"

# 配置Docker镜像加速器
echo "5. 配置Docker镜像加速器..."
daemon_json="/etc/docker/daemon.json"

if [ -w "$(dirname "$daemon_json")" ] 2>/dev/null; then
    # 备份现有配置
    if [ -f "$daemon_json" ]; then
        sudo cp "$daemon_json" "${daemon_json}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 创建新配置
    cat << 'EOF' | sudo tee "$daemon_json" > /dev/null
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://registry.docker-cn.com",
    "https://docker.m.daocloud.io",
    "https://dockerhub.azk8s.cn"
  ],
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5,
  "storage-driver": "overlay2"
}
EOF
    
    echo "✅ 已配置Docker镜像加速器"
    echo "🔄 请重启Docker服务: sudo systemctl restart docker"
else
    echo "⚠️ 无权限配置镜像加速器，请手动配置"
fi

# 显示修复摘要
echo ""
echo "🎉 修复完成！"
echo "========================================="
echo "修复内容："
echo "  ✅ 选择可用镜像源: $working_image"
echo "  ✅ 更新Dockerfile配置"
echo "  ✅ 配置Docker镜像加速器"
echo ""
echo "下一步操作："
echo "  1. 重启Docker: sudo systemctl restart docker"
echo "  2. 重新构建: ./build-and-push.sh mysql"
echo ""
echo "如果还有问题，请检查："
echo "  - 网络连接是否正常"
echo "  - Docker磁盘空间是否充足"
echo "  - 防火墙设置是否正确" 