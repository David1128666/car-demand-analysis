#!/bin/bash
# Recommendation Engine: ALS + Content-Based + Hot -> MySQL
# Usage: ./run-recommendation.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

JAR_FILE="$PROJECT_DIR/recommendation-engine/target/recommendation-engine-1.0.0-jar-with-dependencies.jar"

if [ ! -f "$JAR_FILE" ]; then
    echo "[ERROR] JAR not found: $JAR_FILE"
    echo "[INFO] Building project..."
    cd "$PROJECT_DIR" && mvn clean package -pl recommendation-engine -am -DskipTests
fi

SPARK_HOME="${SPARK_HOME:-/opt/spark}"

echo "[INFO] Starting Recommendation Engine..."
"$SPARK_HOME/bin/spark-submit" \
    --class com.car.analysis.recommendation.RecommendationApp \
    --master local[*] \
    --conf spark.sql.adaptive.enabled=true \
    --conf spark.sql.adaptive.coalescePartitions.enabled=true \
    "$JAR_FILE"
