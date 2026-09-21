# Project Features and Usage

> This document is bilingual. The English version appears first, followed by
> the Simplified Chinese version.

## English

### 1. Project Overview

The platform analyzes multi-source car demand data and produces operational
analytics, market insights, user profiles, and personalized recommendations.
The main data sources are user behavior, search, consultation, price quotation,
and loan inquiry events.

The system uses a Lambda-style architecture:

- **Speed layer**: Spark Structured Streaming consumes Kafka and writes realtime
  metrics to MySQL.
- **Batch layer**: Spark SQL processes historical data for trends, profiles, and
  daily statistics.
- **Serving layer**: MySQL stores analysis results, FastAPI exposes REST APIs,
  and Vue 3 presents the results.
- **Recommendation layer**: ALS collaborative filtering, content recall, and
  popularity recall are combined by a weighted ranking strategy.

### 2. Repository Modules

| Module | Purpose |
|--------|---------|
| `backend/` | FastAPI REST service, authentication, dashboard, market, car, admin, and recommendation APIs |
| `frontend/` | Vue 3 dashboard, analytics, market, car, recommendation, login, and administration pages |
| `simulator/` | Generates synthetic data and delivers it to Kafka through Flume |
| `car-demand-analysis/common/` | Shared Scala models, configuration, JSON utilities, and MySQL utilities |
| `car-demand-analysis/realtime-analysis/` | Kafka to Spark Structured Streaming to MySQL |
| `car-demand-analysis/offline-analysis/` | Spark SQL trend, profile, preference, and daily-stat jobs |
| `car-demand-analysis/recommendation-engine/` | ALS, content-based, popularity, and ranking logic |
| `car-demand-analysis/scripts/` | Maven build and Spark submission scripts |

### 3. Frontend Pages

| Route | Page | Description |
|-------|------|-------------|
| `/login` | Login | JWT authentication and registration |
| `/` | Dashboard | Traffic, behavior, vehicle, quotation, and loan metrics |
| `/analysis` | Analytics | Car type preference, consultation conversion, loan approval, trends, and recommendation performance |
| `/market` | Market insights | Brand share, keywords, fuel trends, price changes, promotions, and discount tiers |
| `/cars` | Car search | Brand, type, fuel, and price filtering with pagination |
| `/cars/:id` | Car detail | Car metadata and basic attributes |
| `/recommendations` | Recommendations | Personalized and popular recommendations |
| `/admin` | Administration | Users, monitoring, configuration, logs, and car management |

The frontend supports English and Simplified Chinese. English is the default
language, and the selected language is stored in browser local storage.

### 4. Realtime Pipeline

Kafka topics:

| Topic | Producer |
|-------|----------|
| `car-user-behavior` | Simulator |
| `car-search` | Simulator |
| `car-consult` | Simulator |
| `car-price-quote` | Simulator |
| `car-loan-inquiry` | Simulator |

The realtime processors parse and validate events, aggregate statistics, and
write results to MySQL through `foreachBatch`.

### 5. Offline Analytics

| Task | Function |
|------|----------|
| `trend` | Brand and daily trend analysis |
| `profile` | User preference and value profiles |
| `preference` | Car type, fuel, and regional preference analysis |
| `daily` | Daily summary statistics |
| `all` | Run all offline tasks in sequence |

### 6. Recommendation Engine

The recommendation pipeline uses:

1. **Collaborative filtering**: ALS matrix factorization over user-car
   interactions.
2. **Content-based recall**: similarity across brand, car type, fuel type, and
   normalized price.
3. **Popularity recall**: global page-view ranking for cold-start users and
   fallback coverage.
4. **Weighted ranking**: collaborative filtering 0.5, content-based 0.3, and
   popularity 0.2.

### 7. Local Setup

The fastest demo startup is:

```bash
docker compose up --build
```

This starts MySQL, Kafka, the FastAPI backend, and the Vue frontend. Open
`http://localhost:5173` and use `admin / admin123`. Database schema and demo data
are initialized automatically.

