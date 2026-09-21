# Car Demand Data Simulator

> This document is bilingual. The English version appears first, followed by
> the Simplified Chinese version.

## English

### Overview

This module generates synthetic car demand events and delivers them to Kafka
through Flume. It supports one-command start and stop operations for local
development and demonstrations.

### Directory Structure

```text
simulator/
├── data/                           # Generated JSON data
├── output/                         # Files monitored by Flume
├── generate_data.py                # Data generation script
├── send_data.sh                    # File delivery script
├── flume-kafka.conf                # Flume agent configuration
├── simulatorctl.sh                 # Start, stop, restart, and status commands
└── README.md
```

### Quick Start

1. Generate synthetic data:

```bash
python generate_data.py
```

2. Start the data sender and Flume:

```bash
chmod +x simulatorctl.sh send_data.sh
./simulatorctl.sh start
```

3. Check service status:

```bash
./simulatorctl.sh status
```

4. Stop all services:

```bash
./simulatorctl.sh stop
```

### Manual Operation

```bash
./send_data.sh once
./send_data.sh loop
./send_data.sh reset

flume-ng agent \
  --name car-demand-analytics \
  --conf ./ \
  --conf-file flume-kafka.conf \
  -Dflume.root.logger=INFO,console
```

### Supported Events

| Event | Topic |
|-------|-------|
| User behavior | `car-user-behavior` |
| Search | `car-search` |
| Consultation | `car-consult` |
| Price quotation | `car-price-quote` |
| Loan inquiry | `car-loan-inquiry` |

### Data Pipeline

```text
JSON data files
    |
    v
send_data.sh
    |
    v
output/*.txt
    |
    v
Flume TAILDIR source
    |
    v
Kafka topics
    |
    v
Spark Structured Streaming
```

### Commands

| Command | Description |
|---------|-------------|
| `./simulatorctl.sh start` | Start data delivery and Flume |
| `./simulatorctl.sh stop` | Stop all simulator processes |
| `./simulatorctl.sh restart` | Restart all simulator processes |
| `./simulatorctl.sh status` | Show process status |
| `./simulatorctl.sh help` | Show command help |

### Troubleshooting

- Confirm Flume is installed and `flume-ng` is available.
- Confirm Kafka is running and the broker address in `flume-kafka.conf` is
  correct.
- Check `flume.log` and `data_sender.log`.
- Run `python generate_data.py` before starting the simulator.
- Grant execute permission with `chmod +x simulatorctl.sh send_data.sh`.

## 中文

### 概述

本模块用于生成汽车需求模拟数据，并通过 Flume 将数据发送到 Kafka，支持在
本地开发和演示环境中一键启动或停止服务。

### 目录结构

```text
simulator/
├── data/                           # 生成的 JSON 模拟数据
├── output/                         # Flume 监控目录
├── generate_data.py                # 数据生成脚本
├── send_data.sh                    # 数据发送脚本
├── flume-kafka.conf                # Flume Agent 配置
├── simulatorctl.sh                 # 启动、停止、重启和状态命令
└── README.md
```

### 快速开始

1. 生成模拟数据：

```bash
python generate_data.py
```

2. 启动数据发送和 Flume：

```bash
chmod +x simulatorctl.sh send_data.sh
./simulatorctl.sh start
```

3. 查看服务状态：

```bash
./simulatorctl.sh status
```

4. 停止全部服务：

```bash
./simulatorctl.sh stop
```

### 手动操作

```bash
./send_data.sh once
./send_data.sh loop
./send_data.sh reset

flume-ng agent \
  --name car-demand-analytics \
  --conf ./ \
  --conf-file flume-kafka.conf \
  -Dflume.root.logger=INFO,console
```

### 支持的数据类型

| 数据类型 | Kafka Topic |
|----------|-------------|
| 用户行为 | `car-user-behavior` |
| 搜索 | `car-search` |
| 咨询 | `car-consult` |
| 报价 | `car-price-quote` |
| 贷款询价 | `car-loan-inquiry` |

### 数据流程

```text
JSON 数据文件
    |
    v
send_data.sh
    |
    v
output/*.txt
    |
    v
Flume TAILDIR Source
    |
    v
Kafka Topics
    |
    v
Spark Structured Streaming
```

### 命令

| 命令 | 说明 |
|------|------|
| `./simulatorctl.sh start` | 启动数据发送和 Flume |
| `./simulatorctl.sh stop` | 停止所有模拟器进程 |
| `./simulatorctl.sh restart` | 重启所有模拟器进程 |
| `./simulatorctl.sh status` | 查看进程状态 |
| `./simulatorctl.sh help` | 查看命令帮助 |

### 常见问题

- 确认已安装 Flume，且 `flume-ng` 命令可用。
- 确认 Kafka 已启动，并检查 `flume-kafka.conf` 中的 Broker 地址。
- 查看 `flume.log` 和 `data_sender.log`。
- 启动模拟器前先运行 `python generate_data.py`。
- 使用 `chmod +x simulatorctl.sh send_data.sh` 添加执行权限。
