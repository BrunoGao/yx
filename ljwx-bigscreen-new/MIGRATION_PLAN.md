# LJWX BigScreen 架构重构迁移计划

## 目标
将现有的单体bigScreen.py文件重构为标准Flask架构，提高可维护性和模块化程度，同时确保Watch端接口的完全兼容性。

## 核心原则
1. **保持兼容性**: 确保5个Watch端接口不受影响
2. **安全迁移**: 逐步迁移，每步验证功能正常
3. **标准架构**: 采用Flask最佳实践
4. **模块化**: 按功能域划分模块

## 迁移阶段

### 阶段1: 基础架构搭建 ✅
- [x] 创建标准Flask项目结构
- [x] 配置管理(config.py)
- [x] 扩展初始化(extensions.py)
- [x] 应用工厂(app/__init__.py)

### 阶段2: Watch端接口迁移 🟡
- [x] 创建Watch蓝图架构
- [ ] 复制原有5个接口的业务逻辑
- [ ] 创建对应的服务层
- [ ] 验证接口兼容性

### 阶段3: 数据模型迁移
- [ ] 复制models.py到新架构
- [ ] 按功能域拆分模型文件
- [ ] 更新导入关系

### 阶段4: 业务服务迁移
- [ ] 健康数据服务(HealthService)
- [ ] 设备管理服务(DeviceService)
- [ ] 告警处理服务(AlertService)
- [ ] 消息服务(MessageService)
- [ ] 配置服务(ConfigService)

### 阶段5: 大屏功能迁移
- [ ] 大屏路由迁移
- [ ] 模板文件迁移
- [ ] 静态资源迁移
- [ ] API接口迁移

### 阶段6: 测试与验证
- [ ] 功能测试
- [ ] 性能测试
- [ ] 兼容性验证
- [ ] 压力测试

### 阶段7: 部署切换
- [ ] 备份原系统
- [ ] 切换到新架构
- [ ] 监控运行状态
- [ ] 回滚准备

## 核心Watch端接口保护清单

必须保持100%兼容的接口：
1. `POST /upload_health_data` - 健康数据上传
2. `POST /upload_device_info` - 设备信息上传
3. `POST /upload_common_event` - 通用事件上传
4. `POST /DeviceMessage/save_message` - 保存设备消息
5. `POST /DeviceMessage/send` - 发送设备消息
6. `GET /DeviceMessage/receive` - 接收设备消息
7. `GET /fetch_health_data_config` - 获取健康数据配置

## 风险控制措施

1. **备份策略**: 每个阶段开始前创建完整备份
2. **回滚计划**: 每个阶段都有明确的回滚步骤
3. **测试验证**: 每个阶段完成后进行功能验证
4. **监控观察**: 实时监控系统运行状态

## 当前进度

当前已完成阶段1的基础架构搭建，正在进行阶段2的Watch端接口迁移。

下一步需要：
1. 完成Watch服务层的具体实现
2. 从原项目复制核心业务逻辑
3. 创建测试用例验证兼容性

## 文件结构对照

### 原架构
```
bigScreen/
├── bigScreen.py (3764行) - 所有功能集中
├── models.py - 数据模型
├── device.py - 设备相关
├── user_health_data.py - 健康数据
├── alert.py - 告警处理
└── ...其他模块
```

### 新架构
```
app/
├── __init__.py - 应用工厂
├── config.py - 配置管理
├── extensions.py - 扩展初始化
├── blueprints/
│   ├── watch/ - Watch端接口(保持兼容)
│   ├── bigscreen/ - 大屏功能
│   └── api/ - 其他API
├── services/ - 业务逻辑层
├── models/ - 数据模型
└── utils/ - 工具函数
```

## 测试计划

每个阶段完成后必须通过以下测试：
1. Watch端接口功能测试
2. 数据库连接测试
3. Redis连接测试
4. 基本功能冒烟测试
5. 性能基准测试 