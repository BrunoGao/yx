# 本地镜像服务器配置指南

## 📋 概述
本文档介绍如何配置本地镜像服务器 `14.127.218.229:5001` 和修改构建脚本以默认推送到本地服务器。

## 🔧 已完成的配置

### 1. 修改构建脚本 (build-and-push.sh)
- ✅ 新增本地镜像服务器配置：`14.127.218.229:5001/ljwx`
- ✅ 默认使用本地镜像服务器 (`USE_LOCAL_REGISTRY=true`)
- ✅ 支持切换到阿里云镜像仓库
- ✅ 自动检测镜像服务器连接性

### 2. 配置 Docker 和 OrbStack
- ✅ 添加 `14.127.218.229:5001` 到 Docker insecure-registries
- ✅ 配置 OrbStack 支持本地镜像服务器
- ✅ 创建测试脚本验证配置

## 🚀 使用方法

### 构建并推送到本地镜像服务器 (默认)
```bash
# 构建单个镜像
./build-and-push.sh bigscreen

# 构建所有应用镜像  
./build-and-push.sh apps

# 构建所有镜像
./build-and-push.sh all
```

### 构建并推送到阿里云镜像仓库
```bash
# 使用环境变量切换到阿里云
USE_LOCAL_REGISTRY=false ./build-and-push.sh bigscreen

# 或者修改脚本中的 USE_LOCAL_REGISTRY 默认值
```

### 测试配置
```bash
# 运行配置测试脚本
./test-local-registry.sh
```

## 📊 配置文件位置

### Docker 配置
- **文件**: `~/.docker/daemon.json`
- **内容**: 添加了 `"insecure-registries": ["14.127.218.229:5001"]`

### OrbStack 配置
- **文件**: `~/.orbstack/config/docker.json`
- **内容**: 添加了 `"insecure-registries": ["14.127.218.229:5001"]`

## 🔍 验证配置

### 1. 检查本地镜像服务器连接
```bash
curl -s http://14.127.218.229:5001/v2/
```

### 2. 查看镜像仓库内容
```bash
curl -s http://14.127.218.229:5001/v2/_catalog | jq
```

### 3. 查看特定镜像的标签
```bash
curl -s http://14.127.218.229:5001/v2/ljwx/ljwx-bigscreen/tags/list | jq
```

## 🏷️ 镜像标签格式

### 本地镜像服务器标签
- `14.127.218.229:5001/ljwx/ljwx-bigscreen:1.2.18`
- `14.127.218.229:5001/ljwx/ljwx-bigscreen:latest`

### 拉取镜像
```bash
# 本地拉取
docker pull 14.127.218.229:5001/ljwx/ljwx-bigscreen:1.2.18

# 远程拉取 (其他机器)
docker pull 14.127.218.229:5001/ljwx/ljwx-bigscreen:1.2.18
```

## 🛠️ 环境变量控制

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `USE_LOCAL_REGISTRY` | `true` | 使用本地镜像服务器 |
| `LOCAL_BUILD` | `false` | 多架构构建模式 |
| `PUSH_TO_REGISTRY` | `true` | 推送到镜像仓库 |
| `PLATFORMS` | `linux/amd64,linux/arm64` | 构建平台 |

## 📁 相关文件

- `build-and-push.sh` - 主构建脚本
- `test-local-registry.sh` - 配置测试脚本  
- `~/.docker/daemon.json` - Docker 配置
- `~/.orbstack/config.json` - OrbStack 配置
- `LOCAL_REGISTRY_SETUP.md` - 本文档

## 🎯 优势

1. **网络速度**: 本地推送和拉取更快
2. **网络稳定**: 不依赖外网连接
3. **成本节省**: 减少阿里云流量费用
4. **开发效率**: 快速迭代和测试
5. **灵活切换**: 支持一键切换到阿里云

## 🔄 重启 Docker 服务

配置修改后需要重启 Docker 服务:

```bash
# 重启 OrbStack (如果使用)
orbstack restart

# 或者重启 Docker Desktop (如果使用)
```

---
*配置完成时间: $(date)*
*文档版本: v1.0*