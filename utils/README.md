# 健康数据迁移工具集

## 概述

这个目录包含了完整的健康数据迁移和管理工具，用于处理大规模健康数据的分区、迁移和优化。

## 脚本说明

### 1. 数据分析脚本

#### `analyze_table_structure.py`
- **功能**: 分析主表、每日表、每周表的结构和数据情况
- **用途**: 迁移前的数据现状分析
- **使用**: `python3 analyze_table_structure.py`

#### `check_user_org.py`
- **功能**: 检查用户组织关联关系
- **用途**: 验证设备与用户的映射关系
- **使用**: `python3 check_user_org.py`

#### `check_org_distribution.py`
- **功能**: 检查org_id分布差异
- **用途**: 对比主表和分区表的数据分布
- **使用**: `python3 check_org_distribution.py`

#### `check_partition_fields.py`
- **功能**: 检查分区表字段结构
- **用途**: 验证分区表与主表的字段差异
- **使用**: `python3 check_partition_fields.py`

### 2. 数据迁移脚本

#### `migrate_health_data.py` ⭐
- **功能**: 完整的健康数据迁移脚本
- **包含步骤**:
  1. 更新主表的org_id和user_id
  2. 迁移每日数据到t_user_health_data_daily
  3. 迁移每周数据到t_user_health_data_weekly
  4. 创建月度分区表
  5. 迁移数据到分区表
  6. 创建分区视图
  7. 清理主表JSON字段
- **使用**: `python3 migrate_health_data.py`

#### `sync_partition_org_ids.py`
- **功能**: 同步分区表的org_id和user_id
- **用途**: 修复分区表中缺失的组织和用户ID
- **使用**: `python3 sync_partition_org_ids.py`

#### `sync_latest_data.py`
- **功能**: 同步最新数据到分区表
- **用途**: 将主表中的最新数据同步到分区表
- **使用**: `python3 sync_latest_data.py`

### 3. 验证脚本

#### `verify_migration.py`
- **功能**: 验证数据迁移结果
- **检查项目**:
  - org_id/user_id更新情况
  - JSON字段清理情况
  - 每日表和每周表数据
  - 分区表数据完整性
  - 查询接口兼容性
- **使用**: `python3 verify_migration.py`

## 使用流程

### 完整迁移流程

```bash
# 1. 分析现状
python3 analyze_table_structure.py
python3 check_user_org.py

# 2. 执行迁移
python3 migrate_health_data.py

# 3. 验证结果
python3 verify_migration.py

# 4. 如有问题，执行修复
python3 sync_partition_org_ids.py
python3 sync_latest_data.py
```

### 单独使用场景

```bash
# 只检查数据分布
python3 check_org_distribution.py

# 只同步org_id
python3 sync_partition_org_ids.py

# 只同步最新数据
python3 sync_latest_data.py

# 检查字段结构
python3 check_partition_fields.py
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| MYSQL_HOST | 127.0.0.1 | MySQL主机地址 |
| MYSQL_PORT | 3306 | MySQL端口 |
| MYSQL_USER | root | MySQL用户名 |
| MYSQL_PASSWORD | aV5mV7kQ!@# | MySQL密码 |
| MYSQL_DATABASE | lj-06 | 数据库名 |

### 配置文件

- `config.py`: 数据库连接配置
- 自动读取环境变量，支持不同环境部署

## 数据结构

### 主表 (t_user_health_data)
- 存储快更新字段：心率、血氧、血压等
- 包含完整的org_id和user_id
- JSON字段已清理

### 每日表 (t_user_health_data_daily)
- 存储每日更新字段：睡眠、运动、锻炼数据
- 按设备+日期分组

### 每周表 (t_user_health_data_weekly)
- 存储每周更新字段：每周运动数据
- 按设备+周开始日期分组

### 分区表 (t_user_health_data_YYYYMM)
- 按月分区：202411-202505
- 包含主表核心字段（不含JSON）
- 通过分区视图统一访问

## 性能优化

### 查询优化
- 分区视图优先查询
- 自动回退到主表
- 三表数据合并

### 存储优化
- JSON数据分离存储
- 按月分区减少查询范围
- 索引优化提升性能

## 注意事项

1. **备份数据**: 迁移前请备份重要数据
2. **测试环境**: 建议先在测试环境验证
3. **分批执行**: 大数据量时建议分批迁移
4. **监控资源**: 注意数据库CPU和内存使用
5. **验证结果**: 每个步骤后都要验证数据完整性

## 故障排除

### 常见问题

1. **连接失败**: 检查数据库配置和网络连接
2. **权限不足**: 确保数据库用户有足够权限
3. **内存不足**: 大数据量迁移时调整批次大小
4. **字段不匹配**: 检查表结构是否一致

### 错误处理

- 所有脚本都有完整的错误处理
- 支持事务回滚
- 详细的日志输出
- 自动重试机制

## 版本历史

- **V6.0**: 完整的数据迁移和分区优化
- **V5.2**: 三表数据合并优化
- **V5.1**: 查询接口优化修复
- **V5.0**: 健康数据上传逻辑修复
- **V4.0**: 健康数据分区表优化
