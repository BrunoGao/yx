#!/bin/bash
# Created Time:    2025-06-26 12:37:43
# Modified Time:   2025-06-26 12:37:52
#set -e # 这告诉bash一但有任何一个语句返回非真的值，则退出bash。
#!/bin/bash
# wait-for-it.sh - 等待服务可用的脚本（Linux兼容版）
# 支持CentOS、Ubuntu、Debian、Alpine等Linux发行版

set -e #遇到错误立即退出

WAITFORIT_cmdname=${0##*/}
WAITFORIT_QUIET=0
WAITFORIT_STRICT=0
WAITFORIT_TIMEOUT=15
WAITFORIT_HOST=""
WAITFORIT_PORT=""
WAITFORIT_CLI=""

# 错误输出函数
echoerr() { 
    if [ $WAITFORIT_QUIET -ne 1 ]; then 
        echo "$@" >&2
    fi
}

# 使用说明
usage() {
    cat << USAGE >&2
Usage:
    $WAITFORIT_cmdname host:port [-s] [-t timeout] [-- command args]
    -h HOST | --host=HOST       Host or IP under test
    -p PORT | --port=PORT       TCP port under test
    -s | --strict               Only execute subcommand if the test succeeds
    -q | --quiet                Don't output any status messages
    -t TIMEOUT | --timeout=TIMEOUT
                                Timeout in seconds, zero for no timeout
    -- COMMAND ARGS             Execute command with args after the test finishes
USAGE
    exit 1
}

# 检测网络连接工具
detect_network_tool() {
    if command -v nc >/dev/null 2>&1; then
        # 检测nc版本和参数支持
        if nc -h 2>&1 | grep -q "\-z"; then
            WAITFORIT_NC_TOOL="nc -z"
        elif nc -h 2>&1 | grep -q "scan"; then
            WAITFORIT_NC_TOOL="nc"
        else
            WAITFORIT_NC_TOOL="nc"
        fi
        echoerr "使用网络工具: $WAITFORIT_NC_TOOL"
        return 0
    elif command -v netcat >/dev/null 2>&1; then
        WAITFORIT_NC_TOOL="netcat -z"
        echoerr "使用网络工具: netcat"
        return 0
    elif command -v telnet >/dev/null 2>&1; then
        WAITFORIT_NC_TOOL="telnet"
        echoerr "使用网络工具: telnet"
        return 0
    else
        echoerr "警告: 未找到nc/netcat/telnet，将使用bash内置网络功能"
        WAITFORIT_NC_TOOL="bash"
        return 0
    fi
}

# 测试网络连接
test_connection() {
    local host=$1
    local port=$2
    
    case "$WAITFORIT_NC_TOOL" in
        "nc -z")
            nc -z "$host" "$port" >/dev/null 2>&1
            return $?
            ;;
        "nc")
            # 某些nc版本不支持-z参数
            echo "" | nc "$host" "$port" >/dev/null 2>&1
            return $?
            ;;
        "netcat -z")
            netcat -z "$host" "$port" >/dev/null 2>&1
            return $?
            ;;
        "telnet")
            # 使用telnet测试连接
            (echo "quit" | telnet "$host" "$port" 2>/dev/null | grep -q "Connected") 2>/dev/null
            return $?
            ;;
        "bash")
            # 使用bash内置网络功能
            if [ -e /dev/tcp ]; then
                exec 3<>/dev/tcp/"$host"/"$port" 2>/dev/null
                if [ $? -eq 0 ]; then
                    exec 3<&-
                    exec 3>&-
                    return 0
                else
                    return 1
                fi
            else
                # 如果/dev/tcp不可用，尝试其他方法
                timeout 1 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null
                return $?
            fi
            ;;
        *)
            echoerr "错误: 无可用的网络测试工具"
            return 1
            ;;
    esac
}

