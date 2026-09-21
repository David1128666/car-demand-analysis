#!/bin/bash
# ============================================
# Flume启动脚本
# 用于启动所有Flume Agent将数据传输到Kafka
# ============================================

# Flume配置目录
CONFIG_DIR="/usr/local/flume"
CONFIG_FILE="/export/data/BD_project/flume-kafka.conf"

# Kafka Broker地址
export KAFKA_BROKERS=localhost:9092

# 检查Flume是否安装
check_flume() {
    if ! command -v flume-ng &> /dev/null; then
        echo "[错误] Flume未安装或未在PATH中"
        echo "请安装Apache Flume并配置环境变量"
        exit 1
    fi
}

# 启动Agent函数
start_agent() {
    local agent_name=$1
    echo "[启动] 正在启动 Flume Agent: ${agent_name}"

    flume-ng agent \
        --name ${agent_name} \
        --conf ${CONFIG_DIR}\conf \
        --conf-file ${CONFIG_FILE} \
        -Dflume.root.logger=INFO,console \
        -Dkafka.bootstrap.servers=${KAFKA_BROKERS} &

    echo "[启动] ${agent_name} 已启动"
}

# 主菜单
show_menu() {
    echo "==========================================="
    echo "  Flume启动器 - 汽车需求数据分析"
    echo "==========================================="
    echo "  1. 启动所有Agent"
    echo "  2. 仅启动用户行为Agent"
    echo "  3. 仅启动搜索数据Agent"
    echo "  4. 仅启动咨询数据Agent"
    echo "  0. 退出"
    echo "==========================================="
    echo -n "请选择操作 [0-4]: "
}

# 主程序
main() {
    check_flume

    case "$1" in
        1)
            echo "启动所有Agent..."
            start_agent agent1  # 用户行为
            start_agent agent2  # 搜索数据
            start_agent agent3  # 咨询数据
            echo "所有Agent已启动"
            ;;
        2)
            start_agent agent1
            ;;
        3)
            start_agent agent2
            ;;
        4)
            start_agent agent3
            ;;
        *)
            show_menu
            read choice
            case ${choice} in
                1) main 1 ;;
                2) main 2 ;;
                3) main 3 ;;
                4) main 4 ;;
                0) exit 0 ;;
                *) echo "[错误] 无效选择" ;;
            esac
            ;;
    esac
}

main "$@"#!/bin/bash
# ============================================
# Flume启动脚本
# 用于启动所有Flume Agent将数据传输到Kafka
# ============================================

# Flume配置目录
CONFIG_DIR="/usr/local/flume"
CONFIG_FILE="/export/data/BD_project/flume-kafka.conf"

# Kafka Broker地址
export KAFKA_BROKERS=localhost:9092

# 检查Flume是否安装
check_flume() {
    if ! command -v flume-ng &> /dev/null; then
        echo "[错误] Flume未安装或未在PATH中"
        echo "请安装Apache Flume并配置环境变量"
        exit 1
    fi
}

# 启动Agent函数
start_agent() {
    local agent_name=$1
    echo "[启动] 正在启动 Flume Agent: ${agent_name}"

    flume-ng agent \
        --name ${agent_name} \
        --conf ${CONFIG_DIR}\conf \
        --conf-file ${CONFIG_FILE} \
        -Dflume.root.logger=INFO,console \
        -Dkafka.bootstrap.servers=${KAFKA_BROKERS} &

    echo "[启动] ${agent_name} 已启动"
}

# 主菜单
show_menu() {
    echo "==========================================="
    echo "  Flume启动器 - 汽车需求数据分析"
    echo "==========================================="
    echo "  1. 启动所有Agent"
    echo "  2. 仅启动用户行为Agent"
    echo "  3. 仅启动搜索数据Agent"
    echo "  4. 仅启动咨询数据Agent"
    echo "  0. 退出"
    echo "==========================================="
    echo -n "请选择操作 [0-4]: "
}

# 主程序
main() {
    check_flume

    case "$1" in
        1)
            echo "启动所有Agent..."
            start_agent agent1  # 用户行为
            start_agent agent2  # 搜索数据
            start_agent agent3  # 咨询数据
            echo "所有Agent已启动"
            ;;
        2)
            start_agent agent1
            ;;
        3)
            start_agent agent2
            ;;
        4)
            start_agent agent3
            ;;
        *)
            show_menu
            read choice
            case ${choice} in
                1) main 1 ;;
                2) main 2 ;;
                3) main 3 ;;
                4) main 4 ;;
                0) exit 0 ;;
                *) echo "[错误] 无效选择" ;;
            esac
            ;;
    esac
}

main "$@"#!/bin/bash
# ============================================
# Flume启动脚本
# 用于启动所有Flume Agent将数据传输到Kafka
# ============================================

# Flume配置目录
CONFIG_DIR="/usr/local/flume"
CONFIG_FILE="/export/data/BD_project/flume-kafka.conf"

# Kafka Broker地址
export KAFKA_BROKERS=localhost:9092

# 检查Flume是否安装
check_flume() {
    if ! command -v flume-ng &> /dev/null; then
        echo "[错误] Flume未安装或未在PATH中"
        echo "请安装Apache Flume并配置环境变量"
        exit 1
    fi
}

# 启动Agent函数
start_agent() {
    local agent_name=$1
    echo "[启动] 正在启动 Flume Agent: ${agent_name}"

    flume-ng agent \
        --name ${agent_name} \
        --conf ${CONFIG_DIR}\conf \
        --conf-file ${CONFIG_FILE} \
        -Dflume.root.logger=INFO,console \
        -Dkafka.bootstrap.servers=${KAFKA_BROKERS} &

    echo "[启动] ${agent_name} 已启动"
}

# 主菜单
show_menu() {
    echo "==========================================="
    echo "  Flume启动器 - 汽车需求数据分析"
    echo "==========================================="
    echo "  1. 启动所有Agent"
    echo "  2. 仅启动用户行为Agent"
    echo "  3. 仅启动搜索数据Agent"
    echo "  4. 仅启动咨询数据Agent"
    echo "  0. 退出"
    echo "==========================================="
    echo -n "请选择操作 [0-4]: "
}

# 主程序
main() {
    check_flume

    case "$1" in
        1)
            echo "启动所有Agent..."
            start_agent agent1  # 用户行为
            start_agent agent2  # 搜索数据
            start_agent agent3  # 咨询数据
            echo "所有Agent已启动"
            ;;
        2)
            start_agent agent1
            ;;
        3)
            start_agent agent2
            ;;
        4)
            start_agent agent3
            ;;
        *)
            show_menu
            read choice
            case ${choice} in
                1) main 1 ;;
                2) main 2 ;;
                3) main 3 ;;
                4) main 4 ;;
                0) exit 0 ;;
                *) echo "[错误] 无效选择" ;;
            esac
            ;;
    esac
}

main "$@"
