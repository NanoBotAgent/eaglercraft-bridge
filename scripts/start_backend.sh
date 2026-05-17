#!/usr/bin/env bash
set -euo pipefail

# Starts the Paper 26.1.2 backend server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"

cd "$BACKEND_DIR"

mkdir -p logs

echo "[INFO] Starting Paper 26.1.2 backend..."

java -Xms512M -Xmx2G \
  -XX:+UseG1GC \
  -XX:+ParallelRefProcEnabled \
  -XX:MaxGCPauseMillis=200 \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+DisableExplicitGC \
  -XX:G1NewSizePercent=30 \
  -XX:G1MaxNewSizePercent=40 \
  -XX:G1HeapRegionSize=8M \
  -XX:G1ReservePercent=20 \
  -jar paper-26.1.2.jar nogui \
  > logs/latest.log 2>&1 &

PID=$!
echo "$PID" > server.pid
disown $PID
echo "[INFO] Paper 26.1.2 backend started (PID: ${PID})"
