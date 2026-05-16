#!/usr/bin/env bash
set -euo pipefail

# Patches EaglerXServer listeners.yml after first-run config generation.
# EaglerXServer overwrites listeners.yml on first boot, so we need to
# update it AFTER the plugin generates defaults.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROXY_DIR="${SCRIPT_DIR}/../proxy"
LISTENERS_FILE="${PROXY_DIR}/plugins/EaglercraftXServer/listeners.yml"

if [ ! -f "$LISTENERS_FILE" ]; then
  echo "[ERROR] listeners.yml not found at ${LISTENERS_FILE}" >&2
  echo "[ERROR] Did the proxy start first to generate configs?" >&2
  exit 1
fi

echo "[INFO] Patching EaglerXServer listeners.yml..."

# Use Python for reliable YAML patching
python3 << 'PYEOF'
import yaml, sys, os

path = os.environ.get("LISTENERS_FILE", sys.argv[1] if len(sys.argv) > 1 else "")

with open(path) as f:
    data = yaml.safe_load(f)

changed = False

# Ensure listeners list exists and has at least one entry
if not data or 'listeners' not in data or not isinstance(data['listeners'], list) or len(data['listeners']) == 0:
    # Create a default listener entry
    data = {'listeners': [{'inject_address': '0.0.0.0:25565'}]}
    changed = True

listener = data['listeners'][0]

# Set inject_address to match BungeeCord's host
if listener.get('inject_address') != '0.0.0.0:25565':
    listener['inject_address'] = '0.0.0.0:25565'
    changed = True

# Enable allow_all_origins for testing
ow = listener.get('origin_whitelist', {})
if not ow.get('allow_all_origins', False):
    ow['allow_all_origins'] = True
    listener['origin_whitelist'] = ow
    changed = True

# Enable eagler and vanilla players
if listener.get('allow_eagler_players') is not True:
    listener['allow_eagler_players'] = True
    changed = True

if listener.get('allow_vanilla_players') is not True:
    listener['allow_vanilla_players'] = True
    changed = True

with open(path, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

print(f"[INFO] listeners.yml patched (changed={changed})")
PYEOF

echo "[INFO] Patching complete"
