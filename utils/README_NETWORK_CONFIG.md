# 网络安全配置工具使用指南

## 🎯 工具概述
这个工具可以自动为所有Flutter项目生成和更新Android网络安全配置，解决HTTP明文访问问题。

## 🚀 快速开始

### 1. 一键更新所有项目
```bash
./utils/update_network_config.sh
```

### 2. 重新编译应用
```bash
flutter build apk
```

### 3. 安装到设备
```bash
flutter install
```

## 📋 详细用法

### 基本命令
```bash
# 使用默认配置（推荐）
./utils/update_network_config.sh

# 添加自定义IP地址
./utils/update_network_config.sh --ips 192.168.1.100 192.168.1.200

# 生产环境配置（禁用调试模式）
./utils/update_network_config.sh --no-debug

# 仅自定义IP，不包含内网段
./utils/update_network_config.sh --no-internal --ips 192.168.1.83

# 允许外网HTTP访问（开发环境）
./utils/update_network_config.sh --allow-external
```

### 高级选项
```bash
# 查看帮助
./utils/update_network_config.sh --help

# 直接使用Python脚本
python3 utils/generate_network_config.py --update-all

# 生成配置文件到指定位置
python3 utils/generate_network_config.py --output my_config.xml

# 生成外网访问配置
python3 utils/generate_network_config.py --allow-external --output external_config.xml
```

## 🔧 配置说明

### 默认配置包含
- ✅ **本地访问**：127.0.0.1, localhost
- ✅ **内网IP段**：192.168.x.x, 10.x.x.x, 172.16-31.x.x
- ✅ **调试模式**：允许所有HTTP访问（开发环境）

### 外网访问配置
- 🌐 **允许外网HTTP**：使用`--allow-external`选项
- 🌐 **完全开放**：允许访问任何HTTP地址
- 🌐 **开发友好**：适合测试外部API

### 安全特性
- 🔒 **仅内网访问**：默认外网HTTP仍被阻止
- 🔒 **显式配置**：符合Android安全策略
- 🔒 **可选调试**：生产环境可禁用
- 🔒 **外网可控**：可选择是否允许外网访问

## 📁 文件结构
```
utils/
├── generate_network_config.py    # Python配置生成器
├── update_network_config.sh      # Shell自动化脚本
├── external_access_config.xml    # 外网访问配置模板
└── README_NETWORK_CONFIG.md      # 本说明文档
```

## 🎯 解决的问题
- ❌ `net::ERR_CLEARTEXT_NOT_PERMITTED` 错误
- ❌ 每次添加新IP需要手动配置
- ❌ 多个项目配置不一致
- ❌ 外网HTTP访问被阻止

## ✅ 提供的优势
- 🚀 **自动化**：一键更新所有项目
- 🔄 **通用性**：支持所有内网IP
- 🌐 **外网支持**：可选择允许外网HTTP访问
- 🛡️ **安全性**：默认仅允许内网HTTP访问
- 📦 **批量处理**：同时处理多个Flutter项目

## ⚠️ 注意事项
1. **需要重新编译**：配置生效需要重新安装应用
2. **调试模式**：生产环境建议使用`--no-debug`
3. **网络环境**：确保设备在内网环境中

## 🔍 故障排除

### 常见问题
1. **脚本权限错误**
   ```bash
   chmod +x utils/update_network_config.sh
   ```

2. **Python脚本找不到**
   ```bash
   # 确保在项目根目录运行
   cd /path/to/your/project
   ./utils/update_network_config.sh
   ```

3. **配置不生效**
   ```bash
   # 重新编译并安装
   flutter clean
   flutter build apk
   flutter install
   ```

## 📞 技术支持
如有问题，请检查：
1. 是否在正确的目录运行脚本
2. Python3是否正确安装
3. Flutter项目结构是否完整 