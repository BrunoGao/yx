#!/bin/bash
# 健康数据模拟器启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIMULATOR="$SCRIPT_DIR/health_data_simulator.py"

# 检查Python脚本是否存在
if [ ! -f "$SIMULATOR" ]; then
    echo "错误: 找不到模拟器脚本 $SIMULATOR"
    exit 1
fi

# 检查Python依赖
python3 -c "import requests,mysql.connector" 2>/dev/null || {
    echo "错误: 缺少Python依赖，请安装: pip3 install requests mysql-connector-python"
    exit 1
}

# 显示帮助信息
show_help() {
    echo "健康数据模拟器 - 使用说明"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  quick           快速测试模式(2天数据)"
    echo "  batch           批量模拟模式(7天数据)"
    echo "  full            完整模拟模式(30天数据)"
    echo "  custom          自定义参数模式"
    echo "  help            显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 quick                    # 快速测试"
    echo "  $0 batch                    # 批量模拟"
    echo "  $0 full                     # 完整模拟"
    echo "  $0 custom --users 5 --days 14  # 自定义参数"
}

# 检查大屏服务是否运行
check_service() {
    echo "检查大屏服务状态..."
    if curl -s http://localhost:5001/health >/dev/null 2>&1; then
        echo "✓ 大屏服务运行正常"
        return 0
    else
        echo "✗ 大屏服务未运行，请先启动服务"
        echo "提示: cd ljwx-bigscreen/bigscreen && python3 run.py"
        return 1
    fi
}

# 主逻辑
case "${1:-help}" in
    "quick")
        echo "=== 快速测试模式 ==="
        check_service || exit 1
        python3 "$SIMULATOR" --quick --no-confirm
        ;;
    "batch")
        echo "=== 批量模拟模式 ==="
        check_service || exit 1
        python3 "$SIMULATOR" --users 3 --days 7 --interval 10 --baseline-days 7
        ;;
    "full")
        echo "=== 完整模拟模式 ==="
        check_service || exit 1
        echo "警告: 这将生成大量数据，可能需要较长时间"
        read -p "是否继续? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            python3 "$SIMULATOR" --users 5 --days 30 --interval 5 --baseline-days 14 --no-confirm
        else
            echo "取消操作"
        fi
        ;;
    "custom")
        echo "=== 自定义参数模式 ==="
        check_service || exit 1
        shift  # 移除第一个参数
        python3 "$SIMULATOR" "$@"
        ;;
    "help"|*)
        show_help
        ;;
esac 