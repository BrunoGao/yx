#!/bin/bash
# Created Time:    2025-06-09 07:43:24
# Modified Time:   2025-07-17 06:01:37
#!/bin/bash
# 灵境万象系统 - 本地多架构构建脚本 v1.2.6

set -e

echo "🏗️ 灵境万象系统 - 本地多架构构建 v1.2.6"

# 加载版本配置
if [ -f "monitoring-versions.env" ]; then
    source monitoring-versions.env
    echo "📋 已加载版本配置文件"
else
    echo "⚠️ 未找到版本配置文件，使用默认配置"
    # 默认配置
    LJWX_VERSION="1.2.18"
    LJWX_GRAFANA_VERSION="1.2.6"
    LJWX_PROMETHEUS_VERSION="1.2.6"
    LJWX_LOKI_VERSION="1.2.6"
    LJWX_PROMTAIL_VERSION="1.2.6"
    LJWX_ALERTMANAGER_VERSION="1.2.6"
    LOCAL_REGISTRY="14.127.218.229:5001/ljwx"  # 本地镜像服务器
    ALIYUN_REGISTRY="crpi-yilnm6upy4pmbp67.cn-shenzhen.personal.cr.aliyuncs.com/ljwx"  # 阿里云镜像仓库
    REGISTRY="${LOCAL_REGISTRY}"  # 默认使用本地镜像服务器
    PLATFORMS="linux/amd64,linux/arm64"  # 多架构构建
fi

# 构建器配置
BUILDER_NAME="multiarch-builder"

# 多架构构建模式配置  
LOCAL_BUILD=${LOCAL_BUILD:-true}  # 默认本地构建(避免网络问题)
PUSH_TO_REGISTRY=${PUSH_TO_REGISTRY:-true}  # 默认推送到镜像仓库
USE_LOCAL_REGISTRY=${USE_LOCAL_REGISTRY:-true}  # 默认使用本地镜像服务器

