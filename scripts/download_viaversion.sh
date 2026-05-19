#!/usr/bin/env bash
set -euo pipefail

# Downloads the latest ViaVersion.jar from GitHub releases
# Placed in proxy/plugins/ViaVersion/ — ViaBungee loads ViaVersion core
# as a library from this subfolder, NOT as a BungeeCord plugin directly.
# Putting it in proxy/plugins/ causes NoClassDefFoundError: JavaPlugin.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${SCRIPT_DIR}/../proxy/plugins/ViaVersion"

mkdir -p "$DEST_DIR"

echo "[INFO] Fetching latest ViaVersion release info..."

API_RESPONSE=$(curl -sSf "https://api.github.com/repos/ViaVersion/ViaVersion/releases/latest") || {
    echo "[ERROR] Failed to fetch ViaVersion release info from GitHub API" >&2
    exit 1
}

TAG=$(echo "$API_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])") || {
    echo "[ERROR] Failed to parse ViaVersion release tag" >&2
    exit 1
}

DOWNLOAD_URL=$(echo "$API_RESPONSE" | python3 -c "
import sys, json
assets = json.load(sys.stdin).get('assets', [])
for a in assets:
    if a['name'].startswith('ViaVersion-') and a['name'].endswith('.jar'):
        print(a['browser_download_url'])
        break
else:
    print('')
") || {
    echo "[ERROR] Failed to parse ViaVersion asset list" >&2
    exit 1
}

if [ -z "$DOWNLOAD_URL" ]; then
    echo "[ERROR] ViaVersion jar asset not found in release ${TAG}" >&2
    exit 1
fi

FILENAME=$(echo "$API_RESPONSE" | python3 -c "
import sys, json
assets = json.load(sys.stdin).get('assets', [])
for a in assets:
    if a['name'].startswith('ViaVersion-') and a['name'].endswith('.jar'):
        print(a['name'])
        break
else:
    print('ViaVersion.jar')
")

DEST="${DEST_DIR}/${FILENAME}"

echo "[INFO] Downloading ViaVersion ${TAG}..."
curl -sSfL -o "$DEST" "$DOWNLOAD_URL" || {
    echo "[ERROR] Failed to download ViaVersion" >&2
    exit 1
}

SIZE=$(stat -c%s "$DEST" 2>/dev/null || stat -f%z "$DEST" 2>/dev/null)
if [ "$SIZE" -lt 1048576 ]; then
    echo "[ERROR] Downloaded ViaVersion jar is only ${SIZE} bytes (expected >1MB)" >&2
    rm -f "$DEST"
    exit 1
fi

echo "[INFO] Downloaded ViaVersion version ${TAG} -> ${DEST}"
