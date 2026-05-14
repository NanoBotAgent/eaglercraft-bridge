#!/usr/bin/env bash
set -euo pipefail

# Polls until Paper 26.1.2 backend is ready (TCP + log check)
# Timeout: 180 seconds

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"
LOG_FILE="${BACKEND_DIR}/logs/latest.log"

HOST="localhost"
PORT=25566
TIMEOUT=180
START_TIME=$(date +%s)

echo "[INFO] Waiting for backend on ${HOST}:${PORT} (timeout: ${TIMEOUT}s)..."

while true; do
    ELAPSED=$(( $(date +%s) - START_TIME ))

    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        echo "[ERROR] Timeout waiting for backend after ${TIMEOUT}s" >&2
        exit 1
    fi

    # Print progress every 15 seconds
    if [ $((ELAPSED % 15)) -eq 0 ] && [ "$ELAPSED" -gt 0 ]; then
        echo "[INFO] Still waiting... ${ELAPSED}s elapsed"
    fi

    # Check TCP connection
    if (echo > /dev/tcp/"$HOST"/"$PORT") 2>/dev/null; then
        # Also check log for "Done ("
        if [ -f "$LOG_FILE" ] && grep -q "Done (" "$LOG_FILE" 2>/dev/null; then
            echo "[INFO] Backend is ready after ${ELAPSED}s"
            exit 0
        fi
    fi

    sleep 2
done
