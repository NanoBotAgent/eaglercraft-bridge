#!/usr/bin/env bash
set -euo pipefail

# Patches EaglerXServer listeners.yml after first-run config generation.
# EaglerXServer defaults to port 25577 but BungeeCord listens on 25565.
# The inject_address MUST match the BungeeCord listener host exactly.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROXY_DIR="${SCRIPT_DIR}/../proxy"
LISTENERS_FILE="${PROXY_DIR}/plugins/EaglercraftXServer/listeners.yml"

if [ ! -f "$LISTENERS_FILE" ]; then
  echo "[ERROR] listeners.yml not found at ${LISTENERS_FILE}" >&2
  echo "[ERROR] Did the proxy start first to generate configs?" >&2
  exit 1
fi

echo "[INFO] Current listeners.yml:"
cat "$LISTENERS_FILE"
echo ""

# Use sed for simple, reliable patching (no Python dependency needed)
# Only replace the value part after the key — preserves leading whitespace/indentation

# Fix 1: inject_address — EaglerXServer defaults to 0.0.0.0:25577, must be 25565 to match BungeeCord
sed -i 's|inject_address:.*|inject_address: "0.0.0.0:25565"|' "$LISTENERS_FILE"

# Fix 2: allow_all_origins — set to true for testing
sed -i 's|allow_all_origins:.*|allow_all_origins: true|' "$LISTENERS_FILE"

# Fix 3: allow_eagler_players — set to true
sed -i 's|allow_eagler_players:.*|allow_eagler_players: true|' "$LISTENERS_FILE"

# Fix 4: allow_vanilla_players — set to true
sed -i 's|allow_vanilla_players:.*|allow_vanilla_players: true|' "$LISTENERS_FILE"

# Verify the patch worked
echo "[INFO] Patched listeners.yml:"
cat "$LISTENERS_FILE"
echo ""

if grep -q 'inject_address: "0.0.0.0:25565"' "$LISTENERS_FILE"; then
  echo "[INFO] inject_address patched successfully to 0.0.0.0:25565"
else
  echo "[ERROR] Failed to patch inject_address" >&2
  exit 1
fi

if grep -q 'allow_all_origins: true' "$LISTENERS_FILE"; then
  echo "[INFO] allow_all_origins patched successfully"
else
  echo "[WARN] allow_all_origins not found in config"
fi

echo "[INFO] Config patching complete"
