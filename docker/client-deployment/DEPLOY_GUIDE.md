### 数据持久化问题
1. 确认外挂目录权限设置正确
2. 检查磁盘空间是否充足
3. 验证备份目录是否可写

### 数据恢复问题

#### 恢复失败常见问题
1. **MySQL恢复失败**：
   ```bash
   # 检查MySQL容器状态
   docker logs ljwx-mysql
   
   # 验证数据库连接
   docker exec ljwx-mysql mysql -uroot -p123456 -e "SHOW DATABASES;"
   
   # 检查备份文件完整性
   head -20 backup/mysql/ljwx_backup_latest.sql
   tail -20 backup/mysql/ljwx_backup_latest.sql
   
   # 手动恢复测试
   docker exec ljwx-mysql mysql -uroot -p123456 -e "CREATE DATABASE test_restore;"
   docker exec -i ljwx-mysql mysql -uroot -p123456 test_restore < backup/mysql/ljwx_backup_latest.sql
   ```

2. **Redis恢复失败**：
   ```bash
   # 检查Redis容器状态
   docker logs ljwx-redis
   
   # 验证RDB文件完整性
   file backup/redis/dump.rdb
   
   # 检查Redis数据目录权限
   ls -la data/redis/
   sudo chmod 777 data/redis/dump.rdb
   
   # 手动重启Redis
   docker-compose restart ljwx-redis
   ```

3. **权限问题**：
   ```bash
   # 修复数据目录权限
   sudo chmod -R 777 data/
   sudo chmod -R 777 backup/
   
   # 重新创建外挂目录
   ./fix-volume-mounts.sh
   ```

#### 完整恢复流程
如果需要完全重新部署并恢复所有数据：

```bash
# 1. 停止所有服务
docker-compose down -v

# 2. 清理数据目录（谨慎操作）
sudo rm -rf data/* logs/*

# 3. 重新部署
./deploy-client.sh

# 4. 等待服务完全启动
sleep 60

# 5. 恢复所有数据
./restore-all-data.sh

# 6. 验证恢复结果
./verify-deployment.sh
```

#### 数据恢复验证清单
恢复完成后，按以下清单验证：

| 检查项 | 验证命令 | 预期结果 |
|--------|----------|----------|
| MySQL连接 | `docker exec ljwx-mysql mysql -uroot -p123456 -e "SELECT 1"` | 返回1 |
| 用户数据 | `docker exec ljwx-mysql mysql -uroot -p123456 -e "USE ljwx; SELECT COUNT(*) FROM t_user_info;"` | >0 |
| 设备数据 | `docker exec ljwx-mysql mysql -uroot -p123456 -e "USE ljwx; SELECT COUNT(*) FROM t_device_info;"` | >0 |
| Redis连接 | `docker exec ljwx-redis redis-cli ping` | PONG |
| Redis数据 | `docker exec ljwx-redis redis-cli DBSIZE` | >0 |
| 后端服务 | `curl http://localhost:9998/actuator/health` | status:UP |
| 大屏服务 | `curl http://localhost:8001` | 200 OK |
| 管理端 | `curl http://localhost:8080` | 200 OK |
| 大屏跳转 | 浏览器访问 `http://localhost:8080/#/home` | 能跳转到大屏 |

#### 应急恢复方案
如果正常恢复流程失败，使用应急方案：

```bash
# 方案1：手动逐步恢复
# 1. 停止所有应用服务（保留数据库）
docker-compose stop ljwx-boot ljwx-bigscreen ljwx-admin

# 2. 仅恢复MySQL
./restore-database.sh backup/mysql/ljwx_backup_latest.sql

# 3. 验证数据库恢复
docker exec ljwx-mysql mysql -uroot -p123456 -e "USE ljwx; SHOW TABLES;"

# 4. 重启应用服务
docker-compose start ljwx-boot ljwx-bigscreen ljwx-admin

# 方案2：使用容器内恢复
# 进入MySQL容器内部操作
docker exec -it ljwx-mysql bash
mysql -uroot -p123456
SOURCE /backup/ljwx_backup_latest.sql;

# 方案3：分批恢复表数据
# 如果整体恢复失败，可按表分批恢复
./restore-table.sh t_user_info
./restore-table.sh t_device_info  
./restore-table.sh t_health_data
``` 