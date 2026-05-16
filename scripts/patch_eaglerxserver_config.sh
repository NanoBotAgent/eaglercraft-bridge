#!/usr/bin/env bash
set -euo pipefail

# Patches EaglerXServer listeners.yml after first-run config generation.
# Uses sed/grep instead of PyYAML to avoid dependency issues.

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

# Patch the file using Python without PyYAML (just regex-based replacement)
python3 << 'PYEOF'
import re, sys

path = sys.argv[1] if len(sys.argv) > 1 else ""
with open(path) as f:
    content = f.read()

changed = False

# Fix inject_address
if 'inject_address' in content:
    # Replace whatever value inject_address has
    new_content = re.sub(r'inject_address:\s*["\']?[^"\n]*["\']?', 'inject_address: "0.0.0.0:25565"', content)
    if new_content != content:
        content = new_content
        changed = True
else:
    # Add inject_address to the first listener entry
    content = content.replace('- ', '- inject_address: "0.0.0.0:25565"\n  ', 1)
    changed = True

# Ensure allow_all_origins: true
if 'allow_all_origins' in content:
    new_content = re.sub(r'allow_all_origins:\s*false', 'allow_all_origins: true', content)
    if new_content != content:
        content = new_content
        changed = True
else:
    # Add it under origin_whitelist
    if 'origin_whitelist:' in content:
        content = content.replace('origin_whitelist:', 'origin_whitelist:\n    allow_all_origins: true')
        changed = True
    else:
        content = content.rstrip() + '\n    origin_whitelist:\n      allow_all_origins: true\n'
        changed = True

# Ensure allow_eagler_players: true
if 'allow_eagler_players' in content:
    new_content = re.sub(r'allow_eagler_players:\s*false', 'allow_eagler_players: true', content)
    if new_content != content:
        content = new_content
        changed = True

# Ensure allow_vanilla_players: true
if 'allow_vanilla_players' in content:
    new_content = re.sub(r'allow_vanilla_players:\s*false', 'allow_vanilla_players: true', content)
    if new_content != content:
        content = new_content
        changed = True

with open(path, 'w') as f:
    f.write(content)

print(f"[INFO] listeners.yml patched (changed={changed})")
PYEOF "$LISTENERS_FILE"

echo "[INFO] Patched listeners.yml:"
cat "$LISTENERS_FILE"
