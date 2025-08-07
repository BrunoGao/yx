#!/bin/bash
# -*- coding: utf-8 -*-
# 数据库恢复脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 配置
MYSQL_CONTAINER="ljwx-mysql"
MYSQL_USER="root"
MYSQL_PASSWORD="123456"
MYSQL_DATABASE="ljwx"
BACKUP_DIR="../backup/mysql"
RESTORE_LOG="logs/restore_$(date +%Y%m%d_%H%M%S).log"

# 创建日志目录
mkdir -p logs

# 检查参数
if [ $# -eq 0 ]; then
    # 自动选择最新备份
    BACKUP_FILE=$(ls -t $BACKUP_DIR/*.sql 2>/dev/null | head -1)
    if [ -z "$BACKUP_FILE" ]; then
        log_error "未找到备份文件，请指定备份文件路径"
        echo "用法: $0 [backup_file.sql]"
        exit 1
    fi
    log_info "自动选择最新备份: $BACKUP_FILE"
else
    BACKUP_FILE="$1"
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "备份文件不存在: $BACKUP_FILE"
        exit 1
    fi
fi

log_info "开始数据库恢复流程..."

# 检查MySQL容器状态
if ! docker ps | grep -q $MYSQL_CONTAINER; then
    log_error "MySQL容器未运行，请先启动服务"
    exit 1
fi

# 等待MySQL服务就绪
log_info "等待MySQL服务就绪..."
for i in {1..30}; do
    if docker exec $MYSQL_CONTAINER mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -e "SELECT 1" >/dev/null 2>&1; then
        log_info "MySQL服务已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "MySQL服务启动超时"
        exit 1
    fi
    sleep 2
done

# 创建数据库备份（恢复前备份）
mkdir -p $BACKUP_DIR
CURRENT_BACKUP="$BACKUP_DIR/pre_restore_$(date +%Y%m%d_%H%M%S).sql"
log_info "创建恢复前备份: $CURRENT_BACKUP"
docker exec $MYSQL_CONTAINER mysqldump -u$MYSQL_USER -p$MYSQL_PASSWORD --single-transaction $MYSQL_DATABASE > $CURRENT_BACKUP

# 执行数据恢复
log_info "正在恢复数据库: $BACKUP_FILE"
{
    echo "恢复开始时间: $(date)"
    echo "备份文件: $BACKUP_FILE"
    echo "目标数据库: $MYSQL_DATABASE"
    echo "----------------------------------------"
} >> $RESTORE_LOG

if docker exec -i $MYSQL_CONTAINER mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < $BACKUP_FILE 2>> $RESTORE_LOG; then
    log_info "数据库恢复成功"
    
    # 验证恢复结果
    log_info "验证恢复结果..."
    USER_COUNT=$(docker exec $MYSQL_CONTAINER mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -e "USE $MYSQL_DATABASE; SELECT COUNT(*) FROM t_user_info;" -N 2>/dev/null || echo "0")
    DEVICE_COUNT=$(docker exec $MYSQL_CONTAINER mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -e "USE $MYSQL_DATABASE; SELECT COUNT(*) FROM t_device_info;" -N 2>/dev/null || echo "0")
    HEALTH_COUNT=$(docker exec $MYSQL_CONTAINER mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -e "USE $MYSQL_DATABASE; SELECT COUNT(*) FROM t_health_data;" -N 2>/dev/null || echo "0")
    
    log_info "恢复统计："
    log_info "  用户数据: $USER_COUNT 条"
    log_info "  设备数据: $DEVICE_COUNT 条"  
    log_info "  健康数据: $HEALTH_COUNT 条"
    
    {
        echo "恢复完成时间: $(date)"
        echo "恢复统计: 用户=$USER_COUNT, 设备=$DEVICE_COUNT, 健康=$HEALTH_COUNT"
        echo "----------------------------------------"
    } >> $RESTORE_LOG
    
    log_info "恢复日志保存至: $RESTORE_LOG"
    log_info "恢复前备份保存至: $CURRENT_BACKUP"
    
else
    log_error "数据库恢复失败，详见日志: $RESTORE_LOG"
    log_warn "可使用恢复前备份回滚: $CURRENT_BACKUP"
    exit 1
fi

log_info "数据库恢复完成！" 