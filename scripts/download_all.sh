#!/usr/bin/env bash
set -euo pipefail

# Downloads all required JARs for the Eaglercraft bridge

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[INFO] === Downloading all Eaglercraft Bridge dependencies ==="

echo "[INFO] --- Downloading BungeeCord ---"
bash "${SCRIPT_DIR}/download_bungeecord.sh"

echo "[INFO] --- Downloading EaglerXServer ---"
bash "${SCRIPT_DIR}/download_eaglerxserver.sh"

echo "[INFO] --- Downloading ViaVersion ---"
bash "${SCRIPT_DIR}/download_viaversion.sh"

echo "[INFO] --- Downloading ViaBackwards ---"
bash "${SCRIPT_DIR}/download_viabackwards.sh"

echo "[INFO] --- Downloading ViaBungee ---"
bash "${SCRIPT_DIR}/download_viabungee.sh"

echo "[INFO] --- Downloading Paper 26.1.2 ---"
bash "${SCRIPT_DIR}/download_paper.sh"

echo "[INFO] === All downloads complete ==="
