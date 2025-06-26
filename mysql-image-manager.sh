#!/bin/bash
# MySQL镜像管理工具 v1.0.0
# 管理本地MySQL镜像缓存，确保构建时使用本地镜像

set -e

echo "🐳 MySQL镜像管理工具"
echo "=============================="

# 显示帮助信息
show_help() {
    echo "使用方法:"
    echo "  $0 check        # 检查本地MySQL镜像状态"
    echo "  $0 pull [arch]  # 拉取MySQL镜像到本地 (默认: amd64,arm64)"
    echo "  $0 clean        # 清理旧的MySQL镜像"
    echo "  $0 info         # 显示MySQL镜像详细信息"
    echo "  $0 list         # 列出所有MySQL相关镜像"
    echo "  $0 multiarch    # 检查多架构支持情况"
    echo ""
    echo "架构参数示例:"
    echo "  $0 pull amd64           # 仅拉取AMD64架构"
    echo "  $0 pull arm64           # 仅拉取ARM64架构"
    echo "  $0 pull amd64,arm64     # 拉取两种架构"
    echo ""
}

# 检查本地MySQL镜像
check_mysql_images() {
    echo "🔍 检查本地MySQL镜像..."
    echo ""
    
    local mysql_tags=("mysql:8.0" "mysql:8.0-debian" "mysql:latest")
    local found_any=false
    
    for tag in "${mysql_tags[@]}"; do
        echo -n "  $tag: "
        if docker image inspect "$tag" >/dev/null 2>&1; then
            local size=$(docker image inspect "$tag" --format='{{.Size}}' | awk '{printf "%.1f MB", $1/1024/1024}')
            local arch=$(docker image inspect "$tag" --format='{{.Architecture}}')
            local created=$(docker image inspect "$tag" --format='{{.Created}}' | cut -c1-19 | tr 'T' ' ')
            echo "✅ 存在 (架构: $arch, 大小: $size, 创建: $created)"
            found_any=true
        else
            echo "❌ 不存在"
        fi
    done
    
    echo ""
    if [ "$found_any" = true ]; then
        echo "✅ 发现本地MySQL镜像，构建时将使用本地缓存"
        echo "💡 提示: 如需多架构支持，请使用 '$0 pull amd64,arm64'"
    else
        echo "⚠️ 未发现本地MySQL镜像，建议运行: $0 pull"
    fi
}

