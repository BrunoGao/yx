#!/bin/bash
# 健康数据迁移一键执行脚本

echo "🚀 开始健康数据迁移流程..."
echo "================================================================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 检查pymysql模块
python3 -c "import pymysql" 2>/dev/null || {
    echo "❌ pymysql模块未安装，正在安装..."
    pip3 install pymysql
}

echo "📊 步骤1: 分析表结构和数据现状"
python3 analyze_table_structure.py

echo -e "\n📊 步骤2: 检查用户组织关联"
python3 check_user_org.py

echo -e "\n🔄 步骤3: 执行完整数据迁移"
python3 migrate_health_data.py

echo -e "\n🔍 步骤4: 验证迁移结果"
python3 verify_migration.py

echo -e "\n📊 步骤5: 检查数据分布"
python3 check_org_distribution.py

echo -e "\n✅ 迁移流程完成！"
echo "如有问题，可单独运行以下修复脚本："
echo "  python3 sync_partition_org_ids.py  # 同步org_id"
echo "  python3 sync_latest_data.py        # 同步最新数据" 