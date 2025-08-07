#!/bin/bash
# -*- coding: utf-8 -*-
# 部署验证脚本

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

# 验证结果统计
PASS_COUNT=0
FAIL_COUNT=0

# 验证函数
verify_check() {
    local name="$1"
    local command="$2"
    local expected="$3"
    
    echo -n "检查 $name ... "
    
    if result=$(eval "$command" 2>/dev/null); then
        if [[ -z "$expected" ]] || [[ "$result" == *"$expected"* ]]; then
            echo -e "${GREEN}✓${NC}"
            ((PASS_COUNT++))
            return 0
        else
            echo -e "${RED}✗${NC} (期望: $expected, 实际: $result)"
            ((FAIL_COUNT++))
            return 1
        fi
    else
        echo -e "${RED}✗${NC} (命令执行失败)"
        ((FAIL_COUNT++))
        return 1
    fi
}

log_info "=== 灵境万象健康管理系统 - 部署验证 ==="

# 1. 容器状态检查
log_step "检查容器状态..."
required_containers=("ljwx-mysql" "ljwx-redis" "ljwx-boot" "ljwx-bigscreen" "ljwx-admin")
for container in "${required_containers[@]}"; do
    verify_check "$container容器" "docker ps --format '{{.Names}}' | grep $container" "$container"
done

# 2. 数据库连接检查
log_step "检查数据库连接..."
verify_check "MySQL连接" "docker exec ljwx-mysql mysql -uroot -p123456 -e 'SELECT 1' -N" "1"

# 3. 数据库表检查
log_step "检查数据库表..."
verify_check "用户表数据" "docker exec ljwx-mysql mysql -uroot -p123456 -e 'USE ljwx; SELECT COUNT(*) FROM t_user_info' -N" ""
verify_check "设备表数据" "docker exec ljwx-mysql mysql -uroot -p123456 -e 'USE ljwx; SELECT COUNT(*) FROM t_device_info' -N" ""

# 4. Redis连接检查  
log_step "检查Redis缓存..."
verify_check "Redis连接" "docker exec ljwx-redis redis-cli ping" "PONG"
verify_check "Redis数据" "docker exec ljwx-redis redis-cli DBSIZE" ""

# 5. 服务健康检查
log_step "检查服务健康状态..."
verify_check "后端API服务" "curl -s http://localhost:9998/actuator/health | grep '\"status\":\"UP\"'" "status\":\"UP"
verify_check "大屏服务" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8001" "200"
verify_check "管理端服务" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080" "200"

# 6. 网络连通性检查
log_step "检查网络连通性..."
verify_check "大屏API连接" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/health" "200"

# 7. 文件权限检查
log_step "检查文件权限..."
verify_check "数据目录权限" "ls -ld data/" ""
verify_check "日志目录权限" "ls -ld logs/" ""

# 8. 特殊功能检查
log_step "检查特殊功能..."
# 检查大屏跳转URL配置
if [ -f "custom-config.env" ]; then
    BIGSCREEN_URL=$(grep VITE_BIGSCREEN_URL custom-config.env | cut -d'=' -f2 | tr -d '"')
    verify_check "大屏URL配置" "echo $BIGSCREEN_URL | grep -E '^https?://'" "http"
fi

# 输出验证结果
echo ""
log_info "=== 验证结果汇总 ==="
log_info "通过检查: ${GREEN}$PASS_COUNT${NC} 项"
if [ $FAIL_COUNT -gt 0 ]; then
    log_error "失败检查: ${RED}$FAIL_COUNT${NC} 项"
else
    log_info "失败检查: $FAIL_COUNT 项"
fi

# 建议操作
if [ $FAIL_COUNT -eq 0 ]; then
    log_info "🎉 所有检查项均通过！系统部署成功"
    echo ""
    log_info "访问地址："
    log_info "  管理端: http://localhost:8080"
    log_info "  大屏端: http://localhost:8001"
    log_info "  API文档: http://localhost:9998/doc.html"
    exit 0
else
    log_error "❌ 部分检查项失败，建议："
    echo "1. 查看服务日志: docker-compose logs -f"
    echo "2. 重启失败服务: docker-compose restart [service_name]"
    echo "3. 检查配置文件: cat custom-config.env"
    echo "4. 重新部署: ./deploy-client.sh"
    exit 1
fi 