#!/usr/bin/env bash
set -euo pipefail

# Polls until BungeeCord proxy + EaglerXServer WebSocket is ready
# Timeout: 60 seconds

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROXY_DIR="${SCRIPT_DIR}/../proxy"
LOG_FILE="${PROXY_DIR}/logs/latest.log"

HOST="localhost"
PORT=25565
TIMEOUT=60
START_TIME=$(date +%s)

echo "[INFO] Waiting for proxy on ${HOST}:${PORT} (timeout: ${TIMEOUT}s)..."

while true; do
    ELAPSED=$(( $(date +%s) - START_TIME ))

    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        echo "[ERROR] Timeout waiting for proxy after ${TIMEOUT}s" >&2
        exit 1
    fi

    # Print progress every 15 seconds
    if [ $((ELAPSED % 15)) -eq 0 ] && [ "$ELAPSED" -gt 0 ]; then
        echo "[INFO] Still waiting... ${ELAPSED}s elapsed"
    fi

    # Check TCP connection
    if (echo > /dev/tcp/"$HOST"/"$PORT") 2>/dev/null; then
        # Also check log for "Listening on"
        if [ -f "$LOG_FILE" ] && grep -q "Listening on" "$LOG_FILE" 2>/dev/null; then
            # Verify WebSocket with Python quick check
            if python3 -c "
import asyncio, websockets, sys
async def check():
    try:
        async with websockets.connect('ws://${HOST}:${PORT}', close_timeout=2) as ws:
            pass
        return True
    except Exception:
        return False
result = asyncio.run(check())
sys.exit(0 if result else 1)
" 2>/dev/null; then
                echo "[INFO] Proxy + WebSocket is ready after ${ELAPSED}s"
                exit 0
            fi
        fi
    fi

    sleep 2
done
