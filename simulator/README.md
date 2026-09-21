# 汽车需求数据分析 - 模拟数据生成器

## 📋 概述

本模块用于生成汽车需求数据分析项目的模拟测试数据，支持一键启动/停止所有服务。

## 📁 目录结构

```
simulator/
├── data/                           # 模拟数据文件目录
│   ├── car-user-behavior.json      # 用户行为数据 (1万条)
│   ├── car-search.json            # 搜索数据 (1万条)
│   └── car-consult.json           # 咨询数据 (1万条)
├── output/                         # 输出目录 (Flume监控)
│   ├── behavior.txt                # 用户行为输出文件
│   ├── search.txt                  # 搜索输出文件
│   └── consult.txt                 # 咨询输出文件
├── generate_data.py                # 数据生成脚本
├── send_data.sh                    # 数据发送脚本
├── flume-kafka.conf                # Flume配置文件 (单Agent)
├── simulatorctl.sh                 # 一键启停脚本
└── README.md                       # 使用说明
```

## 🚀 一键启动（推荐）

### 1. 生成模拟数据

```bash
python generate_data.py
```

### 2. 一键启动所有服务

```bash
chmod +x simulatorctl.sh
./simulatorctl.sh start
```

### 3. 查看服务状态

```bash
./simulatorctl.sh status
```

### 4. 停止所有服务

```bash
./simulatorctl.sh stop
```

## 🔧 高级操作

### 手动操作

```bash
# 1. 发送数据到输出目录
./send_data.sh once    # 单次发送
./send_data.sh loop    # 循环发送
./send_data.sh reset   # 重置计数器

# 2. 启动Flume
flume-ng agent \
    --name car-demand-analytics \
    --conf ./ \
    --conf-file flume-kafka.conf \
    -Dflume.root.logger=INFO,console
```

## 📊 数据格式说明

### 用户行为数据 (car-user-behavior)

```json
{
  "behavior_id": "beh_1712345678900000",
  "user_id": "user_0001",
  "car_id": 1,
  "behavior_type": "browse",
  "behavior_time": "2024-05-14 10:30:00",
  "brand_id": 1,
  "brand_name": "品牌1",
  "series_id": 10,
  "car_type": "SUV",
  "fuel_type": "纯电动",
  "price": 18.5,
  "region_id": 1,
  "session_id": "sess_123456",
  "search_keyword": "比亚迪汉"
}
```

### 搜索数据 (car-search)

```json
{
  "search_id": "sch_1712345678900001",
  "user_id": "user_0001",
  "search_keyword": "比亚迪汉",
  "search_time": "2024-05-14 10:30:00",
  "region_id": 1,
  "result_count": 50,
  "click_position": 2
}
```

### 咨询数据 (car-consult)

```json
{
  "consult_id": "con_1712345678900002",
  "user_id": "user_0001",
  "car_id": 1,
  "consult_time": "2024-05-14 10:30:00",
  "consult_type": "价格咨询",
  "region_id": 1,
  "has_phone": true,
  "followup_status": "待联系"
}
```

## 🔄 数据发送流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   模拟数据文件   │ --> │   send_data.sh  │ --> │   output目录     │ --> │     Flume       │
│ (car-*.json)    │     │   (读取一条)    │     │ (behavior.txt)  │     │ (监控目录)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                                                │
                                                                                v
                                                                        ┌───────────────┐
                                                                        │    Kafka      │
                                                                        │  (3个Topic)   │
                                                                        └───────┬───────┘
                                                                                |
                                                                                v
                                                                        ┌───────────────┐
                                                                        │ Spark         │
                                                                        │ Streaming     │
                                                                        └───────────────┘
```

## 📝 一键启停脚本使用说明

### 命令

| 命令 | 说明 |
|------|------|
| `./simulatorctl.sh start` | 启动所有服务（模拟数据+Flume） |
| `./simulatorctl.sh stop` | 停止所有服务 |
| `./simulatorctl.sh restart` | 重启所有服务 |
| `./simulatorctl.sh status` | 查看服务状态 |
| `./simulatorctl.sh help` | 显示帮助 |

### 工作原理

1. **启动数据发送**: 后台运行 `send_data.sh loop`，每2秒发送一条数据
2. **启动Flume**: 单个Agent监控 `./output` 目录，根据文件名分发到不同Kafka Topic
3. **PID管理**: 使用PID文件记录进程ID，方便停止和监控

### 日志文件

| 文件 | 说明 |
|------|------|
| `flume.log` | Flume运行日志 |
| `data_sender.log` | 数据发送日志 |

## 🛠️ 故障排除

### 1. Flume无法启动

```bash
# 检查Flume安装
which flume-ng

# 检查配置语法
flume-ng version
```

### 2. Kafka连接失败

确保Kafka已启动并配置正确的地址：
```properties
KAFKA_BROKERS=node1:9092
```

### 3. 数据未发送到Kafka

```bash
# 查看Flume日志
tail -f flume.log

# 查看数据发送日志
tail -f data_sender.log

# 检查Kafka Topic
kafka-topics.sh --list --bootstrap-server node1:9092
```

## 📞 注意事项

1. **首次使用**: 先运行 `python generate_data.py` 生成模拟数据
2. **赋执行权限**: `chmod +x simulatorctl.sh send_data.sh`
3. **停止服务**: 必须使用 `./simulatorctl.sh stop`，避免进程残留
4. **重启服务**: 使用 `./simulatorctl.sh restart` 确保干净重启