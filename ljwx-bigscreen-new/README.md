# LJWX BigScreen New

基于Flask的标准专业架构重构版本，支持Watch端、API端和BigScreen端业务。

## 项目结构

```
ljwx-bigscreen-new/
├── app/
│   ├── blueprints/
│   │   ├── watch/          # Watch端业务蓝图
│   │   ├── api/            # API端业务蓝图
│   │   └── bigscreen/      # BigScreen端业务蓝图
│   ├── models/             # 数据模型
│   ├── services/           # 业务服务层
│   ├── config.py           # 配置管理
│   └── __init__.py         # 应用工厂
├── config.env              # 环境配置
├── requirements.txt        # 依赖包
├── run.py                  # 启动入口
└── README.md              # 项目说明
```

## 配置管理

所有配置统一从 `config.env` 读取，支持以下配置项：

```bash
# 数据库配置
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=test

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Flask配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
APP_PORT=8080

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## 业务模块

### 1. Watch端业务 (5个核心接口)

- **健康数据上传**: `POST /watch/upload_health_data`
- **设备信息上传**: `POST /watch/upload_device_info`
- **通用事件上传**: `POST /watch/upload_common_event`
- **设备消息发送/接收**: `POST /watch/send_device_message`, `GET /watch/receive_device_messages/<device_sn>`
- **健康数据配置**: `GET /watch/health_data_config`

### 2. BigScreen端业务 (完整迁移)

#### 页面路由
- `/bigscreen/` - 大屏首页
- `/bigscreen/main` - 主页面
- `/bigscreen/alert` - 告警页面
- `/bigscreen/message` - 消息页面
- `/bigscreen/chart` - 图表页面
- `/bigscreen/personal` - 个人页面
- `/bigscreen/map` - 地图页面
- `/bigscreen/health_table` - 健康数据表格
- `/bigscreen/health_trends` - 健康趋势
- `/bigscreen/health_main` - 健康主页
- `/bigscreen/health_baseline` - 健康基线
- `/bigscreen/user_health_data_analysis` - 健康数据分析
- `/bigscreen/health_profile` - 健康画像
- `/bigscreen/config_management` - 配置管理
- `/bigscreen/device_bind` - 设备绑定
- `/bigscreen/device_analysis` - 设备分析
- `/bigscreen/device_dashboard` - 设备监控大屏
- `/bigscreen/device_detailed_analysis` - 设备详细分析
- `/bigscreen/personal_3d` - 3D人体模型
- `/bigscreen/personal_advanced` - 高级3D人体模型
- `/bigscreen/system_event_alert` - 系统事件告警

#### API接口
- `GET /bigscreen/api/tracks` - 获取轨迹数据
- `GET /bigscreen/getUserInfo` - 获取用户信息
- `GET /bigscreen/get_all_users` - 获取所有用户
- `GET /bigscreen/getUserDeviceSn` - 根据手机号获取设备SN
- `GET /bigscreen/getUserId` - 根据手机号获取用户ID
- `GET /bigscreen/fetch_health_data` - 获取健康数据
- `GET /bigscreen/fetch_alerts` - 获取告警数据
- `GET /bigscreen/fetch_messages` - 获取消息数据
- `GET /bigscreen/fetch_device_info` - 获取设备信息
- `GET /bigscreen/generateHealthJson` - 生成健康数据JSON
- `GET /bigscreen/generateAlertJson` - 生成告警数据JSON
- `GET /bigscreen/get_health_stats` - 获取健康统计
- `GET /bigscreen/checkLicense` - 检查许可证
- `GET /bigscreen/get_customer_id_by_deviceSn` - 根据设备SN获取客户ID
- `POST /bigscreen/DeviceMessage/save_message` - 保存设备消息
- `POST /bigscreen/DeviceMessage/send` - 发送设备消息
- `GET /bigscreen/DeviceMessage/receive` - 接收设备消息
- `POST /bigscreen/upload_device_info` - 上传设备信息
- `POST /bigscreen/upload_health_data` - 上传健康数据
- `POST /bigscreen/upload_common_event` - 上传通用事件
- `GET /bigscreen/fetch_health_data_config` - 获取健康数据配置
- `GET /bigscreen/get_health_data` - 获取健康数据
- `GET /bigscreen/fetch_alertType_stats` - 获取告警类型统计
- `GET /bigscreen/fetch_user_locations` - 获取用户位置信息
- `POST /bigscreen/upload_alerts` - 上传告警数据
- `GET /bigscreen/fetch_health_metrics` - 获取健康指标
- `GET /bigscreen/test_wechat_alert` - 测试微信告警
- `GET /bigscreen/generateAlertChart` - 生成告警图表数据
- `GET /bigscreen/generateAlertTypeChart` - 生成告警类型图表数据
- `GET /bigscreen/gatherDealAlert` - 获取已处理告警
- `GET /bigscreen/get_personal_info` - 获取个人信息
- `GET /bigscreen/gather_device_info` - 获取设备信息汇总
- `GET /bigscreen/get_total_info` - 获取总览信息

### 3. API端业务

- 提供RESTful API接口
- 支持数据查询、统计、分析等功能

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制并修改 `config.env` 文件：

```bash
cp config.env.example config.env
# 编辑 config.env 文件，配置数据库、Redis等信息
```

### 3. 启动应用

```bash
python run.py
```

应用将在 `http://localhost:8080` 启动（端口可在config.env中配置）。