# 拉取MySQL镜像（支持多架构）
pull_mysql_images() {
    local arch_param="${1:-amd64,arm64}"  # 默认拉取amd64和arm64
    echo "📥 拉取MySQL镜像到本地 (架构: $arch_param)..."
    echo ""
    
    # 如果是多架构，为每个架构单独拉取
    if [[ "$arch_param" == *","* ]]; then
        echo "🏗️ 多架构拉取模式"
        IFS=',' read -ra archs <<< "$arch_param"
        
        for arch in "${archs[@]}"; do
            arch=$(echo "$arch" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')  # 去除空格
            echo "📥 拉取 $arch 架构的MySQL镜像..."
            
            if docker pull --platform "linux/$arch" mysql:8.0; then
                echo "✅ 成功拉取 mysql:8.0 ($arch)"
            else
                echo "⚠️ 拉取 mysql:8.0 ($arch) 失败，尝试备选版本..."
                if docker pull --platform "linux/$arch" mysql:8.0-debian; then
                    echo "✅ 成功拉取 mysql:8.0-debian ($arch)"
                else
                    echo "❌ 拉取 $arch 架构镜像失败"
                fi
            fi
        done
    else
        echo "🏗️ 单架构拉取模式: $arch_param"
        if docker pull --platform "linux/$arch_param" mysql:8.0; then
            echo "✅ 成功拉取 mysql:8.0 ($arch_param)"
        else
            echo "⚠️ 拉取 mysql:8.0 失败，尝试备选版本..."
            if docker pull --platform "linux/$arch_param" mysql:8.0-debian; then
                echo "✅ 成功拉取 mysql:8.0-debian ($arch_param)"
            else
                echo "❌ 拉取失败"
                echo "💡 请检查网络连接和Docker镜像加速器配置"
                return 1
            fi
        fi
    fi
    
    echo ""
    echo "🎉 MySQL镜像拉取完成！"
    check_mysql_images
}

# 清理MySQL镜像
clean_mysql_images() {
    echo "🧹 清理MySQL镜像..."
    echo ""
    
    # 显示将要删除的镜像
    echo "📋 将要删除的MySQL镜像："
    docker images mysql --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null || true
    echo ""
    
    read -p "确认删除所有MySQL镜像？(y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo "🗑️ 删除MySQL镜像..."
        docker rmi $(docker images mysql -q) 2>/dev/null || echo "⚠️ 没有MySQL镜像需要删除"
        echo "✅ 清理完成"
    else
        echo "❌ 取消清理操作"
    fi
}

# 显示MySQL镜像详细信息
show_mysql_info() {
    echo "📊 MySQL镜像详细信息..."
    echo ""
    
    local mysql_images=$(docker images mysql --format "{{.Repository}}:{{.Tag}}" 2>/dev/null)
    
    if [ -z "$mysql_images" ]; then
        echo "❌ 未发现本地MySQL镜像"
        return 1
    fi
    
    while IFS= read -r image; do
        if [ -n "$image" ]; then
            echo "🔍 镜像: $image"
            docker image inspect "$image" --format '
  大小: {{printf "%.1f MB" (div .Size 1048576.0)}}
  创建时间: {{.Created}}
  架构: {{.Architecture}}
  操作系统: {{.Os}}
  层数: {{len .RootFS.Layers}}
  ---'
        fi
    done <<< "$mysql_images"
}

# 列出所有MySQL相关镜像
list_mysql_images() {
    echo "📋 所有MySQL相关镜像..."
    echo ""
    
    # 列出MySQL镜像（包含架构信息）
    echo "镜像列表："
    docker images mysql --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null || echo "❌ 未发现MySQL镜像"
    
    echo ""
    echo "🏗️ 架构详情："
    local mysql_images=$(docker images mysql --format "{{.Repository}}:{{.Tag}}" 2>/dev/null)
    if [ -n "$mysql_images" ]; then
        while IFS= read -r image; do
            if [ -n "$image" ]; then
                local arch=$(docker image inspect "$image" --format='{{.Architecture}}' 2>/dev/null || echo "未知")
                echo "  $image -> $arch"
            fi
        done <<< "$mysql_images"
    fi
    
    echo ""
    echo "💾 总占用空间："
    docker images mysql --format "{{.Size}}" 2>/dev/null | awk '{sum += $1} END {printf "%.1f MB\n", sum/1024/1024}' || echo "0 MB"
}

# 检查多架构支持情况
check_multiarch_support() {
    echo "🏗️ 检查MySQL镜像多架构支持..."
    echo ""
    
    local test_images=("mysql:8.0" "mysql:8.0-debian" "mysql:latest")
    
    for image in "${test_images[@]}"; do
        echo "🔍 检查镜像: $image"
        
        # 检查远程镜像的多架构支持
        if command -v docker buildx >/dev/null 2>&1; then
            echo "  远程多架构支持:"
            if docker buildx imagetools inspect "$image" 2>/dev/null | grep -E "linux/(amd64|arm64)" | sed 's/^/    /'; then
                true
            else
                echo "    ❌ 无法获取远程架构信息"
            fi
        else
            echo "    ⚠️ 需要docker buildx支持"
        fi
        
        # 检查本地镜像
        echo "  本地镜像状态:"
        if docker image inspect "$image" >/dev/null 2>&1; then
            local arch=$(docker image inspect "$image" --format='{{.Architecture}}')
            echo "    ✅ 存在 (架构: $arch)"
        else
            echo "    ❌ 不存在"
        fi
        echo ""
    done
    
    echo "💡 建议:"
    echo "  • 对于AMD64+ARM64支持: $0 pull amd64,arm64"
    echo "  • 对于仅ARM64支持: $0 pull arm64"
    echo "  • 对于仅AMD64支持: $0 pull amd64"
}

# 主程序
case "${1:-help}" in
    "check")
        check_mysql_images
        ;;
    "pull")
        pull_mysql_images "$2"
        ;;
    "clean")
        clean_mysql_images
        ;;
    "info")
        show_mysql_info
        ;;
    "list")
        list_mysql_images
        ;;
    "multiarch")
        check_multiarch_support
        ;;
    "help"|*)
        show_help
        ;;
esac 