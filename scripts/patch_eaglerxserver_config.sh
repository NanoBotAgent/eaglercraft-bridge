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

# Disable all rate limiters for CI testing.
# The default config has rate limiters for ip, login, motd, query, http.
# Each has an "enable" flag we set to false.
# We use Python for this since sed on nested YAML is fragile.
python3 -c "
import yaml

with open('${LISTENERS_FILE}', 'r') as f:
    config = yaml.safe_load(f)

# Walk the listener list and disable all rate limiters
if config and 'listener_list' in config:
    for listener in config['listener_list']:
        if 'ratelimit' in listener:
            rl = listener['ratelimit']
            for key in ('ip', 'login', 'motd', 'query', 'http'):
                if key in rl and isinstance(rl[key], dict):
                    rl[key]['enable'] = False

with open('${LISTENERS_FILE}', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    print('[INFO] All rate limiters disabled for CI')
" || echo "[WARN] Failed to disable rate limiters via Python, continuing with sed fallback"

# Fallback: sed-based rate limiter disabling if python failed
# This is a best-effort approach for nested YAML
sed -i '/^[[:space:]]*#/!s|\(enable:[[:space:]]*\)true|\1false|' "$LISTENERS_FILE" 2>/dev/null || true

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
