#!/usr/bin/env bash
set -euo pipefail

# Starts the BungeeCord proxy

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROXY_DIR="${SCRIPT_DIR}/../proxy"

cd "$PROXY_DIR"

mkdir -p logs

echo "[INFO] Starting BungeeCord proxy..."

java -Xms256M -Xmx512M \
  -XX:+UseG1GC \
  -jar BungeeCord.jar \
  > logs/latest.log 2>&1 &

PID=$!
echo "$PID" > server.pid
disown $PID
echo "[INFO] BungeeCord proxy started (PID: ${PID})"
