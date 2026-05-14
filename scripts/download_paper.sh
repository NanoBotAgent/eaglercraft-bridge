#!/usr/bin/env bash
set -euo pipefail

# Downloads the latest stable Paper 26.1.2 build via PaperMC fill API v3
# v3 API: https://fill.papermc.io/v3/projects/paper/versions/26.1.2/builds

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${SCRIPT_DIR}/../backend"
DEST="${DEST_DIR}/paper-26.1.2.jar"

mkdir -p "$DEST_DIR"

echo "[INFO] Fetching Paper 26.1.2 builds list..."

BUILDS_JSON=$(curl -sSf -H "User-Agent: eaglercraft-bridge/1.0" \
  "https://fill.papermc.io/v3/projects/paper/versions/26.1.2/builds") || {
  echo "[ERROR] Failed to fetch Paper 26.1.2 builds from PaperMC API" >&2
  exit 1
}

DOWNLOAD_URL=$(echo "$BUILDS_JSON" | python3 -c "
import sys, json
builds = json.load(sys.stdin)
if not builds:
    sys.exit(1)
# Prefer stable builds, fall back to latest any channel
stable = [b for b in builds if b.get('channel') == 'STABLE']
latest = stable[-1] if stable else builds[-1]
dl = latest.get('downloads', {}).get('server:default', {})
url = dl.get('url', '')
if not url:
    sys.exit(1)
print(url)
") || {
  echo "[ERROR] Failed to parse Paper 26.1.2 build list" >&2
  exit 1
}

echo "[INFO] Downloading Paper 26.1.2 from ${DOWNLOAD_URL}..."
curl -sSfL -o "$DEST" "$DOWNLOAD_URL" || {
  echo "[ERROR] Failed to download Paper 26.1.2" >&2
  exit 1
}

SIZE=$(stat -c%s "$DEST" 2>/dev/null || stat -f%z "$DEST" 2>/dev/null)
if [ "$SIZE" -lt 10485760 ]; then
  echo "[ERROR] Downloaded Paper jar is only ${SIZE} bytes (expected >10MB)" >&2
  rm -f "$DEST"
  exit 1
fi

echo "[INFO] Downloaded Paper 26.1.2 -> ${DEST} (${SIZE} bytes)"
