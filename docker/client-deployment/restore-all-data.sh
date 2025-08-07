#!/bin/bash
# -*- coding: utf-8 -*-
# 一键恢复所有数据脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 配置
BACKUP_BASE_DIR="../backup"
MYSQL_BACKUP_DIR="$BACKUP_BASE_DIR/mysql"
REDIS_BACKUP_DIR="$BACKUP_BASE_DIR/redis"
BOOT_BACKUP_DIR="$BACKUP_BASE_DIR/ljwx-boot"
BIGSCREEN_BACKUP_DIR="$BACKUP_BASE_DIR/ljwx-bigscreen"

log_info "=== 灵境万象健康管理系统 - 数据全量恢复 ==="

# 检查备份目录
check_backup_dirs() {
    log_step "检查备份目录..."
    for dir in "$MYSQL_BACKUP_DIR" "$REDIS_BACKUP_DIR" "$BOOT_BACKUP_DIR" "$BIGSCREEN_BACKUP_DIR"; do
        if [ ! -d "$dir" ]; then
            log_warn "备份目录不存在: $dir"
        else
            files_count=$(ls -1 "$dir" 2>/dev/null | wc -l)
            log_info "  $dir: $files_count 个文件"
        fi
    done
}

# 检查服务状态
check_services() {
    log_step "检查服务状态..."
    
    required_containers=("ljwx-mysql" "ljwx-redis" "ljwx-boot" "ljwx-bigscreen" "ljwx-admin")
    for container in "${required_containers[@]}"; do
        if docker ps | grep -q $container; then
            log_info "  ✓ $container 运行中"
        else
            log_error "  ✗ $container 未运行"
            exit 1
        fi
    done
}

# 恢复MySQL数据
restore_mysql() {
    log_step "恢复MySQL数据库..."
    
    if [ -f "./restore-database.sh" ]; then
        ./restore-database.sh
    else
        # 查找最新的MySQL备份
        MYSQL_BACKUP=$(ls -t $MYSQL_BACKUP_DIR/*.sql 2>/dev/null | head -1)
        if [ -n "$MYSQL_BACKUP" ]; then
            log_info "使用备份文件: $MYSQL_BACKUP"
            docker exec -i ljwx-mysql mysql -uroot -p123456 ljwx < $MYSQL_BACKUP
            log_info "MySQL数据恢复完成"
        else
            log_warn "未找到MySQL备份文件，跳过数据库恢复"
        fi
    fi
}

# 恢复Redis数据
restore_redis() {
    log_step "恢复Redis缓存数据..."
    
    if [ -f "./restore-redis.sh" ]; then
        ./restore-redis.sh
    else
        REDIS_BACKUP=$(ls -t $REDIS_BACKUP_DIR/*.rdb 2>/dev/null | head -1)
        if [ -n "$REDIS_BACKUP" ]; then
            log_info "使用备份文件: $REDIS_BACKUP"
            docker-compose stop ljwx-redis
            cp $REDIS_BACKUP data/redis/dump.rdb
            chmod 777 data/redis/dump.rdb
            docker-compose start ljwx-redis
            sleep 10
            log_info "Redis数据恢复完成"
        else
            log_warn "未找到Redis备份文件，跳过缓存恢复"
        fi
    fi
}

# 恢复应用文件
restore_app_files() {
    log_step "恢复应用文件和配置..."
    
    # 恢复后端文件
    if [ -d "$BOOT_BACKUP_DIR" ]; then
        log_info "恢复ljwx-boot文件..."
        mkdir -p data/ljwx-boot
        cp -r $BOOT_BACKUP_DIR/* data/ljwx-boot/ 2>/dev/null || true
        log_info "ljwx-boot文件恢复完成"
    fi
    
    # 恢复大屏文件
    if [ -d "$BIGSCREEN_BACKUP_DIR" ]; then
        log_info "恢复ljwx-bigscreen文件..."
        mkdir -p data/ljwx-bigscreen
        cp -r $BIGSCREEN_BACKUP_DIR/* data/ljwx-bigscreen/ 2>/dev/null || true
        log_info "ljwx-bigscreen文件恢复完成"
    fi
}

# 验证恢复结果
verify_restore() {
    log_step "验证恢复结果..."
    
    # 验证MySQL
    USER_COUNT=$(docker exec ljwx-mysql mysql -uroot -p123456 -e "USE ljwx; SELECT COUNT(*) FROM t_user_info;" -N 2>/dev/null || echo "0")
    DEVICE_COUNT=$(docker exec ljwx-mysql mysql -uroot -p123456 -e "USE ljwx; SELECT COUNT(*) FROM t_device_info;" -N 2>/dev/null || echo "0")
    
    # 验证Redis
    REDIS_KEYS=$(docker exec ljwx-redis redis-cli DBSIZE 2>/dev/null || echo "0")
    
    # 验证服务
    BOOT_STATUS=$(curl -s http://localhost:9998/actuator/health 2>/dev/null | grep -o '"status":"UP"' || echo "DOWN")
    BIGSCREEN_STATUS=$(curl -s http://localhost:8001 >/dev/null 2>&1 && echo "UP" || echo "DOWN")
    ADMIN_STATUS=$(curl -s http://localhost:8080 >/dev/null 2>&1 && echo "UP" || echo "DOWN")
    
    log_info "恢复结果统计:"
    log_info "  MySQL数据: 用户=$USER_COUNT, 设备=$DEVICE_COUNT"
    log_info "  Redis缓存: $REDIS_KEYS 个键"
    log_info "  服务状态: 后端=$BOOT_STATUS, 大屏=$BIGSCREEN_STATUS, 管理端=$ADMIN_STATUS"
    
    if [ "$BOOT_STATUS" = "UP" ] && [ "$BIGSCREEN_STATUS" = "UP" ] && [ "$ADMIN_STATUS" = "UP" ]; then
        log_info "✓ 所有服务恢复正常"
        return 0
    else
        log_error "✗ 部分服务恢复异常"
        return 1
    fi
}

# 主流程
main() {
    log_info "开始全量数据恢复流程..."
    
    check_backup_dirs
    check_services
    
    # 执行恢复
    restore_mysql
    restore_redis  
    restore_app_files
    
    # 重启服务确保配置生效
    log_step "重启服务以应用恢复的配置..."
    docker-compose restart ljwx-boot ljwx-bigscreen ljwx-admin
    
    # 等待服务启动
    log_info "等待服务完全启动..."
    sleep 30
    
    # 验证结果
    if verify_restore; then
        log_info "🎉 数据全量恢复成功！"
        log_info "访问地址："
        log_info "  管理端: http://localhost:8080"
        log_info "  大屏: http://localhost:8001"
        log_info "  API: http://localhost:9998"
    else
        log_error "❌ 数据恢复过程中出现问题，请检查日志"
        exit 1
    fi
}

# 确认操作
read -p "确认执行数据全量恢复？这将覆盖当前所有数据 (y/N): " confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    main
else
    log_info "操作已取消"
    exit 0
fi 