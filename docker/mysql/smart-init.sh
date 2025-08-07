#!/bin/bash
# MySQL智能数据导入脚本

set -e

echo "🔍 检查客户端数据..."

CLIENT_DATA_DIR="/docker-entrypoint-initdb.d/client"
BUILTIN_DATA_DIR="/docker-entrypoint-initdb.d"

# 检查客户端是否提供了自定义数据
if [ -f "${CLIENT_DATA_DIR}/data.sql" ]; then
    echo "✅ 发现客户端数据文件，使用客户端数据"
    echo "📂 客户端数据: ${CLIENT_DATA_DIR}/data.sql"
    
    # 禁用内置数据
    if [ -f "${BUILTIN_DATA_DIR}/01-builtin-data.sql" ]; then
        mv "${BUILTIN_DATA_DIR}/01-builtin-data.sql" "${BUILTIN_DATA_DIR}/01-builtin-data.sql.disabled"
        echo "🚫 已禁用内置数据文件"
    fi
    
    # 使用客户端数据
    cp "${CLIENT_DATA_DIR}/data.sql" "${BUILTIN_DATA_DIR}/01-client-data.sql"
    echo "📋 已应用客户端数据文件"
    
else
    echo "📦 未发现客户端数据，使用内置数据"
    echo "📂 内置数据: ${BUILTIN_DATA_DIR}/01-builtin-data.sql"
fi

# 检查客户端admin配置
if [ -f "${CLIENT_DATA_DIR}/admin.sql" ]; then
    echo "✅ 发现客户端admin配置，使用客户端配置"
    
    # 禁用内置admin配置（注：内置admin已包含在主数据文件中）
    if [ -f "${BUILTIN_DATA_DIR}/02-builtin-admin.sql" ]; then
        mv "${BUILTIN_DATA_DIR}/02-builtin-admin.sql" "${BUILTIN_DATA_DIR}/02-builtin-admin.sql.disabled"
        echo "🚫 已禁用内置admin配置"
    fi
    
    # 使用客户端admin配置
    cp "${CLIENT_DATA_DIR}/admin.sql" "${BUILTIN_DATA_DIR}/02-client-admin.sql"
    echo "👤 已应用客户端admin配置"
else
    echo "👤 未发现客户端admin配置，使用内置配置（admin用户已包含在主数据文件中）"
fi

echo "🎉 数据导入配置完成" 