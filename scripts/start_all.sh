#!/usr/bin/env bash
set -euo pipefail

# Starts backend then proxy in sequence

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[INFO] === Starting Eaglercraft Bridge ==="

echo "[INFO] Starting backend..."
bash "${SCRIPT_DIR}/start_backend.sh"

echo "[INFO] Waiting for backend to be ready..."
bash "${SCRIPT_DIR}/wait_for_backend.sh"

echo "[INFO] Starting proxy..."
bash "${SCRIPT_DIR}/start_proxy.sh"

echo "[INFO] Waiting for proxy to be ready..."
bash "${SCRIPT_DIR}/wait_for_proxy.sh"

echo "[INFO] === Eaglercraft Bridge is running ==="
