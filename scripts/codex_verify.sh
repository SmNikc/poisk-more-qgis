#!/usr/bin/env bash
set -euo pipefail

echo "[Check] QGIS import"
python3 - <<'PY'
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
try:
    from qgis.core import QgsApplication
    print("QGIS import OK")
except Exception as e:
    print("QGIS import FAILED:", e)
    sys.exit(1)
PY

echo "[Check] ActiveMQ http console"
if command -v curl >/dev/null 2>&1; then
  if curl -fsS http://localhost:8161 >/dev/null 2>&1; then
    print_msg = "ActiveMQ is up (http://localhost:8161)"
    echo "$print_msg"
  else
    echo "ActiveMQ http console not responding (8161)"
  fi
else
  echo "curl not installed; skipping http check"
fi

echo "[Check] ActiveMQ TCP port 61616"
python3 - <<'PY'
import socket, sys
s = socket.socket()
try:
    s.settimeout(2.0)
    s.connect(("localhost", 61616))
    print("ActiveMQ TCP 61616 is open")
except Exception as e:
    print("ActiveMQ TCP 61616 check failed:", e)
    sys.exit(1)
finally:
    s.close()
PY

echo "All checks passed"