Requirements:

- JDK 11 and Maven 3.8+
- Python 3.11+
- Node.js 18+ (20 LTS recommended)
- MySQL 8.0+
- Kafka 3.x
- Flume 1.11 for simulator delivery
- Spark 3.3.1 for distributed jobs

Start services in this order:

1. Start MySQL and Kafka.
2. Create the `car_demand_analysis` database and tables.
3. Run the simulator.
4. Build and run the Scala jobs.
5. Start the FastAPI backend.
6. Start the Vue frontend.

Example commands:

```bash
cd simulator
python generate_data.py
./simulatorctl.sh start

cd ../car-demand-analysis
mvn clean package -DskipTests
./scripts/run-realtime.sh
./scripts/run-offline.sh all
./scripts/run-recommendation.sh

cd ../backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

cd ../frontend
npm install
npm run dev
```

### 8. Configuration

The backend reads database and authentication settings from environment
variables. Copy `.env.example` to `.env` and replace all placeholder values.

Spark module configuration is stored in each module's
`src/main/resources/application.conf`.

Never commit real credentials, private data, database dumps, or access tokens.

### 9. Troubleshooting

- **Maven dependency failures**: check the network and Maven mirror settings.
- **Kafka consumer errors**: verify Kafka, the topic list, and the bootstrap
  address.
- **MySQL write failures**: verify the JDBC URL, credentials, database name, and
  table schema.
- **Frontend 401 responses**: sign in again and confirm that the stored token is
  valid.
- **Empty recommendations**: run the simulator, realtime analysis, offline
  analysis, and recommendation engine in sequence.
- **Spark out-of-memory errors**: increase executor memory or reduce the input
  volume.

### 10. Default Ports

| Service | Port |
|---------|------|
| Vite frontend | 5173 |
| FastAPI backend | 8000 |
| MySQL | 3306 |
| Kafka | 9092 |
| Spark UI | 4040 |

## 中文

### 1. 项目概述

本平台用于分析多源汽车需求数据，输出实时指标、市场洞察、用户画像和个性化
推荐。主要数据来源包括用户行为、搜索、咨询、报价和贷款询价事件。

系统采用 Lambda 风格架构：

- **速度层**：Spark Structured Streaming 消费 Kafka，并将实时指标写入
  MySQL。
- **批处理层**：Spark SQL 处理历史数据，生成趋势、画像和日报。
- **服务层**：MySQL 存储分析结果，FastAPI 提供 REST 接口，Vue 3 展示页面。
- **推荐层**：ALS 协同过滤、内容召回和热门召回通过加权排序融合。

### 2. 仓库模块

| 模块 | 用途 |
|------|------|
| `backend/` | FastAPI 服务，提供认证、看板、市场、车型、后台和推荐接口 |
| `frontend/` | Vue 3 登录、看板、分析、市场、车型、推荐和后台页面 |
| `simulator/` | 生成模拟数据，并通过 Flume 发送到 Kafka |
| `car-demand-analysis/common/` | Scala 公共模型、配置、JSON 和 MySQL 工具 |
| `car-demand-analysis/realtime-analysis/` | Kafka 到 Spark Streaming 到 MySQL |
| `car-demand-analysis/offline-analysis/` | Spark SQL 趋势、画像、偏好和日报任务 |
| `car-demand-analysis/recommendation-engine/` | ALS、内容召回、热门召回和排序 |
| `car-demand-analysis/scripts/` | Maven 构建和 Spark 提交脚本 |

### 3. 前端页面

| 路由 | 页面 | 说明 |
|------|------|------|
| `/login` | 登录 | JWT 认证和账号注册 |
| `/` | 数据大屏 | 流量、行为、车型、报价和贷款指标 |
| `/analysis` | 数据分析 | 车型偏好、咨询转化、贷款审批、趋势和推荐效果 |
| `/market` | 市场洞察 | 品牌份额、关键词、燃料趋势、价格变化、活动和折扣 |
| `/cars` | 车型查询 | 品牌、类型、燃料和价格筛选及分页 |
| `/cars/:id` | 车型详情 | 车型元数据和基础属性 |
| `/recommendations` | 智能推荐 | 个性化和热门推荐 |
| `/admin` | 后台管理 | 用户、监控、配置、日志和车辆管理 |

