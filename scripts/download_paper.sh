#!/usr/bin/env bash
set -euo pipefail

# Downloads the latest Paper 26.1.2 build via PaperMC fill-data API
# Paper API v1 uses SHA-based download URLs, not the v2 path-style URLs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${SCRIPT_DIR}/../backend"
DEST="${DEST_DIR}/paper-26.1.2.jar"

mkdir -p "$DEST_DIR"

echo "[INFO] Fetching Paper 26.1.2 builds list..."

BUILDS_JSON=$(curl -sSf "https://api.papermc.io/v2/projects/paper/versions/26.1.2/builds") || {
  echo "[ERROR] Failed to fetch Paper 26.1.2 builds from PaperMC API" >&2
  exit 1
}

BUILD_AND_SHA=$(echo "$BUILDS_JSON" | python3 -c "
import sys, json
builds = json.load(sys.stdin).get('builds', [])
if not builds:
    sys.exit(1)
latest = max(builds, key=lambda b: b.get('build', 0))
build_num = latest['build']
# Find the paper jar download entry
for ch in latest.get('changes', []):
    pass  # changes don't have SHA
downloads = latest.get('downloads', {})
paper_dl = downloads.get('application', downloads.get('paper', {}))
sha = paper_dl.get('sha256', '') if isinstance(paper_dl, dict) else ''
print(f'{build_num} {sha}')
") || {
  echo "[ERROR] Failed to parse Paper 26.1.2 build list" >&2
  exit 1
}

BUILD=$(echo "$BUILD_AND_SHA" | awk '{print $1}')
SHA=$(echo "$BUILD_AND_SHA" | awk '{print $2}')

if [ -n "$SHA" ]; then
  # fill-data API v1 with SHA
  DOWNLOAD_URL="https://fill-data.papermc.io/v1/objects/${SHA}/paper-26.1.2-${BUILD}.jar"
else
  # Fallback to v2 API path-style URL
  DOWNLOAD_URL="https://api.papermc.io/v2/projects/paper/versions/26.1.2/builds/${BUILD}/downloads/paper-26.1.2-${BUILD}.jar"
fi

echo "[INFO] Downloading Paper 26.1.2 build #${BUILD}..."
curl -sSfL -o "$DEST" "$DOWNLOAD_URL" || {
  echo "[ERROR] Failed to download Paper 26.1.2 build #${BUILD}" >&2
  exit 1
}

SIZE=$(stat -c%s "$DEST" 2>/dev/null || stat -f%z "$DEST" 2>/dev/null)
if [ "$SIZE" -lt 10485760 ]; then
  echo "[ERROR] Downloaded Paper jar is only ${SIZE} bytes (expected >10MB)" >&2
  rm -f "$DEST"
  exit 1
fi

echo "[INFO] Downloaded Paper 26.1.2 build #${BUILD} -> ${DEST}"
