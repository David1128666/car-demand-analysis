#!/bin/bash
# Real-time Analysis: reads Kafka -> Spark Structured Streaming -> MySQL
# Usage: ./run-realtime.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

JAR_FILE="$PROJECT_DIR/realtime-analysis/target/realtime-analysis-1.0.0-jar-with-dependencies.jar"

if [ ! -f "$JAR_FILE" ]; then
    echo "[ERROR] JAR not found: $JAR_FILE"
    echo "[INFO] Building project..."
    cd "$PROJECT_DIR" && mvn clean package -pl realtime-analysis -am -DskipTests
fi

SPARK_HOME="${SPARK_HOME:-/opt/spark}"

echo "[INFO] Starting Real-time Analysis..."
"$SPARK_HOME/bin/spark-submit" \
    --class com.car.analysis.realtime.RealTimeAnalysisApp \
    --master local[*] \
    --conf spark.sql.adaptive.enabled=true \
    --conf spark.sql.adaptive.coalescePartitions.enabled=true \
    --conf spark.streaming.stopGracefullyOnShutdown=true \
    "$JAR_FILE"
