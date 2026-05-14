#!/usr/bin/env bash
set -euo pipefail

# Downloads the latest EaglerXServer.jar from GitHub releases
# Placed in proxy/plugins/ for BungeeCord to load

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${SCRIPT_DIR}/../proxy/plugins"
DEST="${DEST_DIR}/EaglerXServer.jar"

mkdir -p "$DEST_DIR"

echo "[INFO] Fetching latest EaglerXServer release info..."

API_RESPONSE=$(curl -sSf "https://api.github.com/repos/lax1dude/eaglerxserver/releases/latest") || {
    echo "[ERROR] Failed to fetch EaglerXServer release info from GitHub API" >&2
    exit 1
}

TAG=$(echo "$API_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])") || {
    echo "[ERROR] Failed to parse EaglerXServer release tag" >&2
    exit 1
}

DOWNLOAD_URL=$(echo "$API_RESPONSE" | python3 -c "
import sys, json
assets = json.load(sys.stdin).get('assets', [])
for a in assets:
    if a['name'] == 'EaglerXServer.jar':
        print(a['browser_download_url'])
        break
else:
    print('')
") || {
    echo "[ERROR] Failed to parse EaglerXServer asset list" >&2
    exit 1
}

if [ -z "$DOWNLOAD_URL" ]; then
    echo "[ERROR] EaglerXServer.jar asset not found in release ${TAG}" >&2
    exit 1
fi

echo "[INFO] Downloading EaglerXServer ${TAG}..."
curl -sSfL -o "$DEST" "$DOWNLOAD_URL" || {
    echo "[ERROR] Failed to download EaglerXServer.jar" >&2
    exit 1
}

SIZE=$(stat -c%s "$DEST" 2>/dev/null || stat -f%z "$DEST" 2>/dev/null)
if [ "$SIZE" -lt 1048576 ]; then
    echo "[ERROR] Downloaded EaglerXServer.jar is only ${SIZE} bytes (expected >1MB)" >&2
    rm -f "$DEST"
    exit 1
fi

echo "[INFO] Downloaded EaglerXServer version ${TAG} -> ${DEST}"