前端支持英文和简体中文。默认语言为英文，用户选择的语言保存在浏览器本地
存储中。

### 4. 实时数据链路

Kafka Topic：

| Topic | 生产者 |
|-------|--------|
| `car-user-behavior` | 数据模拟器 |
| `car-search` | 数据模拟器 |
| `car-consult` | 数据模拟器 |
| `car-price-quote` | 数据模拟器 |
| `car-loan-inquiry` | 数据模拟器 |

实时处理器负责解析和校验事件、聚合统计指标，并通过 `foreachBatch` 写入
MySQL。

### 5. 离线分析

| 任务 | 功能 |
|------|------|
| `trend` | 品牌和每日趋势分析 |
| `profile` | 用户偏好和价值画像 |
| `preference` | 车型、燃料和地区偏好分析 |
| `daily` | 每日汇总统计 |
| `all` | 依次执行全部离线任务 |

### 6. 推荐引擎

推荐流程包括：

1. **协同过滤**：基于用户与车型交互矩阵执行 ALS 矩阵分解。
2. **内容召回**：计算品牌、车型、燃料和归一化价格之间的相似度。
3. **热门召回**：按全局浏览量排序，用于新用户冷启动和结果补全。
4. **加权排序**：协同过滤 0.5、内容推荐 0.3、热门推荐 0.2。

### 7. 本地运行

最快的演示启动方式是：

```bash
docker compose up --build
```

该命令会启动 MySQL、Kafka、FastAPI 后端和 Vue 前端。访问
`http://localhost:5173`，使用 `admin / admin123` 登录。数据库结构和演示数据
会自动初始化。

环境要求：

- JDK 11 和 Maven 3.8+
- Python 3.11+
- Node.js 18+，推荐 20 LTS
- MySQL 8.0+
- Kafka 3.x
- Flume 1.11，用于模拟器发送数据
- Spark 3.3.1，用于执行 Spark 任务

建议启动顺序：

1. 启动 MySQL 和 Kafka。
2. 创建 `car_demand_analysis` 数据库和业务表。
3. 启动数据模拟器。
4. 构建并运行 Scala 任务。
5. 启动 FastAPI 后端。
6. 启动 Vue 前端。

示例命令：

```bash
cd simulator
python generate_data.py
./simulatorctl.sh start

cd ../car-demand-analysis
mvn clean package -DskipTests
./scripts/run-realtime.sh
./scripts/run-offline.sh all
./scripts/run-recommendation.sh

cd ../backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

cd ../frontend
npm install
npm run dev
```

### 8. 配置

后端通过环境变量读取数据库和认证配置。复制 `.env.example` 为 `.env`，并替换
全部占位值。

Spark 模块配置位于各模块的 `src/main/resources/application.conf`。

不要提交真实凭据、私有数据、数据库备份或访问令牌。

### 9. 常见问题

- **Maven 依赖失败**：检查网络和 Maven 镜像设置。
- **Kafka 消费异常**：检查 Kafka、Topic 列表和 Broker 地址。
- **MySQL 写入失败**：检查 JDBC 地址、账号、数据库名和表结构。
- **前端返回 401**：重新登录并确认本地 Token 有效。
- **推荐结果为空**：依次运行模拟器、实时分析、离线分析和推荐引擎。
- **Spark 内存不足**：增加 Executor 内存或减少处理数据量。

### 10. 默认端口

| 服务 | 端口 |
|------|------|
| Vite 前端 | 5173 |
| FastAPI 后端 | 8000 |
| MySQL | 3306 |
| Kafka | 9092 |
| Spark UI | 4040 |
