#!/usr/bin/env bash
set -euo pipefail
timeout="${1:-60}"
echo "Waiting up to ${timeout}s for ActiveMQ 61616..."
for i in $(seq 1 "$timeout"); do
  if (echo > /dev/tcp/localhost/61616) >/dev/null 2>&1; then
    echo "ActiveMQ is ready"
    exit 0
  fi
  sleep 1
done
echo "Timed out waiting for ActiveMQ"
exit 1