## 架构特点

### 1. 极致码高尔夫风格
- 所有代码控制在最少行数实现相关功能
- 注释在代码右侧，文件和函数注释控制在一行以内
- 变量由统一配置文件管理，不重复定义

### 2. 标准Flask架构
- 蓝图模式组织业务模块
- 服务层分离业务逻辑
- 模型层统一数据访问
- 配置层统一管理

### 3. 中文友好
- 所有接口、文档、注释使用中文
- 错误信息本地化
- 日志记录中文

### 4. 性能优化
- 数据库连接池
- Redis缓存支持
- 异步处理支持
- 批量操作优化

## 迁移说明

### 从 ljwx-bigscreen 迁移

本项目已完整迁移 `ljwx-bigscreen/bigscreen/bigScreen.py` 中的所有业务功能：

1. **页面路由**: 所有页面路由已迁移到 `app/blueprints/bigscreen/routes.py`
2. **API接口**: 所有API接口已迁移并保持兼容
3. **业务逻辑**: 核心业务逻辑已迁移到 `app/services/bigscreen_service.py`
4. **数据模型**: 使用统一的数据模型层
5. **配置管理**: 所有配置统一从 `config.env` 读取

### 兼容性保证

- Watch端5个核心接口完全兼容
- BigScreen端所有接口保持原有路径和参数
- 数据库结构兼容原有设计
- 前端调用无需修改

## 开发指南

### 添加新接口

1. 在对应的蓝图路由文件中添加路由
2. 在服务层实现业务逻辑
3. 在配置文件中添加相关配置
4. 更新README文档

### 添加新配置

1. 在 `config.env` 中添加配置项
2. 在 `app/config.py` 中读取配置
3. 在代码中使用 `app.config['CONFIG_NAME']` 访问

### 数据库操作

使用SQLAlchemy ORM进行数据库操作：

```python
from app.models import UserHealthData, DeviceInfo

# 查询
users = UserHealthData.query.filter_by(deviceSn='xxx').all()

# 创建
new_user = UserHealthData(deviceSn='xxx', ...)
db.session.add(new_user)
db.session.commit()
```

## 测试

### 测试Watch端接口

```bash
python test_watch_apis.py
```

### 测试BigScreen端接口

```bash
curl http://localhost:8080/bigscreen/api/tracks
curl http://localhost:8080/bigscreen/getUserInfo?deviceSn=TEST001
```

## 部署

### Docker部署

```bash
docker build -t ljwx-bigscreen-new .
docker run -p 8080:8080 ljwx-bigscreen-new
```

### 生产环境

1. 修改 `config.env` 中的生产环境配置
2. 使用 `gunicorn` 或 `uwsgi` 部署
3. 配置反向代理（nginx）
4. 设置日志轮转和监控

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！ 