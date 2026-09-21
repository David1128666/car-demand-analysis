#!/bin/bash
# ============================================
# 数据发送脚本
# 用于读取模拟数据文件并将数据发送到Flume监听的目录
# ============================================
# 使用方法:
#   ./send_data.sh once    # 单次发送所有类型数据各一条
#   ./send_data.sh loop    # 循环发送(默认2秒间隔)
#   ./send_data.sh reset   # 重置计数器
# ============================================

# 数据目录 - 模拟数据文件位置
DATA_DIR="/export/data/BD_project/data"

# 输出目录 - Flume监控的目录
OUTPUT_DIR="/export/data/mock/data_BD_project/output"

# 创建输出目录
mkdir -p ${OUTPUT_DIR}

# 计数器文件基路径（每种数据类型独立计数器）
COUNTER_BASE="${OUTPUT_DIR}/.counter"

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

PYTHON=$(find_python3)

# 发送间隔(秒)
DELAY=2

# 初始化计数器（每种数据类型独立）
init_counter() {
    local counter_file="${COUNTER_BASE}_$1"
    if [ ! -f ${counter_file} ]; then
        echo "0" > ${counter_file}
    fi
}

# 获取下一条数据的行号（按 output_prefix 独立计数）
get_next_line() {
    local prefix=$1
    local counter_file="${COUNTER_BASE}_${prefix}"
    init_counter "${prefix}"
    LINE_NUM=$(cat ${counter_file})
    NEXT_LINE=$((LINE_NUM + 1))
    echo ${NEXT_LINE} > ${counter_file}
    echo ${LINE_NUM}
}

# 发送数据函数
# 参数1: 数据文件
# 参数2: 输出文件前缀
# 参数3: 主题名称
send_data() {
    local data_file=$1
    local output_prefix=$2
    local topic=$3

    # 获取要读取的行号（按output_prefix独立计数）
    local line_num=$(get_next_line "${output_prefix}")

    # 检查文件是否存在且有数据
    if [ ! -f ${data_file} ]; then
        echo "[错误] 数据文件不存在: ${data_file}"
        return 1
    fi

    local total_lines=$(wc -l < ${data_file})

    # 如果行号超过文件行数，重置为0
    if [ ${line_num} -ge ${total_lines} ]; then
        echo "0" > "${COUNTER_BASE}_${output_prefix}"
        line_num=0
    fi

    # 读取指定行的数据
    local raw_data=$(sed -n "$((line_num + 1))p" ${data_file})

    if [ -z "${raw_data}" ]; then
        echo "[警告] 第 ${line_num} 行数据为空"
        return 1
    fi

    # 更新时间字段为当前时间（优先Python3，降级为sed+date）
    if [ -n "${PYTHON}" ]; then
        local data=$(echo "${raw_data}" | ${PYTHON} -c "
import sys, json
from datetime import datetime
d = json.loads(sys.stdin.read())
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
for key in ['behavior_time', 'search_time', 'consult_time', 'quote_time', 'inquiry_time']:
    if key in d:
        d[key] = now
        break
print(json.dumps(d, ensure_ascii=False))
")
    else
        local now=$(date '+%Y-%m-%d %H:%M:%S')
        # 先用 -E（BSD/macOS），不行用 -r（旧版GNU），再不行用基础正则
        local SED_FLAG=""
        if echo "test" | sed -E 's/test/ok/' >/dev/null 2>&1; then
            SED_FLAG="-E"
        elif echo "test" | sed -r 's/test/ok/' >/dev/null 2>&1; then
            SED_FLAG="-r"
        fi
        if [ -n "${SED_FLAG}" ]; then
            local data=$(echo "${raw_data}" | sed ${SED_FLAG} "s/\"(behavior_time|search_time|consult_time|quote_time|inquiry_time)\":\"[^\"]*\"/\"\\1\":\"${now}\"/g")
        else
            # 基础正则（所有sed都支持）
            local data=$(echo "${raw_data}" | sed "s/\"\(behavior_time\|search_time\|consult_time\|quote_time\|inquiry_time\)\":\"[^\"]*\"/\"\\1\":\"${now}\"/g")
        fi
    fi

    # 追加到同一个文件（Flume持续监控同一文件）
    echo "${data}" >> "${OUTPUT_DIR}/${output_prefix}.txt"

    echo "[$(date '+%H:%M:%S')] 主题: ${topic}, 行号: ${line_num}, 文件: ${OUTPUT_DIR}/${output_prefix}.txt"
}

# 单次发送模式
send_once() {
    send_data "${DATA_DIR}/car-user-behavior.json" "behavior" "car-user-behavior"
    send_data "${DATA_DIR}/car-search.json" "search" "car-search"
    send_data "${DATA_DIR}/car-consult.json" "consult" "car-consult"
    send_data "${DATA_DIR}/car-price-quote.json" "price-quote" "car-price-quote"
    send_data "${DATA_DIR}/car-loan-inquiry.json" "loan-inquiry" "car-loan-inquiry"
}

# 循环发送模式
send_loop() {
    echo "[INFO] 开始循环发送数据，间隔: ${DELAY}秒"
    echo "[INFO] 按 Ctrl+C 停止"

    while true; do
        send_once
        sleep ${DELAY}
    done
}

# 重置计数器（所有数据类型）
reset_counter() {
    for f in "${COUNTER_BASE}"_*; do
        [ -f "$f" ] && echo "0" > "$f"
    done
    echo "[INFO] 所有计数器已重置"
}

# 主程序
main() {
    # 检查数据文件是否存在
    if [ ! -f "${DATA_DIR}/car-user-behavior.json" ]; then
        echo "[错误] 数据文件不存在，请先运行 generate_data.py 生成数据"
        echo "[提示] 或将模拟数据文件复制到: ${DATA_DIR}"
        exit 1
    fi

    case "$1" in
        once)
            send_once
            ;;
        loop)
            send_loop
            ;;
        reset)
            reset_counter
            ;;
        *)
            echo "使用方法:"
            echo "  $0 once   # 单次发送所有类型数据各一条"
            echo "  $0 loop   # 循环发送"
            echo "  $0 reset  # 重置计数器"
            echo ""
            echo "默认: 循环发送"
            echo ""
            send_loop
            ;;
    esac
}

main "$@"
