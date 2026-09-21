#!/bin/bash
# Build all modules
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "[INFO] Building all modules..."
cd "$PROJECT_DIR" && mvn clean package -DskipTests

echo ""
echo "[INFO] Build complete. Artifacts:"
ls -la realtime-analysis/target/*.jar offline-analysis/target/*.jar recommendation-engine/target/*.jar 2>/dev/null
