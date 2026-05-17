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

# Patch inject_address: change whatever value it has to 0.0.0.0:25565
# Pattern: skip comment lines, then match lines where inject_address is the
# YAML key (first word after leading whitespace), preserving indentation.
#   /^[[:space:]]*#/!  — skip lines starting with optional whitespace then #
#   ^\([[:space:]]*inject_address:[[:space:]]*\)  — capture key + spacing
#   .*  — replace entire value (quoted or unquoted)
#   \10.0.0.0:25565  — preserved key + new value (unquoted, valid YAML string)
sed -i '/^[[:space:]]*#/!s|^\([[:space:]]*inject_address:[[:space:]]*\).*|\10.0.0.0:25565|' "$LISTENERS_FILE"

# Validate the patched file is still valid YAML
python3 -c "import yaml; yaml.safe_load(open('${LISTENERS_FILE}'))" && \
  echo "[PASS] listeners.yml valid YAML after patching" || {
  echo "[FAIL] listeners.yml corrupted by patcher" >&2
  exit 1
}

# Verify the patch applied correctly
if grep -q '^[[:space:]]*inject_address:[[:space:]]*0\.0\.0\.0:25565' "$LISTENERS_FILE"; then
  echo "[INFO] inject_address patched successfully to 0.0.0.0:25565"
else
  echo "[ERROR] Failed to patch inject_address" >&2
  exit 1
fi

echo "[INFO] Config patching complete"
