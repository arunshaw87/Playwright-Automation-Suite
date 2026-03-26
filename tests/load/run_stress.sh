#!/usr/bin/env bash
# Stress load test — ramp to 200 users over 20s, hold for 10 minutes
# Usage: ./run_stress.sh [host]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="${1:-${LOCUST_HOST:-http://localhost:80}}"
REPORTS_DIR="$SCRIPT_DIR/reports/load"
mkdir -p "$REPORTS_DIR"

echo "Running STRESS load test against $HOST"
echo "  Users: 200 | Spawn rate: 10/s | Duration: 10m"

locust \
  -f "$SCRIPT_DIR/locustfile.py" \
  --headless \
  --users 200 \
  --spawn-rate 10 \
  --run-time 10m \
  --host "$HOST" \
  --html "$REPORTS_DIR/stress_report.html" \
  --csv "$REPORTS_DIR/stress" \
  --exit-code-on-error 1

echo "Stress test complete. Report: $REPORTS_DIR/stress_report.html"
