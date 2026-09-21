#!/bin/bash
# ============================================
# 一键启停脚本 - 汽车需求数据分析
# ============================================
# 功能：
#   1. 生成最新模拟数据
#   2. 启动模拟数据发送
#   3. 启动Flume将数据发送到Kafka
#   4. 一键停止所有服务
#
# 使用方法：
#   ./simulatorctl.sh start     # 启动所有服务
#   ./simulatorctl.sh stop      # 停止所有服务
#   ./simulatorctl.sh restart   # 重启所有服务
#   ./simulatorctl.sh status    # 查看服务状态
# ============================================

# 应用根目录
APP_HOME="/export/data/BD_project"
FLUME_HOME="/usr/local/flume"
# 日志和输出目录
LOG_DIR="/export/data/mock/data_BD_project/logs"
OUTPUT_DIR="/export/data/mock/data_BD_project/output"

# 配置文件
FLUME_CONFIG="./job/flume-kafka.conf"
FLUME_AGENT_NAME="car-demand-analytics"
FLUME_LOG="/export/data/mock/data_BD_project/logs/flume.log"
DATA_SENDER_LOG="/export/data/mock/data_BD_project/logs/data_sender.log"
DATA_SCRIPT="${APP_HOME}/send_data.sh"
GENERATE_SCRIPT="$(dirname "$0")/generate_data.py"
GENERATE_DATA_DIR="$(dirname "$0")/data"

# PID文件
FLUME_PID_FILE="${APP_HOME}/flume.pid"
DATA_PID_FILE="${APP_HOME}/data_sender.pid"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查Flume是否安装
check_flume() {
    if ! command -v flume-ng &> /dev/null; then
        log_error "Flume未安装或未在PATH中"
        echo "请安装Apache Flume并配置环境变量"
        exit 1
    fi
    log_info "Flume已安装: $(which flume-ng)"
}

# 重新生成模拟数据（时间戳为当天最新）
# 检测 Python 3（依次尝试常见命名）
find_python3() {
    for candidate in python3 python3.8 python3.6 python3.7 python3.9 python3.10 python3.11 python3.12 python; do
        local p=$(command -v "${candidate}" 2>/dev/null)
        if [ -n "${p}" ]; then
            local ver=$("${p}" --version 2>&1)
            case "${ver}" in
                *"Python 3"*) echo "${p}"; return 0 ;;
            esac
        fi
    done
    return 1
}

