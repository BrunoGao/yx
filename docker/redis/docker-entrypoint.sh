#!/bin/sh
# Redis Docker启动脚本 - 支持环境变量配置

set -e

# 设置默认值
REDIS_PASSWORD=${REDIS_PASSWORD:-123456}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_MAXMEMORY=${REDIS_MAXMEMORY:-512mb}
REDIS_MAXMEMORY_POLICY=${REDIS_MAXMEMORY_POLICY:-allkeys-lru}

echo "🔧 Redis容器启动 - 自动修复权限和生成配置..."
echo "   密码: ${REDIS_PASSWORD}"
echo "   端口: ${REDIS_PORT}"
echo "   最大内存: ${REDIS_MAXMEMORY}"
echo "   淘汰策略: ${REDIS_MAXMEMORY_POLICY}"

# 确保目录权限正确 - 重启后自动修复
echo "🔐 修复Redis目录权限..."
mkdir -p /data /var/log/redis /backup

# 清理可能的锁定文件和错误状态
echo "🧹 清理Redis锁定文件..."
rm -f /data/dump.rdb.lock /data/redis.lock /data/*.tmp 2>/dev/null || true
rm -f /var/log/redis/*.lock 2>/dev/null || true

# 修复权限 - 确保redis用户可以写入
chown -R redis:redis /data /var/log/redis /backup 2>/dev/null || {
    echo "⚠️ chown失败，使用chmod备用方案..."
    chmod -R 777 /data /var/log/redis /backup
}

# 设置正确的目录权限
chmod 755 /data /var/log/redis /backup

# 测试写入权限
touch /data/test_write && rm -f /data/test_write || {
    echo "⚠️ Redis数据目录写入测试失败，强制设置777权限"
    chmod -R 777 /data
}

# 使用envsubst替换环境变量生成最终配置文件
envsubst < /usr/local/etc/redis/redis.conf.template > /usr/local/etc/redis/redis.conf

echo "✅ Redis配置文件生成完成"

# 如果第一个参数是redis-server，则启动Redis
if [ "$1" = 'redis-server' ]; then
    echo "🚀 启动Redis服务器..."
    exec redis-server /usr/local/etc/redis/redis.conf
fi

# 否则执行传入的命令
exec "$@" 