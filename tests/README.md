# E2E Test Framework

Comprehensive end-to-end automation framework for Python 3.13 covering four test
disciplines: UI, API, Mobile, and Load testing.

## Suites

| Suite  | Tool                          | Target                        | Directory        |
|--------|-------------------------------|-------------------------------|------------------|
| UI     | Pytest + Playwright + POM     | https://www.saucedemo.com     | `tests/ui/`      |
| API    | Pytest + HTTPX + Pydantic v2  | REST API (configurable)       | `tests/api/`     |
| Mobile | Pytest + Appium 2.x + POM     | Native Android / iOS app      | `tests/mobile/`  |
| Load   | Locust                        | REST API (configurable)       | `tests/load/`    |

## Quick Start

### Prerequisites
- Python 3.13
- Node.js 24 + pnpm (for starting the API server locally)

### Install all dependencies
```bash
make install
```

### Run smoke tests (API health — always available)
```bash
make test-smoke
```

### Run full API test suite
```bash
make test-api API_BASE_URL=http://localhost:80
```

### Run UI tests
```bash
make test-ui BROWSER=chromium
```

### Run load test smoke profile
```bash
make test-load API_BASE_URL=http://localhost:80
```

### Run all suites
```bash
make test-all
```

## CI/CD

GitHub Actions workflow at `.github/workflows/ci.yml`:
- **API tests** — run on every push/PR
- **UI tests** — matrix: Chromium + Firefox, run on every push/PR
- **Load smoke** — runs after API tests pass (1 min, 5 users)
- **Mobile tests** — opt-in via `ENABLE_MOBILE_TESTS` repository variable

## Docker

```bash
# Build all test images
make docker-build

# Run API tests in Docker
make docker-test-api

# Full orchestration (API server + api-tests)
docker compose run api-tests

# Load test smoke
docker compose run load-tests
```

## Configuration

Copy `.env.example` to `.env` and fill in your values. Key variables:

| Variable            | Default                     | Used by    |
|---------------------|-----------------------------|------------|
| `API_BASE_URL`      | `http://localhost:80`       | API, Load  |
| `BASE_URL`          | `https://www.saucedemo.com` | UI         |
| `BROWSER`           | `chromium`                  | UI         |
| `APPIUM_SERVER_URL` | `http://localhost:4723`     | Mobile     |
| `LOCUST_HOST`       | `http://localhost:80`       | Load       |

See individual suite READMEs for full configuration options:
- [`tests/api/README.md`](api/README.md)
- [`tests/ui/README.md`](ui/README.md)
- [`tests/mobile/README.md`](mobile/README.md)
- [`tests/load/README.md`](load/README.md)

## Reports

All reports are written to `reports/` subdirectories within each suite:
- `tests/api/reports/junit/` — JUnit XML
- `tests/ui/reports/html/` — HTML report, `reports/junit/` — JUnit XML, `reports/screenshots/` — failure screenshots
- `tests/mobile/reports/junit/`, `reports/screenshots/`
- `tests/load/reports/load/` — Locust HTML + CSV
