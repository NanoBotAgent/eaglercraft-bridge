#!/usr/bin/env bash
set -euo pipefail

# Downloads the latest BungeeCord.jar from md-5 CI server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${SCRIPT_DIR}/../proxy"
DEST="${DEST_DIR}/BungeeCord.jar"

mkdir -p "$DEST_DIR"

echo "[INFO] Downloading BungeeCord from md-5 CI..."

curl -sSfL -o "$DEST" "https://ci.md-5.net/job/BungeeCord/lastSuccessfulBuild/artifact/bootstrap/target/BungeeCord.jar" || {
    echo "[ERROR] Failed to download BungeeCord.jar from md-5 CI" >&2
    exit 1
}

SIZE=$(stat -c%s "$DEST" 2>/dev/null || stat -f%z "$DEST" 2>/dev/null)
if [ "$SIZE" -lt 1048576 ]; then
    echo "[ERROR] Downloaded BungeeCord.jar is only ${SIZE} bytes (expected >1MB)" >&2
    rm -f "$DEST"
    exit 1
fi

echo "[INFO] Downloaded BungeeCord -> ${DEST}"