# 设置代理（网络优化）
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 生成数据库升级脚本
generate_upgrade_script() {
    # 加载版本配置
    if [ -f "database_versions.env" ]; then
        source database_versions.env
    else
        echo "❌ 未找到数据库版本配置文件"
        return 1
    fi
    
    local upgrade_script="database/upgrades/upgrade_${PREVIOUS_DB_VERSION}_to_${CURRENT_DB_VERSION}.sql"
    
    echo "🔄 生成数据库升级脚本: ${PREVIOUS_DB_VERSION} -> ${CURRENT_DB_VERSION}"
    
    # 创建升级脚本
    cat > "$upgrade_script" << EOF
-- 灵境万象系统数据库升级脚本
-- 版本: ${PREVIOUS_DB_VERSION} -> ${CURRENT_DB_VERSION}
-- 生成时间: $(date)
-- 说明: 自动生成的数据库升级脚本，请在生产环境使用前仔细测试

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 检查当前数据库版本
SELECT '开始升级数据库...' as message;

-- 创建版本管理表（如果不存在）
CREATE TABLE IF NOT EXISTS \`db_version\` (
  \`id\` int NOT NULL AUTO_INCREMENT,
  \`version\` varchar(20) NOT NULL COMMENT '版本号',
  \`description\` varchar(255) DEFAULT NULL COMMENT '版本描述',
  \`created_at\` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (\`id\`),
  UNIQUE KEY \`uk_version\` (\`version\`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据库版本管理表';

-- 插入当前版本记录
INSERT IGNORE INTO \`db_version\` (\`version\`, \`description\`) VALUES ('${CURRENT_DB_VERSION}', '数据统计优化');

EOF

    # 使用mysqldiff生成结构差异（如果可用）
    if command -v mysqldiff &> /dev/null; then
        echo "🔍 使用mysqldiff生成结构差异..."
        {
            echo "-- 结构变更 (自动生成)"
            echo "-- 注意: 以下SQL语句为自动生成，请仔细检查后执行"
            echo ""
            mysqldiff --server1=root:${DB_PASSWORD}@${DB_HOST}:3306 \
                     --server2=root:${DB_PASSWORD}@${DB_HOST}:3306 \
                     --difftype=sql \
                     --skip-data-check \
                     ${DB_NAME}:${DB_NAME} || echo "-- 无结构差异或工具不可用"
        } >> "$upgrade_script"
    else
        echo "⚠️ mysqldiff工具不可用，生成基础升级脚本..."
        cat >> "$upgrade_script" << EOF
-- 手动添加结构变更
-- 请根据实际情况添加以下类型的语句:
-- ALTER TABLE table_name ADD COLUMN new_column VARCHAR(255);
-- CREATE INDEX idx_name ON table_name (column_name);
-- 等等...

EOF
    fi
    
    # 添加脚本结尾
    cat >> "$upgrade_script" << EOF

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 升级完成
SELECT CONCAT('数据库升级完成: ${PREVIOUS_DB_VERSION} -> ${CURRENT_DB_VERSION}') as message;
EOF

    echo "✅ 升级脚本生成完成: $upgrade_script"
    echo "📝 客户使用方法:"
    echo "   mysql -u用户名 -p密码 数据库名 < $upgrade_script"
}

# 导出MySQL数据
export_mysql_data() {
    echo "🗄️ 导出MySQL数据到data.sql..."
    
    # MySQL连接参数
    local mysql_host="127.0.0.1"
    local mysql_user="root"
    local mysql_password="123456"
    local mysql_database="test"
    local target_database="lj-06"
    
    # 检查mysqldump是否可用
    if ! command -v mysqldump &> /dev/null; then
        echo "❌ mysqldump未找到，请安装MySQL客户端"
        exit 1
    fi
    
    # 测试MySQL连接
    if ! mysql -h"$mysql_host" -u"$mysql_user" -p"$mysql_password" -e "SELECT 1;" "$mysql_database" &> /dev/null; then
        echo "❌ MySQL连接失败，请检查连接参数"
        exit 1
    fi
    
    echo "✅ MySQL连接成功，开始导出数据..."
    
    # 导出数据并添加建库语句
    {
        echo "-- 灵境万象系统数据库初始化脚本"
        echo "-- 导出时间: $(date)"
        echo "-- 源数据库: $mysql_database@$mysql_host"
        echo "-- 目标数据库: $target_database"
        echo ""
        echo "-- 创建数据库"
        echo "CREATE DATABASE IF NOT EXISTS \`$target_database\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        echo "USE \`$target_database\`;"
        echo ""
        
        # 导出所有数据、视图、存储过程、函数、事件(定时器)
        mysqldump -h"$mysql_host" -u"$mysql_user" -p"$mysql_password" \
            --single-transaction \
            --routines \
            --triggers \
            --events \
            --complete-insert \
            --comments \
            --add-drop-table \
            --set-charset \
            --default-character-set=utf8mb4 \
            "$mysql_database"
    } > data.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ 数据导出成功: data.sql"
        echo "📊 导出统计:"
        echo "   - 文件大小: $(du -h data.sql | cut -f1)"
        echo "   - 行数: $(wc -l < data.sql)"
        echo "   - 包含内容: 表结构、数据、视图、存储过程、函数、触发器、事件"
    else
        echo "❌ 数据导出失败"
        exit 1
    fi
}

# 镜像仓库登录函数
login_registry() {
    if [ "$PUSH_TO_REGISTRY" = "true" ]; then
        if [ "$USE_LOCAL_REGISTRY" = "true" ]; then
            echo "🔐 配置本地镜像仓库 14.127.218.229:5001..."
            # 本地镜像服务器通常不需要认证，但检查连接性
            if curl -f -s "http://14.127.218.229:5001/v2/" > /dev/null; then
                echo "✅ 本地镜像服务器连接成功"
            else
                echo "❌ 本地镜像服务器 14.127.218.229:5001 无法访问"
                echo "💡 请确保:"
                echo "   1. 镜像服务器正在运行"
                echo "   2. 网络连接正常"
                echo "   3. 防火墙允许 5001 端口"
                exit 1
            fi
        elif [[ "$REGISTRY" == *"aliyuncs.com"* ]]; then
            echo "🔐 登录阿里云Docker镜像仓库..."
            echo "admin123" | docker login --username brunogao --password-stdin crpi-yilnm6upy4pmbp67.cn-shenzhen.personal.cr.aliyuncs.com
            if [ $? -eq 0 ]; then
                echo "✅ 阿里云登录成功"
            else
                echo "❌ 阿里云登录失败，请检查凭据"
                exit 1
            fi
        fi
    fi
}

# 检查参数
if [ $# -eq 0 ]; then
    echo "📋 使用方法:"
    echo "   $0 all                    # 构建所有镜像(应用+监控)"
    echo "   $0 apps                   # 构建应用镜像"
    echo "   $0 monitoring             # 构建监控镜像"
    echo ""
    echo "🔧 应用组件:"
    echo "   $0 mysql                  # 构建MySQL镜像"
    echo "   $0 redis                  # 构建Redis镜像"
    echo "   $0 boot                   # 构建Boot镜像"
    echo "   $0 bigscreen              # 构建Bigscreen镜像"
    echo "   $0 admin                  # 构建Admin镜像"
    echo ""
    echo "📊 监控组件:"
    echo "   $0 grafana                # 构建定制化Grafana"
    echo "   $0 prometheus             # 构建定制化Prometheus"
    echo "   $0 loki                   # 构建定制化Loki"
    echo "   $0 promtail               # 构建定制化Promtail"
    echo "   $0 alertmanager           # 构建定制化AlertManager"
    echo ""
    echo "🎯 构建模式:"
    echo "   LOCAL_BUILD=false             # 多架构构建(默认)"
    echo "   PUSH_TO_REGISTRY=true         # 推送到镜像仓库(默认)"
    echo "   USE_LOCAL_REGISTRY=true       # 使用本地镜像服务器(默认)"
    echo "   USE_LOCAL_REGISTRY=false      # 使用阿里云镜像仓库"
    echo ""
    echo "💡 当前架构: $PLATFORMS"
    echo "📊 当前版本: 应用 $LJWX_VERSION, 监控 $LJWX_GRAFANA_VERSION"
    echo "🏷️  当前仓库: $([ "$USE_LOCAL_REGISTRY" = "true" ] && echo "本地 $LOCAL_REGISTRY" || echo "阿里云 $ALIYUN_REGISTRY")"
    echo "🏷️  镜像前缀: $REGISTRY"
    exit 1
fi

# 初始化多架构构建器(仅在需要时)
init_buildx() {
    if [ "$LOCAL_BUILD" = "true" ] && [ "$PLATFORMS" = "linux/amd64" ]; then
        echo "🔧 使用本地Docker构建..."
        return 0
    fi
    
    echo "🔧 初始化多架构构建器..."
    if ! docker buildx inspect $BUILDER_NAME >/dev/null 2>&1; then
        docker buildx create --name $BUILDER_NAME --use
    else
        docker buildx use $BUILDER_NAME
    fi
    docker buildx inspect --bootstrap
}

# 构建应用镜像函数
build_app_image() {
    local image=$1
    local image_name="ljwx-$image"
    local tag="$REGISTRY/$image_name:$LJWX_VERSION"
    local latest_tag="$REGISTRY/$image_name:latest"
    
    echo "🔨 构建应用镜像 $image_name (架构: $PLATFORMS)..."
    
    # 构建参数
    local build_args=""
    if [ "$LOCAL_BUILD" = "true" ] && [ "$PLATFORMS" = "linux/amd64" ]; then
        # 本地构建
        build_args="build"
    else
        # 多架构构建
        build_args="buildx build --platform $PLATFORMS"
        if [ "$PUSH_TO_REGISTRY" = "true" ]; then
            build_args="$build_args --push"
        else
            build_args="$build_args --load"
        fi
    fi
    
    case $image in
        "mysql")
            echo "🗄️ 构建MySQL镜像前先导出最新数据..."
            export_mysql_data
            echo "🔄 生成数据库升级脚本..."
            # 备份当前data.sql作为对比基准
            if [ -f "data.sql" ]; then
                cp data.sql data.sql.bak
                echo "📁 备份当前data.sql -> data.sql.bak"
            fi
            generate_upgrade_script
            # 尝试使用Python高级分析器
            if command -v python3 &> /dev/null && pip3 show mysql-connector-python &> /dev/null; then
                echo "🐍 使用Python高级分析器生成升级脚本..."
                python3 database/generate_upgrade_advanced.py
            fi
            echo "🧹 清除缓存以确保使用最新的data.sql..."
            if [ "$LOCAL_BUILD" = "true" ] && [ "$PLATFORMS" = "linux/amd64" ]; then
                docker build --no-cache -t $tag -t $latest_tag . -f docker/mysql/Dockerfile
            else
                docker $build_args --no-cache -t $tag -t $latest_tag . -f docker/mysql/Dockerfile
            fi
            ;;
        "redis")
            if [ "$LOCAL_BUILD" = "true" ] && [ "$PLATFORMS" = "linux/amd64" ]; then
                docker build -t $tag -t $latest_tag . -f docker/redis/Dockerfile
            else
                docker $build_args -t $tag -t $latest_tag . -f docker/redis/Dockerfile
            fi
            ;;
        "boot")
            if [ "$LOCAL_BUILD" = "true" ] && [ "$PLATFORMS" = "linux/amd64" ]; then
                docker build -t $tag -t $latest_tag . -f ljwx-boot/ljwx-boot-admin/Dockerfile.prod
            else
                docker $build_args -t $tag -t $latest_tag . -f ljwx-boot/ljwx-boot-admin/Dockerfile.prod
            fi
            ;;
        "bigscreen")
            if [ "$LOCAL_BUILD" = "true" ] && [ "$PLATFORMS" = "linux/amd64" ]; then
                docker build -t $tag -t $latest_tag ljwx-bigscreen/bigscreen/ -f ljwx-bigscreen/bigscreen/Dockerfile.multiarch
            else
                docker $build_args -t $tag -t $latest_tag ljwx-bigscreen/bigscreen/ -f ljwx-bigscreen/bigscreen/Dockerfile.multiarch
            fi
            ;;
        "admin")
            if [ "$LOCAL_BUILD" = "true" ] && [ "$PLATFORMS" = "linux/amd64" ]; then
                docker build -t $tag -t $latest_tag ljwx-admin/ -f ljwx-admin/Dockerfile.prod
            else
                docker $build_args -t $tag -t $latest_tag ljwx-admin/ -f ljwx-admin/Dockerfile.prod
            fi
            ;;
        *)
            echo "❌ 未知应用镜像: $image"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        echo "✅ $image_name 应用镜像构建成功"
        echo "🏷️  镜像标签: $tag, $latest_tag"
    else
        echo "❌ $image_name 应用镜像构建失败"
        return 1
    fi
}

# 构建监控镜像函数
build_monitoring_image() {
    local image=$1
    local image_name="ljwx-$image"
    
    # 根据组件设置版本
    case $image in
        "grafana")
            local version=$LJWX_GRAFANA_VERSION
            ;;
        "prometheus")
            local version=$LJWX_PROMETHEUS_VERSION
            ;;
        "loki")
            local version=$LJWX_LOKI_VERSION
            ;;
        "promtail")
            local version=$LJWX_PROMTAIL_VERSION
            ;;
        "alertmanager")
            local version=$LJWX_ALERTMANAGER_VERSION
            ;;
        *)
            echo "❌ 未知监控镜像: $image"
            return 1
            ;;
    esac
    
    local tag="$REGISTRY/$image_name:$version"
    local latest_tag="$REGISTRY/$image_name:latest"
    
    echo "🔨 构建监控镜像 $image_name:$version (架构: $PLATFORMS)..."
    
    # 构建镜像
    if [ "$LOCAL_BUILD" = "true" ] && [ "$PLATFORMS" = "linux/amd64" ]; then
        docker build \
            --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
            --build-arg VERSION="$version" \
            -t $tag -t $latest_tag \
            . -f docker/$image/Dockerfile
    else
        docker buildx build --platform $PLATFORMS \
            --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
            --build-arg VERSION="$version" \
            -t $tag -t $latest_tag \
            $([ "$PUSH_TO_REGISTRY" = "true" ] && echo "--push" || echo "--load") \
            . -f docker/$image/Dockerfile
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ $image_name:$version 监控镜像构建成功"
        echo "🏷️  镜像标签: $tag, $latest_tag"
    else
        echo "❌ $image_name:$version 监控镜像构建失败"
        return 1
    fi
}

# 构建所有应用镜像
build_all_apps() {
    echo "🚀 开始构建所有应用镜像..."
    
    local app_images=("mysql" "redis" "boot" "bigscreen" "admin")
    
    for image in "${app_images[@]}"; do
        build_app_image "$image"
        echo ""
    done
}

# 构建所有监控镜像
build_all_monitoring() {
    echo "📊 开始构建所有监控镜像..."
    
    local monitoring_images=("grafana" "prometheus" "loki" "promtail" "alertmanager")
    
    for image in "${monitoring_images[@]}"; do
        build_monitoring_image "$image"
        echo ""
    done
}

# 构建所有镜像
build_all() {
    echo "🏗️ 开始构建所有镜像(应用+监控)..."
    echo ""
    
    # 先构建应用镜像
    build_all_apps
    
    echo "🔄 应用镜像构建完成，开始构建监控镜像..."
    echo ""
    
    # 再构建监控镜像
    build_all_monitoring
}

# 显示构建总结
show_summary() {
    echo ""
    echo "🎉 本地构建完成！"
    echo ""
    echo "📊 构建摘要:"
    echo "   应用版本: $LJWX_VERSION"
    echo "   监控版本: $LJWX_GRAFANA_VERSION"
    echo "   构建架构: $PLATFORMS"
    echo "   镜像前缀: $REGISTRY"
    echo "   构建模式: $([ "$LOCAL_BUILD" = "true" ] && echo "本地构建" || echo "多架构构建")"
    echo ""
    echo "🔍 查看本地镜像:"
    echo "   docker images | grep $REGISTRY"
    echo ""
    
    if [[ " $@ " =~ " all " ]] || [[ " $@ " =~ " apps " ]]; then
        echo "   # 应用镜像"
        echo "   docker images $REGISTRY/ljwx-mysql"
        echo "   docker images $REGISTRY/ljwx-redis"
        echo "   docker images $REGISTRY/ljwx-boot"
        echo "   docker images $REGISTRY/ljwx-bigscreen"
        echo "   docker images $REGISTRY/ljwx-admin"
    fi
    
    if [[ " $@ " =~ " all " ]] || [[ " $@ " =~ " monitoring " ]]; then
        echo "   # 监控镜像"
        echo "   docker images $REGISTRY/ljwx-grafana"
        echo "   docker images $REGISTRY/ljwx-prometheus"
        echo "   docker images $REGISTRY/ljwx-loki"
        echo "   docker images $REGISTRY/ljwx-promtail"
        echo "   docker images $REGISTRY/ljwx-alertmanager"
    fi
    
    echo ""
    if [ "$USE_LOCAL_REGISTRY" = "true" ]; then
        echo "🚀 推送到本地镜像服务器的镜像:"
    else
        echo "🚀 推送到阿里云的镜像:"
    fi
    if [[ " $@ " =~ " all " ]] || [[ " $@ " =~ " apps " ]]; then
        echo "   $REGISTRY/ljwx-mysql:$LJWX_VERSION"
        echo "   $REGISTRY/ljwx-redis:$LJWX_VERSION"
        echo "   $REGISTRY/ljwx-boot:$LJWX_VERSION"
        echo "   $REGISTRY/ljwx-bigscreen:$LJWX_VERSION"
        echo "   $REGISTRY/ljwx-admin:$LJWX_VERSION"
    fi
    echo ""
    if [ "$USE_LOCAL_REGISTRY" = "true" ]; then
        echo "   本地拉取命令: docker pull $REGISTRY/ljwx-xxx:$LJWX_VERSION"
        echo "   远程拉取命令: docker pull 14.127.218.229:5001/ljwx/ljwx-xxx:$LJWX_VERSION"
    else
        echo "   客户可使用命令拉取: docker pull $REGISTRY/ljwx-xxx:$LJWX_VERSION"
    fi
}

# 设置镜像仓库
setup_registry() {
    # 确保本地和阿里云仓库配置存在
    if [ -z "$LOCAL_REGISTRY" ]; then
        LOCAL_REGISTRY="14.127.218.229:5001/ljwx"
    fi
    if [ -z "$ALIYUN_REGISTRY" ]; then
        ALIYUN_REGISTRY="crpi-yilnm6upy4pmbp67.cn-shenzhen.personal.cr.aliyuncs.com/ljwx"
    fi
    
    if [ "$USE_LOCAL_REGISTRY" = "true" ]; then
        REGISTRY="$LOCAL_REGISTRY"
        echo "📍 使用本地镜像服务器: $REGISTRY"
    else
        REGISTRY="$ALIYUN_REGISTRY"
        echo "📍 使用阿里云镜像仓库: $REGISTRY"
    fi
}

# 主程序
main() {
    # 设置镜像仓库
    setup_registry
    
    # 登录镜像仓库(如果需要推送)
    login_registry
    
    # 初始化构建器
    init_buildx
    
    case "$1" in
        "all")
            build_all
            ;;
        "apps")
            build_all_apps
            ;;
        "monitoring")
            build_all_monitoring
            ;;
        "mysql"|"redis"|"boot"|"bigscreen"|"admin")
            for image in "$@"; do
                build_app_image "$image"
                echo ""
            done
            ;;
        "grafana"|"prometheus"|"loki"|"promtail"|"alertmanager")
            for image in "$@"; do
                build_monitoring_image "$image"
                echo ""
            done
            ;;
        *)
            # 混合构建：检查每个参数类型
            for image in "$@"; do
                case $image in
                    "mysql"|"redis"|"boot"|"bigscreen"|"admin")
                        build_app_image "$image"
                        ;;
                    "grafana"|"prometheus"|"loki"|"promtail"|"alertmanager")
                        build_monitoring_image "$image"
                        ;;
                    *)
                        echo "❌ 未知镜像类型: $image"
                        ;;
                esac
                echo ""
            done
            ;;
    esac
    
    # 显示构建总结
    show_summary "$@"
}

# 执行主程序
main "$@"
