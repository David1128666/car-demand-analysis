# 基于多源数据行为的汽车需求挖掘与推荐平台

一个面向汽车用户行为与市场数据的分析与推荐项目，包含 Vue 3 前端、
FastAPI 后端、模拟数据生成器、Spark 实时/离线分析任务，以及基于多路召回的
推荐引擎。

## 功能模块

- **数据大屏与后台管理**：展示用户行为、搜索、咨询、报价和贷款等业务指标。
- **实时分析**：通过 Spark Structured Streaming 消费 Kafka 数据并写入 MySQL。
- **离线分析**：通过 Spark SQL 完成趋势、用户画像、车型偏好和日统计等任务。
- **推荐引擎**：结合 ALS 协同过滤、内容召回和热门召回生成推荐结果。
- **数据模拟器**：生成用户行为、搜索、咨询、报价和贷款等模拟数据。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3、Vite、Pinia、Vue Router、Axios、ECharts |
| 后端 | Python 3.11、FastAPI、PyMySQL |
| 实时计算 | Apache Spark Structured Streaming、Apache Kafka、Flume |
| 离线计算 | Apache Spark SQL |
| 推荐 | Apache Spark MLlib、ALS、多路召回与排序 |
| 存储 | MySQL 8.0 |
| 构建 | Maven 3.8+、Scala 2.13.14、JDK 11 |

## 项目结构

```text
基于多源数据行为的汽车需求挖掘与推荐平台/
├── backend/                         # FastAPI 后端服务
├── frontend/                        # Vue 3 前端
├── simulator/                       # Flume/Kafka 模拟数据生成与发送
├── car-demand-analysis/             # Scala Maven 多模块工程
│   ├── common/                      # 公共模型、配置与工具
│   ├── realtime-analysis/           # Kafka -> Spark -> MySQL
│   ├── offline-analysis/            # Spark SQL 离线分析
│   ├── recommendation-engine/       # 推荐召回与排序
│   └── scripts/                     # 构建与运行脚本
├── .env.example
├── .gitattributes
├── .gitignore
├── LICENSE
└── README.md
```

## 数据流

```text
数据模拟器 / Flume
        │
        ▼
Kafka Topics
  ├── car-user-behavior
  ├── car-search
  ├── car-consult
  ├── car-price-quote
  └── car-loan-inquiry
        │
        ▼
Spark Structured Streaming
        │
        ▼
      MySQL
        │
  ┌─────┼──────────┐
  ▼     ▼          ▼
实时统计 离线分析 推荐引擎
  │     │          │
  └─────┼──────────┘
        ▼
   FastAPI 接口
        │
        ▼
   Vue 3 前端
```

## 环境要求

- JDK 11
- Maven 3.8+
- Python 3.11+
- Node.js 18+（推荐 20 LTS）
- MySQL 8.0+
- Apache Kafka 3.x
- Apache Flume 1.11（模拟器发送数据时需要）
- Apache Spark 3.3.1（运行 Spark 任务时需要）

## 配置

复制根目录 `.env.example` 为 `.env`，并修改本地数据库账号：

```text
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=change-me
MYSQL_DATABASE=car_demand_analysis
SECRET_KEY=replace-with-a-random-secret
PASSWORD_SALT=replace-with-a-random-salt
```

各 Spark 模块的 Kafka、MySQL 和检查点配置位于：

```text
car-demand-analysis/realtime-analysis/src/main/resources/application.conf
car-demand-analysis/offline-analysis/src/main/resources/application.conf
car-demand-analysis/recommendation-engine/src/main/resources/application.conf
```

仓库中的 `root/root` 仅为本地开发默认值。运行前请修改为自己的数据库账号，
且不要将真实密码、Token、数据库备份或生产数据提交到 Git。

## 快速开始

### 1. 初始化数据库

创建数据库：

```sql
CREATE DATABASE car_demand_analysis
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

按业务需要准备实时统计、离线分析、用户画像和推荐结果等业务表。

### 2. 启动后端

在项目根目录执行：

```powershell
Copy-Item .env.example .env
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --env-file ..\.env --host 0.0.0.0 --port 8000
```

后端接口文档默认位于 `http://localhost:8000/docs`。

### 3. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

前端开发服务默认由 Vite 提供，运行时请确保后端地址配置正确。

### 4. 构建 Scala 模块

```powershell
mvn -f car-demand-analysis/pom.xml clean package -DskipTests
```

也可以使用脚本：

```bash
./car-demand-analysis/scripts/build-all.sh
./car-demand-analysis/scripts/run-realtime.sh
./car-demand-analysis/scripts/run-offline.sh all
./car-demand-analysis/scripts/run-recommendation.sh
```

### 5. 启动模拟数据

```bash
cd simulator
python generate_data.py
chmod +x simulatorctl.sh send_data.sh
./simulatorctl.sh start
```

模拟数据目录属于运行产物，不会提交到 Git；需要时可通过
`simulator/generate_data.py` 重新生成。

## Kafka Topics

| Topic | 说明 |
|-------|------|
| `car-user-behavior` | 用户浏览、收藏、对比等行为 |
| `car-search` | 用户搜索行为 |
| `car-consult` | 车型咨询行为 |
| `car-price-quote` | 车型报价与优惠数据 |
| `car-loan-inquiry` | 贷款咨询数据 |

## 主要输出表

| 表名 | 来源 | 说明 |
|------|------|------|
| `realtime_stats` | 实时分析 | 用户行为实时统计 |
| `realtime_price_stats` | 实时分析 | 报价与折扣统计 |
| `realtime_loan_stats` | 实时分析 | 贷款申请统计 |
| `search_log` | 实时分析 | 热门搜索记录 |
| `operation_log` | 实时分析 | 咨询跟进与操作记录 |
| `daily_stats` | 离线分析 | 日报和趋势统计 |
| `user_profile` | 离线分析 | 用户画像 |
| `recommendation` | 推荐引擎 | 推荐结果 |

## 相关文档

- `simulator/README.md`
- `car-demand-analysis/scripts/项目功能说明与使用文档.md`

## License

本项目使用 [MIT License](LICENSE)。
