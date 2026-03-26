#!/usr/bin/env bash
# Soak load test — 50 users for 30 minutes (detect memory leaks / slow degradation)
# Usage: ./run_soak.sh [host]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="${1:-${LOCUST_HOST:-http://localhost:80}}"
REPORTS_DIR="$SCRIPT_DIR/reports/load"
mkdir -p "$REPORTS_DIR"

echo "Running SOAK load test against $HOST"
echo "  Users: 50 | Spawn rate: 5/s | Duration: 30m"

locust \
  -f "$SCRIPT_DIR/locustfile.py" \
  --config "$SCRIPT_DIR/locust.conf" \
  --headless \
  --users 50 \
  --spawn-rate 5 \
  --run-time 30m \
  --host "$HOST" \
  --html "$REPORTS_DIR/soak_report.html" \
  --csv "$REPORTS_DIR/soak" \
  --exit-code-on-error 1

echo "Soak test complete. Report: $REPORTS_DIR/soak_report.html"
