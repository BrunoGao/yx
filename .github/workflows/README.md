# 灵境万象系统 CI/CD 配置

## 概述
本项目使用 GitHub Actions 实现自动化 CI/CD 流水线，支持多架构（AMD64/ARM64）Docker 镜像构建并推送到阿里云容器镜像服务。

## 配置说明

### 镜像版本
- 当前版本: `1.3.1`
- 镜像仓库: `crpi-yilnm6upy4pmbp67.cn-shenzhen.personal.cr.aliyuncs.com/ljwx`

### 支持的服务
#### 应用服务
- `ljwx-mysql`: MySQL 数据库
- `ljwx-redis`: Redis 缓存
- `ljwx-boot`: Spring Boot 后端服务
- `ljwx-bigscreen`: 大屏展示前端
- `ljwx-admin`: 管理后台

#### 监控服务
- `ljwx-grafana`: 监控面板
- `ljwx-prometheus`: 监控数据采集
- `ljwx-loki`: 日志聚合
- `ljwx-promtail`: 日志收集
- `ljwx-alertmanager`: 告警管理

### 构建触发条件
- `push` 到 `main` 或 `master` 分支
- 创建版本标签（`v*`）
- Pull Request 到 `main` 或 `master` 分支

### 镜像标签策略
- 分支名称标签（如 `main`）
- 版本号标签（如 `1.3.1`）
- `latest` 标签（仅主分支）
- Pull Request 标签

### 登录凭据
- 用户名: `brunogao`
- 密码: `admin123`（在 GitHub Actions 中配置为 Secret）

## 使用方法

1. 推送代码到 GitHub
2. GitHub Actions 自动触发构建
3. 构建完成后，镜像将推送到阿里云容器镜像服务

## 镜像拉取命令
```bash
# 拉取最新版本
docker pull crpi-yilnm6upy4pmbp67.cn-shenzhen.personal.cr.aliyuncs.com/ljwx/ljwx-mysql:1.3.1
docker pull crpi-yilnm6upy4pmbp67.cn-shenzhen.personal.cr.aliyuncs.com/ljwx/ljwx-redis:1.3.1
docker pull crpi-yilnm6upy4pmbp67.cn-shenzhen.personal.cr.aliyuncs.com/ljwx/ljwx-boot:1.3.1
docker pull crpi-yilnm6upy4pmbp67.cn-shenzhen.personal.cr.aliyuncs.com/ljwx/ljwx-bigscreen:1.3.1
docker pull crpi-yilnm6upy4pmbp67.cn-shenzhen.personal.cr.aliyuncs.com/ljwx/ljwx-admin:1.3.1
```

## 注意事项
- 构建支持 AMD64 和 ARM64 架构
- 使用 GitHub Actions 缓存加速构建
- MySQL 服务在构建时会导出最新数据