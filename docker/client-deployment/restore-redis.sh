#!/bin/bash
# -*- coding: utf-8 -*-
# Redis数据恢复脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 配置
REDIS_CONTAINER="ljwx-redis"
BACKUP_DIR="../backup/redis"
REDIS_DATA_DIR="data/redis"

# 检查参数
if [ $# -eq 0 ]; then
    # 自动选择最新备份
    RDB_FILE=$(ls -t $BACKUP_DIR/*.rdb 2>/dev/null | head -1)
    if [ -z "$RDB_FILE" ]; then
        log_error "未找到Redis备份文件"
        echo "用法: $0 [dump.rdb]"
        exit 1
    fi
    log_info "自动选择最新备份: $RDB_FILE"
else
    RDB_FILE="$1"
    if [ ! -f "$RDB_FILE" ]; then
        log_error "Redis备份文件不存在: $RDB_FILE"
        exit 1
    fi
fi

log_info "开始Redis数据恢复..."

# 检查Redis容器
if ! docker ps | grep -q $REDIS_CONTAINER; then
    log_error "Redis容器未运行"
    exit 1
fi

# 备份当前Redis数据
mkdir -p $BACKUP_DIR
CURRENT_BACKUP="$BACKUP_DIR/pre_restore_$(date +%Y%m%d_%H%M%S).rdb"
log_info "备份当前Redis数据: $CURRENT_BACKUP"
docker exec $REDIS_CONTAINER redis-cli BGSAVE
sleep 5
docker cp $REDIS_CONTAINER:/data/dump.rdb $CURRENT_BACKUP

# 停止Redis服务
log_info "停止Redis服务..."
docker-compose stop $REDIS_CONTAINER

# 恢复数据文件
log_info "恢复Redis数据文件..."
mkdir -p $REDIS_DATA_DIR
cp $RDB_FILE $REDIS_DATA_DIR/dump.rdb
chmod 777 $REDIS_DATA_DIR/dump.rdb

# 启动Redis服务
log_info "启动Redis服务..."
docker-compose start $REDIS_CONTAINER

# 等待服务就绪
sleep 10

# 验证恢复
if docker exec $REDIS_CONTAINER redis-cli ping | grep -q PONG; then
    KEY_COUNT=$(docker exec $REDIS_CONTAINER redis-cli DBSIZE 2>/dev/null || echo "0")
    log_info "Redis恢复成功，当前键数量: $KEY_COUNT"
    log_info "恢复前备份保存至: $CURRENT_BACKUP"
else
    log_error "Redis恢复失败"
    exit 1
fi 