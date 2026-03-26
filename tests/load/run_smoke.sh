#!/usr/bin/env bash
# Smoke load test — 5 users, 1 minute, headless
# Usage: ./run_smoke.sh [host]
set -euo pipefail

HOST="${1:-${LOCUST_HOST:-http://localhost:80}}"
REPORTS_DIR="reports/load"
mkdir -p "$REPORTS_DIR"

echo "Running SMOKE load test against $HOST"
echo "  Users: 5 | Spawn rate: 1/s | Duration: 1m"

locust \
  -f locustfile.py \
  --headless \
  --users 5 \
  --spawn-rate 1 \
  --run-time 1m \
  --host "$HOST" \
  --html "$REPORTS_DIR/smoke_report.html" \
  --csv "$REPORTS_DIR/smoke" \
  --exit-code-on-error 1

echo "Smoke test complete. Report: $REPORTS_DIR/smoke_report.html"
