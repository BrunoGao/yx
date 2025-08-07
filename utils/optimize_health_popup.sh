#!/bin/bash
# 健康弹出信息优化脚本

cd "$(dirname "$0")"

echo "🏥 健康呼吸点弹出信息优化工具"
echo "================================"

case "${1:-optimize}" in
    "optimize"|"")
        echo "🚀 开始优化健康弹出信息显示..."
        python3 optimize_health_popup.py
        ;;
    "restore")
        echo "🔄 恢复原始健康弹出信息..."
        python3 optimize_health_popup.py restore
        ;;
    "help"|"-h"|"--help")
        echo "使用方法:"
        echo "  $0 [optimize]  # 优化健康弹出信息(默认)"
        echo "  $0 restore     # 恢复原始健康弹出信息"
        echo "  $0 help        # 显示帮助信息"
        echo ""
        echo "优化功能:"
        echo "• 🎨 现代化UI设计 - 渐变背景、毛玻璃效果"
        echo "• 📊 智能健康状态指示 - 自动判断健康等级"
        echo "• 🎯 分类指标显示 - 主要/次要指标分组"
        echo "• 💫 交互动效 - 悬停效果、动画过渡"
        echo "• 📱 响应式设计 - 适配不同屏幕"
        echo "• ⏰ 智能时间显示 - 相对时间格式"
        echo "• 🌈 健康状态颜色编码 - 五级颜色体系"
        ;;
    *)
        echo "❌ 未知参数: $1"
        echo "使用 '$0 help' 查看帮助信息"
        exit 1
        ;;
esac 