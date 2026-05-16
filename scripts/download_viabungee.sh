#!/usr/bin/env bash
set -euo pipefail

# Downloads ViaBungee (BungeeCord loader for ViaVersion) from Hangar
# ViaVersion/ViaBackwards universal jars need ViaBungee on BungeeCord

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${SCRIPT_DIR}/../proxy/plugins"
mkdir -p "$DEST_DIR"

VIABUNGEE_VERSION="0.4.0"
DOWNLOAD_URL="https://hangarcdn.papermc.io/plugins/ViaVersion/ViaBungee/versions/${VIABUNGEE_VERSION}/WATERFALL/ViaBungee-${VIABUNGEE_VERSION}.jar"
DEST="${DEST_DIR}/ViaBungee-${VIABUNGEE_VERSION}.jar"

echo "[INFO] Downloading ViaBungee ${VIABUNGEE_VERSION}..."
curl -sSfL -o "$DEST" "$DOWNLOAD_URL" || {
  echo "[ERROR] Failed to download ViaBungee" >&2
  exit 1
}

SIZE=$(stat -c%s "$DEST" 2>/dev/null || stat -f%z "$DEST" 2>/dev/null)
if [ "$SIZE" -lt 100000 ]; then
  echo "[ERROR] Downloaded ViaBungee jar is only ${SIZE} bytes (expected >100KB)" >&2
  rm -f "$DEST"
  exit 1
fi

echo "[INFO] Downloaded ViaBungee version ${VIABUNGEE_VERSION} -> ${DEST}"
