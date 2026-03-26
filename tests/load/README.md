# Load Test Framework

Load testing suite using **Python 3.13** and **Locust**. Models realistic traffic
across four user behaviour classes with configurable load profiles (smoke, soak, stress, spike).

## Structure

```
tests/load/
├── locustfile.py             # Main Locust entry point with all HttpUser classes
├── locust.conf               # Default Locust settings (override via CLI flags)
├── config/
│   └── load_profiles.py     # LoadProfile dataclasses: smoke, soak, stress, spike
├── utils/
│   └── auth_helper.py       # Token acquisition + Authorization header injection
├── run_smoke.sh              # Headless smoke run  (5 users, 1 min)
├── run_stress.sh             # Headless stress run (200 users, 10 min)
├── run_soak.sh               # Headless soak run   (50 users, 30 min)
├── run_spike.sh              # Headless spike run  (500 users, 5 min)
├── requirements-load.txt     # Pinned dependencies
└── README.md                 # This file
```

## User Classes

| Class           | Weight | Wait time    | Behaviour                                          |
|-----------------|--------|--------------|----------------------------------------------------|
| `APIHealthUser` | 10%    | 0.5s (const) | Hammers `GET /api/healthz` at constant throughput  |
| `BrowseUser`    | 70%    | 1–3s         | Browses products & users (read-heavy)              |
| `CheckoutUser`  | 20%    | 2–5s         | Full CRUD cycle: create → read → delete            |
| `AuthUser`      | 10%    | 3–8s         | Exercises login endpoint (valid + invalid)         |

## Setup

```bash
cd tests/load

python3.13 -m venv .venv
source .venv/bin/activate

pip install -r requirements-load.txt
```

## Running Tests

### UI mode (local development — interactive web UI at http://localhost:8089)
```bash
LOCUST_HOST=http://localhost:80 locust -f locustfile.py
```

### Smoke test (headless — 5 users, 1 min)
```bash
./run_smoke.sh http://localhost:80
```

### Stress test (headless — 200 users, 10 min)
```bash
./run_stress.sh http://localhost:80
```

### Soak test (headless — 50 users, 30 min)
```bash
./run_soak.sh http://localhost:80
```

### Spike test (headless — 500 users at 100/s, 5 min)
```bash
./run_spike.sh http://localhost:80
```

### Direct Locust CLI
```bash
locust -f locustfile.py \
  --headless \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --host http://localhost:80 \
  --html reports/load/report.html \
  --csv reports/load/results
```

## Reports

Reports are written to `reports/load/` (relative to `tests/load/`):
- `*_report.html` — Locust HTML report (RPS graph, response time distribution, error table)
- `*_stats.csv` — per-request stats (requests, failures, median/average/P50/P95/P99 latency)
- `*_history.csv` — time-series stats (useful for detecting degradation over soak runs)
- `*_failures.csv` — failure details (error messages, method, endpoint)
- `*_exceptions.csv` — Python exception tracebacks from tasks

## Load Profiles

| Profile | Users | Spawn rate | Duration | Purpose                           |
|---------|-------|------------|----------|-----------------------------------|
| smoke   | 5     | 1/s        | 1 min    | Quick sanity check / CI gate      |
| soak    | 50    | 5/s        | 30 min   | Detect memory leaks / degradation |
| stress  | 200   | 10/s       | 10 min   | Find breaking point               |
| spike   | 500   | 100/s      | 5 min    | Simulate sudden traffic burst     |

Load profiles can be used programmatically:

```python
from config.load_profiles import get_profile

profile = get_profile("stress")
print(profile.users, profile.spawn_rate, profile.run_time)
```

## Key Metrics

| Metric       | Description                              | Smoke target  |
|--------------|------------------------------------------|---------------|
| RPS          | Requests per second sustained            | > 50          |
| P50 latency  | Median response time                     | < 200 ms      |
| P90 latency  | 90th percentile response time            | < 500 ms      |
| P99 latency  | 99th percentile response time            | < 2000 ms     |
| Failure rate | % of requests that failed                | < 1%          |

## Environment Variables

| Variable        | Default               | Description                     |
|-----------------|-----------------------|---------------------------------|
| `LOCUST_HOST`   | `http://localhost:80` | Target API host                 |
| `API_AUTH_PATH` | `/api/auth/login`     | Auth login endpoint path        |
| `API_USERNAME`  | `admin`               | Login username                  |
| `API_PASSWORD`  | `password`            | Login password                  |

## Distributed Locust (optional extension)

For high-volume tests, run master/worker mode:
```bash
# Master
locust -f locustfile.py --master --host http://api:80

# Each worker (separate machine or container)
locust -f locustfile.py --worker --master-host <master-ip>
```

Grafana + InfluxDB integration: use the `--csv` flag and forward metrics to a
time-series DB via a metrics exporter (out of scope for this framework).
