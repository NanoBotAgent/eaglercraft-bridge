#!/usr/bin/env bash
set -euo pipefail

# Starts BungeeCord proxy with two-pass startup for EaglerXServer.
# Pass 1: Start proxy, let EaglerXServer generate its default configs, then stop.
# Pass 2: Patch the generated configs, then start proxy for real.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROXY_DIR="${SCRIPT_DIR}/../proxy"

cd "$PROXY_DIR"
mkdir -p logs

echo "[INFO] === Two-pass proxy startup ==="

# --- PASS 1: Generate configs ---
echo "[INFO] Pass 1: Starting proxy to generate EaglerXServer configs..."

java -Xms256M -Xmx512M \
  -XX:+UseG1GC \
  -jar BungeeCord.jar \
  > logs/latest.log 2>&1 &

PID=$!
echo "$PID" > server.pid
echo "[INFO] BungeeCord proxy started (PID: ${PID})"

# Wait for proxy to fully boot and EaglerXServer to generate configs
echo "[INFO] Waiting for proxy to boot and generate configs..."
TIMEOUT=90
START_TIME=$(date +%s)
while true; do
  ELAPSED=$(( $(date +%s) - START_TIME ))
  if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
    echo "[ERROR] Timeout waiting for proxy first boot" >&2
    kill "$PID" 2>/dev/null || true
    exit 1
  fi
  # Check if proxy is listening AND EaglerXServer generated its configs
  if [ -f logs/latest.log ] && grep -q "Listening on" logs/latest.log 2>/dev/null; then
    if [ -f plugins/EaglercraftXServer/listeners.yml ]; then
      echo "[INFO] Proxy booted and configs generated after ${ELAPSED}s"
      break
    fi
  fi
  sleep 2
done

# Give it a moment more to finish writing configs
sleep 3

# Stop the proxy
echo "[INFO] Stopping proxy (pass 1)..."
kill "$PID" 2>/dev/null || true
sleep 5
kill -9 "$PID" 2>/dev/null || true
rm -f server.pid

# --- Patch configs ---
echo "[INFO] Patching EaglerXServer configs..."
export LISTENERS_FILE="${PROXY_DIR}/plugins/EaglercraftXServer/listeners.yml"
bash "${SCRIPT_DIR}/patch_eaglerxserver_config.sh"

# --- PASS 2: Start for real ---
echo "[INFO] Pass 2: Starting proxy with patched configs..."

# Clear the old log so wait_for_proxy detects the fresh boot
> logs/latest.log

java -Xms256M -Xmx512M \
  -XX:+UseG1GC \
  -jar BungeeCord.jar \
  > logs/latest.log 2>&1 &

PID=$!
echo "$PID" > server.pid
echo "[INFO] BungeeCord proxy started (PID: ${PID})"
echo "[INFO] === Two-pass startup complete ==="
