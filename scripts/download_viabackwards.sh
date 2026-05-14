#!/usr/bin/env bash
set -euo pipefail

# Downloads the latest ViaBackwards.jar from GitHub releases
# Placed in proxy/plugins/ for BungeeCord to load

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${SCRIPT_DIR}/../proxy/plugins"

mkdir -p "$DEST_DIR"

echo "[INFO] Fetching latest ViaBackwards release info..."

API_RESPONSE=$(curl -sSf "https://api.github.com/repos/ViaVersion/ViaBackwards/releases/latest") || {
    echo "[ERROR] Failed to fetch ViaBackwards release info from GitHub API" >&2
    exit 1
}

TAG=$(echo "$API_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])") || {
    echo "[ERROR] Failed to parse ViaBackwards release tag" >&2
    exit 1
}

DOWNLOAD_URL=$(echo "$API_RESPONSE" | python3 -c "
import sys, json
assets = json.load(sys.stdin).get('assets', [])
for a in assets:
    if a['name'].startswith('ViaBackwards-') and a['name'].endswith('.jar'):
        print(a['browser_download_url'])
        break
else:
    print('')
") || {
    echo "[ERROR] Failed to parse ViaBackwards asset list" >&2
    exit 1
}

if [ -z "$DOWNLOAD_URL" ]; then
    echo "[ERROR] ViaBackwards jar asset not found in release ${TAG}" >&2
    exit 1
fi

FILENAME=$(echo "$API_RESPONSE" | python3 -c "
import sys, json
assets = json.load(sys.stdin).get('assets', [])
for a in assets:
    if a['name'].startswith('ViaBackwards-') and a['name'].endswith('.jar'):
        print(a['name'])
        break
else:
    print('ViaBackwards.jar')
")

DEST="${DEST_DIR}/${FILENAME}"

echo "[INFO] Downloading ViaBackwards ${TAG}..."
curl -sSfL -o "$DEST" "$DOWNLOAD_URL" || {
    echo "[ERROR] Failed to download ViaBackwards" >&2
    exit 1
}

SIZE=$(stat -c%s "$DEST" 2>/dev/null || stat -f%z "$DEST" 2>/dev/null)
if [ "$SIZE" -lt 1048576 ]; then
    echo "[ERROR] Downloaded ViaBackwards jar is only ${SIZE} bytes (expected >1MB)" >&2
    rm -f "$DEST"
    exit 1
fi

echo "[INFO] Downloaded ViaBackwards version ${TAG} -> ${DEST}"
