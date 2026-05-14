#!/usr/bin/env bash
set -euo pipefail

# Gracefully stops both proxy and backend servers

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROXY_DIR="${SCRIPT_DIR}/../proxy"
BACKEND_DIR="${SCRIPT_DIR}/../backend"

echo "[INFO] Stopping Eaglercraft Bridge..."

# Stop proxy first
if [ -f "${PROXY_DIR}/server.pid" ]; then
    PROXY_PID=$(cat "${PROXY_DIR}/server.pid")
    if kill -0 "$PROXY_PID" 2>/dev/null; then
        echo "[INFO] Stopping proxy (PID: ${PROXY_PID})..."
        kill "$PROXY_PID" 2>/dev/null || true
        # Wait up to 10 seconds for graceful shutdown
        for i in $(seq 1 10); do
            if ! kill -0 "$PROXY_PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        # Force kill if still running
        if kill -0 "$PROXY_PID" 2>/dev/null; then
            echo "[WARN] Force killing proxy..."
            kill -9 "$PROXY_PID" 2>/dev/null || true
        fi
        echo "[INFO] Proxy stopped"
    else
        echo "[INFO] Proxy already stopped"
    fi
    rm -f "${PROXY_DIR}/server.pid"
fi

# Stop backend
if [ -f "${BACKEND_DIR}/server.pid" ]; then
    BACKEND_PID=$(cat "${BACKEND_DIR}/server.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "[INFO] Stopping backend (PID: ${BACKEND_PID})..."
        kill "$BACKEND_PID" 2>/dev/null || true
        # Wait up to 15 seconds for graceful shutdown
        for i in $(seq 1 15); do
            if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        # Force kill if still running
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo "[WARN] Force killing backend..."
            kill -9 "$BACKEND_PID" 2>/dev/null || true
        fi
        echo "[INFO] Backend stopped"
    else
        echo "[INFO] Backend already stopped"
    fi
    rm -f "${BACKEND_DIR}/server.pid"
fi

echo "[INFO] Eaglercraft Bridge stopped"