regenerate_data() {
    log_step "重新生成模拟数据..."

    if [ ! -f "${GENERATE_SCRIPT}" ]; then
        log_warn "generate_data.py 未找到: ${GENERATE_SCRIPT}"
        log_warn "跳过数据生成，使用已有数据"
        return 0
    fi

    local PYTHON=$(find_python3)
    if [ -z "${PYTHON}" ]; then
        log_warn "未找到 Python 3，跳过数据生成"
        return 0
    fi
    ${PYTHON} "${GENERATE_SCRIPT}"
    if [ $? -ne 0 ]; then
        log_error "数据生成失败"
        return 1
    fi

    # 将生成的数据复制到Flume读取目录
    if [ -d "${GENERATE_DATA_DIR}" ]; then
        mkdir -p /export/data/BD_project/data
        cp "${GENERATE_DATA_DIR}"/*.json /export/data/BD_project/data/ 2>/dev/null
        log_info "数据已复制到 /export/data/BD_project/data/"
    fi

    log_info "模拟数据生成完成"
}

# 检查数据文件是否存在
check_data() {
    if [ ! -f "/export/data/BD_project/data/car-user-behavior.json" ]; then
        log_error "模拟数据文件不存在，请先运行 generate_data.py"
        log_error "或复制数据文件到: /export/data/BD_project/data/"
        exit 1
    fi
    log_info "模拟数据文件检查通过"
}

# 创建输出目录和初始文件
prepare_output_dir() {
    mkdir -p /export/data/mock/data_BD_project/logs
    mkdir -p /export/data/mock/data_BD_project/output

    # 创建初始空文件（TAILDIR需要文件存在）
    touch /export/data/mock/data_BD_project/output/behavior.txt
    touch /export/data/mock/data_BD_project/output/search.txt
    touch /export/data/mock/data_BD_project/output/consult.txt
    touch /export/data/mock/data_BD_project/output/price-quote.txt
    touch /export/data/mock/data_BD_project/output/loan-inquiry.txt

    log_info "输出目录已准备: /export/data/mock/data_BD_project/output"
    log_info "日志目录已准备: /export/data/mock/data_BD_project/logs"
}

# 启动模拟数据发送
start_data_sender() {
    log_step "启动模拟数据发送服务..."

    # 切换到工作目录后启动数据发送（循环模式，2秒间隔）
    cd ${APP_HOME}
    mkdir -p /export/data/mock/data_BD_project/logs
    nohup ${DATA_SCRIPT} loop > ${DATA_SENDER_LOG} 2>&1 &
    DATA_PID=$!
    echo ${DATA_PID} > ${DATA_PID_FILE}

    sleep 1
    if kill -0 ${DATA_PID} 2>/dev/null; then
        log_info "模拟数据发送服务已启动 (PID: ${DATA_PID})"
        log_info "日志文件: ${DATA_SENDER_LOG}"
    else
        log_error "模拟数据发送服务启动失败"
        return 1
    fi
}

# 停止模拟数据发送
stop_data_sender() {
    log_step "停止模拟数据发送服务..."

    if [ -f ${DATA_PID_FILE} ]; then
        DATA_PID=$(cat ${DATA_PID_FILE})
        if kill -0 ${DATA_PID} 2>/dev/null; then
            kill ${DATA_PID} 2>/dev/null
            sleep 1
            if kill -0 ${DATA_PID} 2>/dev/null; then
                kill -9 ${DATA_PID} 2>/dev/null
            fi
            log_info "模拟数据发送服务已停止 (PID: ${DATA_PID})"
        else
            log_warn "模拟数据发送服务未运行"
        fi
        rm -f ${DATA_PID_FILE}
    else
        pkill -f "send_data.sh" 2>/dev/null
        log_info "已尝试停止所有数据发送进程"
    fi
}

# 启动Flume
start_flume() {
    log_step "启动Flume服务..."

    # 创建日志和输出目录
    mkdir -p /export/data/mock/data_BD_project/logs
    mkdir -p /export/data/mock/data_BD_project/output

    # 切换到工作目录后启动Flume
    cd ${FLUME_HOME}
    nohup ./bin/flume-ng agent \
        --name ${FLUME_AGENT_NAME} \
        --conf ./conf \
        --conf-file ${FLUME_CONFIG} \
        -Dflume.root.logger=INFO,console \
        -Dkafka.bootstrap.servers=node1:9092 \
        > ${FLUME_LOG} 2>&1 &

    FLUME_PID=$!
    echo ${FLUME_PID} > ${FLUME_PID_FILE}

    sleep 3
    if kill -0 ${FLUME_PID} 2>/dev/null; then
        log_info "Flume服务已启动 (PID: ${FLUME_PID})"
        log_info "Agent名称: ${FLUME_AGENT_NAME}"
        log_info "日志文件: ${FLUME_LOG}"
    else
        log_error "Flume服务启动失败，请检查日志: ${FLUME_LOG}"
        return 1
    fi
}

# 停止Flume
stop_flume() {
    log_step "停止Flume服务..."

    if [ -f ${FLUME_PID_FILE} ]; then
        FLUME_PID=$(cat ${FLUME_PID_FILE})
        if kill -0 ${FLUME_PID} 2>/dev/null; then
            kill ${FLUME_PID} 2>/dev/null
            sleep 2
            if kill -0 ${FLUME_PID} 2>/dev/null; then
                kill -9 ${FLUME_PID} 2>/dev/null
            fi
            log_info "Flume服务已停止 (PID: ${FLUME_PID})"
        else
            log_warn "Flume服务未运行"
        fi
        rm -f ${FLUME_PID_FILE}
    else
        pkill -f "flume-ng" 2>/dev/null
        log_info "已尝试停止所有Flume进程"
    fi
}

# 查看服务状态
show_status() {
    echo ""
    echo "=========================================="
    echo "  服务状态"
    echo "=========================================="
    echo "工作目录: ${APP_HOME}"
    echo ""

    echo "Flume服务:"
    if [ -f ${FLUME_PID_FILE} ]; then
        FLUME_PID=$(cat ${FLUME_PID_FILE})
        if kill -0 ${FLUME_PID} 2>/dev/null; then
            echo -e "  ${GREEN}● 运行中${NC} (PID: ${FLUME_PID})"
        else
            echo -e "  ${RED}○ 未运行${NC} (PID文件存在但进程已停止)"
        fi
    else
        echo -e "  ${RED}○ 未运行${NC}"
    fi

    echo ""
    echo "模拟数据发送:"
    if [ -f ${DATA_PID_FILE} ]; then
        DATA_PID=$(cat ${DATA_PID_FILE})
        if kill -0 ${DATA_PID} 2>/dev/null; then
            echo -e "  ${GREEN}● 运行中${NC} (PID: ${DATA_PID})"
        else
            echo -e "  ${RED}○ 未运行${NC} (PID文件存在但进程已停止)"
        fi
    else
        echo -e "  ${RED}○ 未运行${NC}"
    fi

    echo ""
    echo "日志文件:"
    [ -f ${FLUME_LOG} ] && echo "  Flume: ${FLUME_LOG}" || echo "  Flume: 不存在"
    [ -f ${DATA_SENDER_LOG} ] && echo "  数据发送: ${DATA_SENDER_LOG}" || echo "  数据发送: 不存在"

    echo ""
}

# 启动所有服务
do_start() {
    echo ""
    echo "=========================================="
    echo "  启动所有服务"
    echo "=========================================="
    echo ""

    regenerate_data
    check_data
    prepare_output_dir

    start_data_sender
    start_flume

    echo ""
    echo "=========================================="
    echo -e "${GREEN}  所有服务已启动！${NC}"
    echo "=========================================="
    show_status
}

# 停止所有服务
do_stop() {
    echo ""
    echo "=========================================="
    echo "  停止所有服务"
    echo "=========================================="
    echo ""

    stop_flume
    stop_data_sender

    echo ""
    echo "=========================================="
    echo -e "${GREEN}  所有服务已停止！${NC}"
    echo "=========================================="
}

# 重启所有服务
do_restart() {
    do_stop
    sleep 2
    do_start
}

# 显示帮助
show_help() {
    echo ""
    echo "=========================================="
    echo "  汽车需求数据分析 - 一键启停脚本"
    echo "=========================================="
    echo ""
    echo "工作目录: ${APP_HOME}"
    echo ""
    echo "使用方法:"
    echo "  $0 start     # 启动所有服务"
    echo "  $0 stop      # 停止所有服务"
    echo "  $0 restart   # 重启所有服务"
    echo "  $0 status    # 查看服务状态"
    echo "  $0 help      # 显示帮助"
    echo ""
    echo "服务说明:"
    echo "  - 数据生成: 运行 generate_data.py 生成最新模拟数据"
    echo "  - 数据发送: 循环发送模拟数据到output目录（自动更新时间戳）"
    echo "  - Flume: 监控output目录并发送到Kafka"
    echo ""
    echo "日志文件:"
    echo "  - Flume日志: ${FLUME_LOG}"
    echo "  - 数据发送日志: ${APP_HOME}/data_sender.log"
    echo ""
}

# 主程序
main() {
    case "$1" in
        start)
            do_start
            ;;
        stop)
            do_stop
            ;;
        restart)
            do_restart
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            show_help
            ;;
    esac
}

main "$@"
