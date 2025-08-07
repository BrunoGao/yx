# 灵境万象系统 - Docker集成部署方案

## 🚀 快速部署 (客户交付版本 v1.2.16)

```bash
# 1. 拉取最新镜像并启动服务
docker-compose pull && docker-compose up -d

# 2. 验证服务状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f
```

## 📋 版本信息

- **当前版本**: v1.2.16 (2025-06-26)
- **镜像仓库**: 阿里云容器镜像服务
- **支持架构**: AMD64, ARM64
- **数据库版本**: MySQL 8.0 (包含管理员分离功能)

## 🔥 v1.2.16 新特性

### 👥 管理员和普通用户分离功能
- **视图模式切换**: 支持全部用户、仅员工、仅管理员三种视图
- **权限精细控制**: 员工管理和用户管理分离
- **数据库优化**: 新增`is_admin`字段标记管理员角色
- **API分离**: 员工查询自动排除管理员用户

**使用方法**:
1. 在用户管理页面顶部选择视图模式
2. 通过`/employee/page`接口获取纯员工列表
3. 管理员角色通过`sys_role.is_admin=1`标识

## 🏗️ 服务架构

| 服务名 | 端口 | 镜像版本 | 描述 |
|--------|------|----------|------|
| ljwx-mysql | 3306 | 1.2.16 | MySQL数据库服务 |
| ljwx-redis | 6379 | 1.2.16 | Redis缓存服务 |
| ljwx-boot | 9998 | 1.2.16 | Spring Boot后端服务 |
| ljwx-bigscreen | 8001 | 1.2.16 | Python大屏服务 |
| ljwx-admin | 8080 | 1.2.16 | Vue3前端管理系统 |

## 💾 数据库升级

系统已包含自动数据库升级脚本，首次启动时会自动执行：

```sql
-- 管理员分离功能初始化
ALTER TABLE sys_role ADD COLUMN is_admin TINYINT(1) DEFAULT 0;
UPDATE sys_role SET is_admin = 1 WHERE role_code IN ('ADMIN', 'DAdmin');
```

## 🔧 环境配置

### 必需文件
- `custom-config.env` - 环境变量配置
- `custom-config.py` - Python服务配置  
- `custom-admin-config.js` - 前端配置
- `client-data.sql/` - 数据库初始化脚本

### 配置示例
```bash
# custom-config.env
MYSQL_PASSWORD=your_secure_password
VITE_APP_TITLE=您的公司穿戴管理系统
```

## 📊 健康检查

所有服务都配置了健康检查机制：
- **MySQL**: 30秒间隔，60秒启动等待
- **Redis**: 30秒间隔，30秒启动等待  
- **Boot**: 60秒间隔，120秒启动等待
- **Bigscreen**: 60秒间隔，90秒启动等待
- **Admin**: 60秒间隔，60秒启动等待

## 🛠️ 故障排除

### 用户分离功能不生效
```bash
# 检查数据库是否包含is_admin字段
docker-compose exec mysql mysql -uroot -p -e "DESCRIBE sys_role;"

# 手动执行升级脚本
docker-compose exec mysql mysql -uroot -p < /docker-entrypoint-initdb.d/client/init-admin-separation.sql
```

### 镜像版本验证
```bash
# 验证镜像多架构支持
docker manifest inspect crpi-yilnm6upy4pmbp67.cn-shenzhen.personal.cr.aliyuncs.com/ljwx/ljwx-admin:1.2.16
```

## 🔄 更新流程

### 1. 重新构建镜像
```bash
./build-and-push.sh apps  # 构建所有应用镜像
```

### 2. 部署更新
```bash
docker-compose pull      # 拉取最新镜像
docker-compose up -d     # 滚动更新服务
```

## 🌐 访问地址

- **管理后台**: http://localhost:8080
- **数据大屏**: http://localhost:8001  
- **后端API**: http://localhost:9998

**默认账号**: admin / 123456

## 📝 更新日志

### v1.2.16 (2025-06-26)
- ✨ 新增管理员和普通用户分离功能
- 🛠️ 优化数据库结构，增加`is_admin`字段
- 🎨 前端新增视图模式选择器
- 🔧 完善API权限控制
- 📦 支持多架构镜像构建

### v1.2.15
- 🔒 增强安全性配置
- 🚀 性能优化
- 🐛 修复已知问题

## 🤝 技术支持

如遇问题请检查：
1. 日志输出：`docker-compose logs [service_name]`
2. 服务状态：`docker-compose ps`  
3. 网络连通：`docker-compose exec ljwx-boot curl mysql:3306` 

# 健康大屏 Flask 新架构

## 目录结构

```
app/
  blueprints/
    api/         # API蓝图
    bigscreen/   # 大屏页面蓝图
    watch/       # Watch端接口蓝图
  models/        # 按领域拆分的数据模型
  services/      # 业务服务层
  config.py      # 配置文件
  extensions.py  # 扩展初始化
  __init__.py    # 应用工厂
requirements.txt # 依赖
run.py           # 启动入口
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动方法

```bash
python run.py
```

## 兼容说明
- Watch端五大接口100%兼容原有路径和参数。
- 大屏页面和API接口全部迁移为标准Flask蓝图，支持模块化维护。
- 所有配置、变量、常量均集中管理。
- 支持sqlite和MySQL，默认sqlite。

## 迁移说明
- 业务逻辑已分层，后续可平滑迁移和扩展。
- 详细测试脚本见`test_new_architecture.py`。

## 常见问题
- 缺少依赖请先`pip install -r requirements.txt`
- 数据库表自动创建，首次启动无需手动建表。
- 如需自定义配置请编辑`.env`或环境变量。 