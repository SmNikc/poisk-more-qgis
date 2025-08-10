#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

echo "[1/6] Update apt & base tools"
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends ca-certificates gnupg curl wget unzip xz-utils lsb-release software-properties-common procps

echo "[2/6] Install QGIS LTR on Ubuntu 24.04 (noble)"
UBU_CODENAME=$(. /etc/os-release && echo "${UBUNTU_CODENAME}")
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.qgis.org/downloads/qgis-archive-keyring.gpg -o /tmp/qgis-archive-keyring.gpg
sudo mv /tmp/qgis-archive-keyring.gpg /etc/apt/keyrings/qgis-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/qgis-archive-keyring.gpg] https://qgis.org/ubuntu-ltr ${UBU_CODENAME} main" | sudo tee /etc/apt/sources.list.d/qgis-ltr.list
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends   qgis qgis-python qgis-plugin-grass   python3-qgis python3-pip python3-pyqt5   gdal-bin python3-gdal xvfb

echo "[3/6] Python deps for plugin tests"
python3 -m pip install --upgrade pip
python3 -m pip install pytest pytest-xdist requests paho-mqtt

echo "[4/6] Headless GUI (Xvfb)"
if ! pgrep -f "Xvfb :99" >/dev/null 2>&1; then
  nohup Xvfb :99 -screen 0 1920x1080x24 >/tmp/xvfb.log 2>&1 &
  sleep 1
fi
export DISPLAY=:99
export QT_QPA_PLATFORM=offscreen

echo "[5/6] ActiveMQ setup"
WORK=/workspace
if [ -d "${WORK}/poisk-more-qgis/docker/activemq" ]; then
  echo "Found docker/activemq directory — trying local run"
  if [ -x "${WORK}/poisk-more-qgis/docker/activemq/bin/activemq" ]; then
    nohup "${WORK}/poisk-more-qgis/docker/activemq/bin/activemq" console >/tmp/activemq.log 2>&1 &
  else
    AMQ_VER=5.16.6
    cd /tmp
    curl -fsSL "https://downloads.apache.org/activemq/${AMQ_VER}/apache-activemq-${AMQ_VER}-bin.tar.gz" -o amq.tgz
    sudo tar -C /opt -xzf amq.tgz
    nohup /opt/apache-activemq-${AMQ_VER}/bin/activemq console >/tmp/activemq.log 2>&1 &
  fi
else
  AMQ_VER=5.16.6
  cd /tmp
  curl -fsSL "https://downloads.apache.org/activemq/${AMQ_VER}/apache-activemq-${AMQ_VER}-bin.tar.gz" -o amq.tgz
  sudo tar -C /opt -xzf amq.tgz
  nohup /opt/apache-activemq-${AMQ_VER}/bin/activemq console >/tmp/activemq.log 2>&1 &
fi

echo "[6/6] Quick smoke checks"
python3 - <<'PY'
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
try:
    from qgis.core import QgsApplication
    print("QGIS imported OK")
except Exception as e:
    print("QGIS import FAILED:", e)
    sys.exit(1)
print("All good.")
PY

echo "Setup complete."
