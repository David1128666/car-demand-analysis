# Multi-source Car Demand Mining and Recommendation Platform

A full-stack platform for analyzing car demand from user behavior, search,
consultation, quotation, and loan-inquiry data. The system combines a Vue 3
frontend, a FastAPI backend, Spark batch and streaming jobs, and a multi-recall
recommendation engine.

The frontend supports English and Simplified Chinese and stores the selected
language in the browser.

## Features

- **Dashboard**: page views, unique visitors, searches, consultations,
  favorites, car inventory, quotation, and loan metrics.
- **Analytics**: car type preference, brand consultation conversion, loan
  approval, daily trends, and recommendation performance.
- **Market insights**: brand preference, market share, search keywords, fuel
  trends, price changes, price wars, promotions, and discount tiers.
- **Car search**: filtering and pagination for brands, car types, fuel types,
  prices, and detailed car records.
- **Recommendations**: ALS collaborative filtering, content-based recall,
  popularity recall, weighted ranking, and user-level recommendation views.
- **Administration**: user management, database monitoring, data freshness,
  system configuration, operation logs, and car management.
- **Data simulator**: synthetic event generation and delivery to Kafka through
  Flume.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3, Vite, Pinia, Vue Router, Axios, ECharts, Lucide |
| Internationalization | Custom English and Simplified Chinese dictionaries |
| Backend | Python 3.11, FastAPI, PyMySQL |
| Streaming | Apache Spark Structured Streaming, Apache Kafka, Flume |
| Batch analytics | Apache Spark SQL |
| Recommendation | Apache Spark MLlib, ALS, content recall, popularity recall |
| Storage | MySQL 8.0 |
| Build | Maven 3.8+, Scala 2.13.14, JDK 11 |

## Repository Layout

```text
car-demand-analysis/
├── backend/                         # FastAPI service
├── frontend/                        # Vue 3 application
├── simulator/                       # Synthetic data and Flume/Kafka pipeline
├── car-demand-analysis/             # Scala Maven multi-module project
│   ├── common/                      # Shared models, configuration, utilities
│   ├── realtime-analysis/           # Kafka -> Spark -> MySQL
│   ├── offline-analysis/            # Spark SQL batch analytics
│   ├── recommendation-engine/       # Recall and ranking pipeline
│   └── scripts/                     # Build and runtime scripts
├── .env.example
├── .gitattributes
├── .gitignore
├── LICENSE
└── README.md
```

## Data Flow

```text
Synthetic data generator / Flume
              |
              v
          Kafka Topics
  ├── car-user-behavior
  ├── car-search
  ├── car-consult
  ├── car-price-quote
  └── car-loan-inquiry
              |
              v
Spark Structured Streaming
              |
              v
            MySQL
              |
      ┌───────┼──────────┐
      v       v          v
 Realtime  Offline   Recommendation
 Analytics Analytics     Engine
      |       |          |
      └───────┼──────────┘
              v
         FastAPI API
              |
              v
        Vue 3 Frontend
```

## Requirements

- JDK 11
- Maven 3.8+
- Python 3.11+
- Node.js 18+ (20 LTS recommended)
- MySQL 8.0+
- Apache Kafka 3.x
- Apache Flume 1.11 for simulator delivery
- Apache Spark 3.3.1 for Spark jobs

## Configuration

Copy the environment template:

```powershell
Copy-Item .env.example .env
```

Update the local database and authentication values:

```text
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=change-me
MYSQL_DATABASE=car_demand_analysis
SECRET_KEY=replace-with-a-random-secret
PASSWORD_SALT=replace-with-a-random-salt
```

Spark module configuration is stored in:

```text
car-demand-analysis/realtime-analysis/src/main/resources/application.conf
car-demand-analysis/offline-analysis/src/main/resources/application.conf
car-demand-analysis/recommendation-engine/src/main/resources/application.conf
```

The `root/root` database values in the repository are local development
defaults only. Never commit real passwords, tokens, database dumps, or personal
data.

## Quick Start

### 1. Create the database

```sql
CREATE DATABASE car_demand_analysis
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

Create the required realtime, offline, profile, and recommendation tables before
running the pipeline.

### 2. Start the backend

From the repository root:

```powershell
Copy-Item .env.example .env
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --env-file ..\.env --host 0.0.0.0 --port 8000
```

API documentation is available at `http://localhost:8000/docs`.

### 3. Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

The default language is English. Use the language button in the navigation to
switch to Simplified Chinese.

### 4. Build the Scala modules

```powershell
mvn -f car-demand-analysis/pom.xml clean package -DskipTests
```

Runtime scripts:

```bash
./car-demand-analysis/scripts/build-all.sh
./car-demand-analysis/scripts/run-realtime.sh
./car-demand-analysis/scripts/run-offline.sh all
./car-demand-analysis/scripts/run-recommendation.sh
```

### 5. Start the simulator

```bash
cd simulator
python generate_data.py
chmod +x simulatorctl.sh send_data.sh
./simulatorctl.sh start
```

Generated simulator data is treated as runtime output and is excluded from Git.
Run `simulator/generate_data.py` to recreate it when needed.

## Kafka Topics

| Topic | Description |
|-------|-------------|
| `car-user-behavior` | Browsing, favorites, comparison, and related behavior |
| `car-search` | Search events |
| `car-consult` | Car consultation events |
| `car-price-quote` | Quotation and discount events |
| `car-loan-inquiry` | Loan inquiry events |

## Main Output Tables

| Table | Source | Description |
|-------|--------|-------------|
| `realtime_stats` | Realtime analytics | User behavior statistics |
| `realtime_price_stats` | Realtime analytics | Quotation and discount statistics |
| `realtime_loan_stats` | Realtime analytics | Loan inquiry statistics |
| `search_log` | Realtime analytics | Popular search records |
| `operation_log` | Realtime analytics | Consultation and operation records |
| `daily_stats` | Offline analytics | Daily trend statistics |
| `user_profile` | Offline analytics | User preference profiles |
| `recommendation` | Recommendation engine | Ranked recommendation results |

## Documentation

- [Simulator guide](simulator/README.md)
- [Project features and usage](car-demand-analysis/scripts/Project-Features-and-Usage.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development, verification, and
documentation requirements.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and secret-handling
guidance. Never commit real credentials or personal data.

## License

This project is released under the [MIT License](LICENSE).