# 等待服务可用
wait_for() {
    # 检测网络工具
    detect_network_tool
    
    if [ $WAITFORIT_TIMEOUT -gt 0 ]; then
        echoerr "$WAITFORIT_cmdname: 等待 $WAITFORIT_TIMEOUT 秒连接到 $WAITFORIT_HOST:$WAITFORIT_PORT"
    else
        echoerr "$WAITFORIT_cmdname: 等待连接到 $WAITFORIT_HOST:$WAITFORIT_PORT (无超时限制)"
    fi
    
    WAITFORIT_start_ts=$(date +%s)
    
    while true; do
        if test_connection "$WAITFORIT_HOST" "$WAITFORIT_PORT"; then
            WAITFORIT_end_ts=$(date +%s)
            echoerr "$WAITFORIT_cmdname: $WAITFORIT_HOST:$WAITFORIT_PORT 在 $((WAITFORIT_end_ts - WAITFORIT_start_ts)) 秒后可用"
            return 0
        fi
        
        # 检查超时
        if [ $WAITFORIT_TIMEOUT -gt 0 ]; then
            WAITFORIT_current_ts=$(date +%s)
            if [ $((WAITFORIT_current_ts - WAITFORIT_start_ts)) -ge $WAITFORIT_TIMEOUT ]; then
                echoerr "$WAITFORIT_cmdname: 超时 - $WAITFORIT_HOST:$WAITFORIT_PORT 在 $WAITFORIT_TIMEOUT 秒内不可用"
                return 1
            fi
        fi
        
        sleep 1
    done
}

# 解析命令行参数
while [ $# -gt 0 ]; do
    case "$1" in
        *:*)
            WAITFORIT_hostport=$(echo "$1" | tr ':' ' ')
            WAITFORIT_HOST=$(echo $WAITFORIT_hostport | cut -d' ' -f1)
            WAITFORIT_PORT=$(echo $WAITFORIT_hostport | cut -d' ' -f2)
            shift 1
            ;;
        -q | --quiet)
            WAITFORIT_QUIET=1
            shift 1
            ;;
        -s | --strict)
            WAITFORIT_STRICT=1
            shift 1
            ;;
        -h)
            WAITFORIT_HOST="$2"
            if [ "$WAITFORIT_HOST" = "" ]; then 
                echoerr "错误: -h 参数需要指定主机名"
                usage
            fi
            shift 2
            ;;
        --host=*)
            WAITFORIT_HOST="${1#*=}"
            shift 1
            ;;
        -p)
            WAITFORIT_PORT="$2"
            if [ "$WAITFORIT_PORT" = "" ]; then 
                echoerr "错误: -p 参数需要指定端口号"
                usage
            fi
            shift 2
            ;;
        --port=*)
            WAITFORIT_PORT="${1#*=}"
            shift 1
            ;;
        -t)
            WAITFORIT_TIMEOUT="$2"
            if [ "$WAITFORIT_TIMEOUT" = "" ]; then 
                echoerr "错误: -t 参数需要指定超时时间"
                usage
            fi
            shift 2
            ;;
        --timeout=*)
            WAITFORIT_TIMEOUT="${1#*=}"
            shift 1
            ;;
        --)
            shift
            WAITFORIT_CLI="$@"
            break
            ;;
        --help)
            usage
            ;;
        *)
            echoerr "未知参数: $1"
            usage
            ;;
    esac
done

# 验证必需参数
if [ "$WAITFORIT_HOST" = "" ] || [ "$WAITFORIT_PORT" = "" ]; then
    echoerr "错误: 必须提供主机名和端口号"
    usage
fi

# 验证端口号格式
if ! echo "$WAITFORIT_PORT" | grep -q "^[0-9]\+$"; then
    echoerr "错误: 端口号必须是数字"
    usage
fi

# 验证端口号范围
if [ "$WAITFORIT_PORT" -lt 1 ] || [ "$WAITFORIT_PORT" -gt 65535 ]; then
    echoerr "错误: 端口号必须在1-65535范围内"
    usage
fi

# 验证超时时间
if ! echo "$WAITFORIT_TIMEOUT" | grep -q "^[0-9]\+$"; then
    echoerr "错误: 超时时间必须是数字"
    usage
fi

# 等待服务
wait_for
WAITFORIT_RESULT=$?

# 执行后续命令
if [ "$WAITFORIT_CLI" != "" ]; then
    if [ $WAITFORIT_RESULT -ne 0 ] && [ $WAITFORIT_STRICT -eq 1 ]; then
        echoerr "$WAITFORIT_cmdname: 严格模式下拒绝执行后续命令"
        exit $WAITFORIT_RESULT
    fi
    # 执行后续命令
    exec $WAITFORIT_CLI
else
    exit $WAITFORIT_RESULT
fi

