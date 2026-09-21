#!/bin/bash
# Offline Analysis: SparkSQL reads MySQL -> batch analytics -> MySQL
# Usage: ./run-offline.sh [task: trend|profile|preference|daily|all]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

TASK="${1:-all}"

JAR_FILE="$PROJECT_DIR/offline-analysis/target/offline-analysis-1.0.0-jar-with-dependencies.jar"

if [ ! -f "$JAR_FILE" ]; then
    echo "[ERROR] JAR not found: $JAR_FILE"
    echo "[INFO] Building project..."
    cd "$PROJECT_DIR" && mvn clean package -pl offline-analysis -am -DskipTests
fi

SPARK_HOME="${SPARK_HOME:-/opt/spark}"

echo "[INFO] Starting Offline Analysis (task=$TASK)..."
"$SPARK_HOME/bin/spark-submit" \
    --class com.car.analysis.offline.OfflineAnalysisApp \
    --master local[*] \
    --conf spark.sql.adaptive.enabled=true \
    "$JAR_FILE" "$TASK"
