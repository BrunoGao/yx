#!/bin/bash
# MySQL容器权限自动修复入口脚本 - 确保重启安全

set -e

echo "🔧 MySQL容器启动 - 自动修复权限..."

# 创建必要目录
mkdir -p /var/lib/mysql /var/log/mysql /backup

# 清理锁定和错误文件
echo "🧹 清理MySQL锁定文件..."
rm -f /var/lib/mysql/mysql.sock* /var/lib/mysql/mysqld*.err /var/lib/mysql/auto.cnf 2>/dev/null || true
rm -f /var/lib/mysql/*.pid /var/lib/mysql/*.lock 2>/dev/null || true

# 修复权限 - 确保mysql用户可以写入
echo "🔐 修复数据目录权限..."
chown -R mysql:mysql /var/lib/mysql /var/log/mysql /backup 2>/dev/null || {
    echo "⚠️ chown失败，使用chmod备用方案..."
    chmod -R 777 /var/lib/mysql /var/log/mysql /backup
}

# 设置正确的目录权限
chmod 755 /var/lib/mysql /var/log/mysql /backup

# 特殊处理：如果数据目录为空或损坏，重新初始化权限
if [ ! -d "/var/lib/mysql/mysql" ] || [ ! -f "/var/lib/mysql/mysql/user.MYD" ]; then
    echo "📁 首次初始化或数据目录损坏，设置初始化权限..."
    chmod 777 /var/lib/mysql
    # 确保mysql用户可以创建文件
    touch /var/lib/mysql/test_write && rm -f /var/lib/mysql/test_write || {
        echo "⚠️ 写入测试失败，强制设置777权限"
        chmod -R 777 /var/lib/mysql
    }
fi

# 检查磁盘空间
df -h /var/lib/mysql | tail -1 | awk '{
    if ($5+0 > 95) print "⚠️ 磁盘空间不足: " $5 " 已使用"
    else print "💾 磁盘空间充足: " $4 " 可用"
}'

echo "✅ MySQL权限修复完成"

# 执行原始入口脚本
exec docker-entrypoint.sh "$@" 