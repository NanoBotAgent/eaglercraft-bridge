#!/usr/bin/env bash
set -euo pipefail

# Patches EaglerXServer listeners.yml after first-run config generation.
# EaglerXServer 1.1.0 defaults inject_address to 0.0.0.0:25577 on BungeeCord,
# but our BungeeCord listens on 0.0.0.0:25565. The inject_address MUST match
# a BungeeCord listener exactly or the pipeline injection won't happen.
#
# Also disables all rate limiters for CI testing, since test connections
# come from localhost and need to fire rapidly without throttling.
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
sed -i '/^[[:space:]]*#/!s|^\([[:space:]]*inject_address:[[:space:]]*\).*|\10.0.0.0:25565|' "$LISTENERS_FILE"

# Disable all rate limiters for CI testing using Python/YAML.
# Pass the listeners file path as a command-line argument (not via heredoc
# variable expansion which breaks with single-quoted heredoc delimiters).
python3 - "$LISTENERS_FILE" << 'PYTHON'
import sys
import yaml

path = sys.argv[1]
with open(path, "r") as f:
    config = yaml.safe_load(f)

changed = False
if config and "listener_list" in config:
    for listener in config["listener_list"]:
        if "ratelimit" in listener and isinstance(listener["ratelimit"], dict):
            rl = listener["ratelimit"]
            for key in ("ip", "login", "motd", "query", "http"):
                if key in rl and isinstance(rl[key], dict):
                    if rl[key].get("enable", False):
                        rl[key]["enable"] = False
                        changed = True

if changed:
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    print("[INFO] All rate limiters disabled for CI")
else:
    print("[INFO] No rate limiters found to disable (may already be off)")
PYTHON

# Validate the patched file is still valid YAML
python3 -c "import yaml; yaml.safe_load(open('${LISTENERS_FILE}'))" && \
    echo "[PASS] listeners.yml valid YAML after patching" || \
    { echo "[FAIL] listeners.yml corrupted by patcher" >&2; exit 1; }

# Verify the inject_address patch applied correctly
if grep -q '^[[:space:]]*inject_address:[[:space:]]*0\.0\.0\.0:25565' "$LISTENERS_FILE"; then
    echo "[INFO] inject_address patched successfully to 0.0.0.0:25565"
else
    echo "[ERROR] Failed to patch inject_address" >&2
    exit 1
fi

echo "[INFO] Config patching complete"
