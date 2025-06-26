#!/bin/bash

echo "==================== 智能穿戴系统快速启动 ===================="
echo "正在检查环境..."

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装Docker"
    echo "安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 提示用户配置
echo "请按以下步骤进行配置:"
echo "1. 复制配置模板: cp custom-config.env my-config.env"
echo "2. 编辑配置文件: vim my-config.env"
echo "3. 运行部署脚本: ./deploy-client.sh my-config.env"
echo ""

read -p "是否使用默认配置直接部署? (y/N): " confirm
if [[ $confirm == [yY] ]]; then
    echo "使用默认配置部署..."
    ./deploy-client.sh
else
    echo "请按上述步骤完成配置后再运行部署脚本"
fi 