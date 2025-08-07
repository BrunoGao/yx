#!/bin/bash
# 自动更新所有Flutter项目的网络安全配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Flutter项目网络安全配置更新工具${NC}"
echo "=================================="

# 检查Python脚本是否存在
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/generate_network_config.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ 找不到Python脚本: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# 显示使用说明
show_usage() {
    echo -e "${YELLOW}使用方法:${NC}"
    echo "  $0 [选项]"
    echo ""
    echo -e "${YELLOW}选项:${NC}"
    echo "  --ips IP1 IP2 IP3    添加自定义IP地址"
    echo "  --no-internal        不包含内网IP段"
    echo "  --no-debug           不包含调试模式"
    echo "  --allow-external     允许外网HTTP访问"
    echo "  --help               显示此帮助信息"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo "  $0                                    # 使用默认配置更新所有项目"
    echo "  $0 --ips 192.168.1.100 192.168.1.200  # 添加自定义IP"
    echo "  $0 --no-debug                         # 生产环境配置"
    echo "  $0 --allow-external                   # 允许外网HTTP访问"
}

# 解析参数
CUSTOM_IPS=""
NO_INTERNAL=""
NO_DEBUG=""
ALLOW_EXTERNAL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --ips)
            shift
            while [[ $# -gt 0 && ! $1 =~ ^-- ]]; do
                CUSTOM_IPS="$CUSTOM_IPS $1"
                shift
            done
            ;;
        --no-internal)
            NO_INTERNAL="--no-internal"
            shift
            ;;
        --no-debug)
            NO_DEBUG="--no-debug"
            shift
            ;;
        --allow-external)
            ALLOW_EXTERNAL="--allow-external"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 未知参数: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# 构建Python命令
PYTHON_CMD="python3 $PYTHON_SCRIPT --update-all"

if [ -n "$CUSTOM_IPS" ]; then
    PYTHON_CMD="$PYTHON_CMD --ips $CUSTOM_IPS"
fi

if [ -n "$NO_INTERNAL" ]; then
    PYTHON_CMD="$PYTHON_CMD $NO_INTERNAL"
fi

if [ -n "$NO_DEBUG" ]; then
    PYTHON_CMD="$PYTHON_CMD $NO_DEBUG"
fi

if [ -n "$ALLOW_EXTERNAL" ]; then
    PYTHON_CMD="$PYTHON_CMD $ALLOW_EXTERNAL"
fi

echo -e "${BLUE}📋 配置参数:${NC}"
echo "  自定义IP: ${CUSTOM_IPS:-无}"
echo "  内网IP段: ${NO_INTERNAL:+禁用}${NO_INTERNAL:-启用}"
echo "  调试模式: ${NO_DEBUG:+禁用}${NO_DEBUG:-启用}"
echo "  外网访问: ${ALLOW_EXTERNAL:+允许}${ALLOW_EXTERNAL:-禁止}"
echo ""

# 确认操作
read -p "是否继续更新所有Flutter项目? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  操作已取消${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🚀 开始更新...${NC}"

# 执行更新
cd "$SCRIPT_DIR/.."
eval $PYTHON_CMD

echo ""
echo -e "${GREEN}✅ 更新完成！${NC}"
echo ""
echo -e "${YELLOW}📝 下一步操作:${NC}"
echo "1. 重新编译Flutter应用: flutter build apk"
echo "2. 安装到Android设备"
echo "3. 现在可以访问任何内网HTTP地址"
echo ""
echo -e "${BLUE}💡 提示:${NC}"
echo "- 此配置允许所有内网IP访问，适合开发环境"
echo "- 生产环境建议使用 --no-debug 选项"
echo "- 如需添加特定IP，使用 --ips 参数" 