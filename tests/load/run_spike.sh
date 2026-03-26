#!/usr/bin/env bash
# Spike load test — burst to 500 users at 100/s, hold for 5 minutes
# Usage: ./run_spike.sh [host]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="${1:-${LOCUST_HOST:-http://localhost:80}}"
REPORTS_DIR="$SCRIPT_DIR/reports/load"
mkdir -p "$REPORTS_DIR"

echo "Running SPIKE load test against $HOST"
echo "  Users: 500 | Spawn rate: 100/s | Duration: 5m"

locust \
  -f "$SCRIPT_DIR/locustfile.py" \
  --config "$SCRIPT_DIR/locust.conf" \
  --headless \
  --users 500 \
  --spawn-rate 100 \
  --run-time 5m \
  --host "$HOST" \
  --html "$REPORTS_DIR/spike_report.html" \
  --csv "$REPORTS_DIR/spike" \
  --exit-code-on-error 1

echo "Spike test complete. Report: $REPORTS_DIR/spike_report.html"
