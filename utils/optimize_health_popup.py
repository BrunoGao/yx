#!/usr/bin/env python3
"""健康弹出信息优化便捷执行脚本"""
import sys,os
bigscreen_path = os.path.join(os.path.dirname(__file__), '..', 'ljwx-bigscreen', 'bigscreen', 'bigScreen')
sys.path.insert(0, bigscreen_path)

def optimize_health_popup():
    """优化健康弹出信息显示"""
    try:
        import health_popup_integration
        integrate_health_popup_optimization = health_popup_integration.integrate_health_popup_optimization
        
        print("🚀 开始优化健康呼吸点弹出信息...")
        integrate_health_popup_optimization()
        print("✅ 健康弹出信息优化完成!")
        
        print("\n📋 优化内容:")
        print("• 🎨 现代化UI设计 - 渐变背景、毛玻璃效果、动画过渡")
        print("• 📊 智能健康状态指示 - 根据数值自动判断健康等级")
        print("• 🎯 分类指标显示 - 主要生理指标与次要指标分组")
        print("• 💫 交互动效 - 悬停效果、脉冲动画、加载动画")
        print("• 📱 响应式设计 - 适配不同屏幕尺寸")
        print("• ⏰ 智能时间显示 - 相对时间格式(几分钟前、几小时前)")
        print("• 🌈 健康状态颜色编码 - 优秀(蓝)、良好(绿)、正常(黄)、警告(橙)、危险(红)")
        print("• 🔧 增强功能按钮 - 详细分析、一键处理、优雅关闭")
        
        print("\n🎯 使用说明:")
        print("• 点击地图上的健康呼吸点查看优化后的弹出窗口")
        print("• 健康指标会根据正常范围自动显示颜色状态")
        print("• 支持告警点和健康点两种不同的显示样式")
        print("• 位置信息会自动获取并显示详细地址")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保在正确的目录下运行此脚本")
    except Exception as e:
        print(f"❌ 优化过程中出现错误: {e}")

def restore_health_popup():
    """恢复原始健康弹出信息"""
    try:
        import health_popup_integration
        restore_original_health_popup = health_popup_integration.restore_original_health_popup
        
        print("🔄 开始恢复原始健康弹出信息...")
        restore_original_health_popup()
        print("✅ 已恢复原始健康弹出信息!")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
    except Exception as e:
        print(f"❌ 恢复过程中出现错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_health_popup()
    else:
        optimize_health_popup() 