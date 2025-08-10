#!/usr/bin/env bash
set -euo pipefail

echo "[Patch] Switch to qgis-archive-keyring.gpg"
sudo mkdir -p /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/qgis-archive-keyring.gpg https://download.qgis.org/downloads/qgis-archive-keyring.gpg

# Create sources entry in new-style .sources file (Ubuntu 24.04+ friendly)
. /etc/os-release
cat <<SRC | sudo tee /etc/apt/sources.list.d/qgis.sources >/dev/null
Types: deb
URIs: https://qgis.org/ubuntu-ltr
Suites: ${UBUNTU_CODENAME}
Components: main
Signed-By: /etc/apt/keyrings/qgis-archive-keyring.gpg
SRC

sudo rm -f /etc/apt/sources.list.d/qgis-ltr.list || true
sudo apt-get update -y
echo "[Patch] Done. You can re-run installation now."