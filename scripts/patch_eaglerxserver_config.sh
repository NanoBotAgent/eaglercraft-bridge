#!/usr/bin/env bash
set -euo pipefail

# Patches EaglerXServer listeners.yml after first-run config generation.
# EaglerXServer 1.1.0 defaults inject_address to 0.0.0.0:25577 on BungeeCord,
# but our BungeeCord listens on 0.0.0.0:25565. The inject_address MUST match
# a BungeeCord listener exactly or the pipeline injection won't happen.
#
# NOTE: EaglerXServer 1.1.0 has NO origin_whitelist/allow_all_origins config.
# That was EaglerXBungee. 1.1.0 accepts all origins by default.
# dual_stack: true is also the default, no patching needed.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROXY_DIR="${SCRIPT_DIR}/../proxy"
LISTENERS_FILE="${PROXY_DIR}/plugins/EaglercraftXServer/listeners.yml"

if [ ! -f "$LISTENERS_FILE" ]; then
  echo "[ERROR] listeners.yml not found at ${LISTENERS_FILE}" >&2
  echo "[ERROR] Did the proxy start first to generate configs?" >&2
  exit 1
fi

echo "[INFO] Current listeners.yml (before patching):"
cat "$LISTENERS_FILE"
echo ""

# The ONLY fix needed: change inject_address from 0.0.0.0:25577 to 0.0.0.0:25565
# Use sed with careful matching to handle both quoted and unquoted YAML values
sed -i "s|inject_address:.*0\.0\.0\.0:25577|inject_address: \"0.0.0.0:25565\"|" "$LISTENERS_FILE"

# Verify the patch worked
echo "[INFO] Patched listeners.yml:"
cat "$LISTENERS_FILE"
echo ""

if grep -q 'inject_address.*0\.0\.0\.0:25565' "$LISTENERS_FILE" && ! grep -q '25577' "$LISTENERS_FILE"; then
  echo "[INFO] inject_address patched successfully: 0.0.0.0:25577 -> 0.0.0.0:25565"
elif grep -q 'inject_address.*0\.0\.0\.0:25565' "$LISTENERS_FILE"; then
  echo "[WARN] inject_address set to 25565 but 25577 still present somewhere in config"
else
  echo "[ERROR] Failed to patch inject_address" >&2
  exit 1
fi

echo "[INFO] Config patching complete"
