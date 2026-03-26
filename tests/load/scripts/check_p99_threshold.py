"""
CI P99 Latency Threshold Checker
---------------------------------
Parses the Locust `_stats.csv` file produced by --csv and exits non-zero
if any endpoint's P99 response time exceeds the configured threshold.

Usage:
    python check_p99_threshold.py <path/to/smoke_stats.csv> [--threshold-ms 2000]

Exit codes:
    0  All P99 latencies are within threshold
    1  One or more P99 latencies exceed threshold (CI failure)
    2  CSV file not found or malformed
"""

import argparse
import csv
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enforce P99 latency SLA on Locust CSV output")
    parser.add_argument("csv_file", help="Path to Locust *_stats.csv file")
    parser.add_argument(
        "--threshold-ms",
        type=int,
        default=2000,
        help="Maximum allowed P99 response time in milliseconds (default: 2000)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv_file)

    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        return 2

    violations: list[tuple[str, float]] = []
    total_rows = 0

    try:
        with csv_path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                name: str = row.get("Name", "unknown")
                # Skip the aggregated totals row
                if name.strip().lower() == "aggregated":
                    continue
                total_rows += 1

                raw_p99 = row.get("99%", row.get("99th percentile", "")).strip()
                if not raw_p99 or raw_p99 == "N/A":
                    continue

                try:
                    p99_ms = float(raw_p99)
                except ValueError:
                    print(f"WARNING: Non-numeric P99 value '{raw_p99}' for '{name}', skipping", file=sys.stderr)
                    continue

                if p99_ms > args.threshold_ms:
                    violations.append((name, p99_ms))
    except (OSError, csv.Error) as exc:
        print(f"ERROR: Failed to read CSV: {exc}", file=sys.stderr)
        return 2

    if total_rows == 0:
        print("ERROR: No request rows found in CSV — load test may not have run or produced no traffic", file=sys.stderr)
        return 1

    if violations:
        print(f"\n{'='*60}")
        print(f"P99 LATENCY THRESHOLD EXCEEDED (limit: {args.threshold_ms} ms)")
        print(f"{'='*60}")
        for name, p99 in violations:
            print(f"  FAIL  {p99:>8.0f} ms  |  {name}")
        print(f"{'='*60}")
        print(f"Total violations: {len(violations)}")
        return 1

    print(f"P99 latency check PASSED (threshold: {args.threshold_ms} ms, rows checked: {total_rows})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
