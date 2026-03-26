# E2E Test Framework

Comprehensive end-to-end automation framework built with **Python 3.13**, living
alongside a TypeScript/Node.js API server monorepo. Covers four test disciplines:
UI, API, Mobile, and Load.

## Suites

| Suite  | Tool                         | Target                        | Directory       |
|--------|------------------------------|-------------------------------|-----------------|
| UI     | Pytest + Playwright + POM    | https://www.saucedemo.com     | `tests/ui/`     |
| API    | Pytest + HTTPX + Pydantic v2 | REST API (configurable)       | `tests/api/`    |
| Mobile | Pytest + Appium 2.x + POM    | Native Android / iOS app      | `tests/mobile/` |
| Load   | Locust                       | REST API (configurable)       | `tests/load/`   |

## Prerequisites

- Python 3.13
- Node.js 24 + pnpm (for running the API server locally)
- Docker + Docker Compose (for containerised runs)

## Quick Start

### 1. Install all test dependencies

```bash
make install
```

### 2. Start the API server (for API and load tests)

```bash
pnpm install --frozen-lockfile
pnpm --filter @workspace/api-server run dev
```

### 3. Run each suite

```bash
# API health smoke — always works
make test-smoke

# Full API suite (endpoints not yet live are skipped gracefully)
make test-api API_BASE_URL=http://localhost:80

# UI tests — targets https://www.saucedemo.com
make test-ui BROWSER=chromium

# Load test — smoke profile (1 min, 5 users, headless)
make test-load API_BASE_URL=http://localhost:80

# Mobile tests — skips automatically if Appium server is unreachable
make test-mobile

# Run API + UI + load together
make test-all
```

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable             | Default                     | Used by        |
|----------------------|-----------------------------|----------------|
| `API_BASE_URL`       | `http://localhost:80`       | API, Load      |
| `BASE_URL`           | `https://www.saucedemo.com` | UI             |
| `BROWSER`            | `chromium`                  | UI             |
| `APPIUM_SERVER_URL`  | `http://localhost:4723`     | Mobile         |
| `LOCUST_HOST`        | `http://localhost:80`       | Load           |
| `API_USERNAME`       | `admin`                     | API, Load      |
| `API_PASSWORD`       | `password`                  | API, Load      |

See individual suite READMEs for full configuration:
- [`tests/api/README.md`](tests/api/README.md)
- [`tests/ui/README.md`](tests/ui/README.md)
- [`tests/mobile/README.md`](tests/mobile/README.md)
- [`tests/load/README.md`](tests/load/README.md)

## Docker

```bash
# Build all test images
make docker-build

# Run API tests in Docker (spins up api-server automatically)
make docker-test-api

# Run UI tests in Docker
make docker-test-ui

# Run load tests in Docker (smoke profile)
make docker-test-load

# Full orchestration via Docker Compose
docker compose run --rm api-tests
docker compose run --rm ui-tests
docker compose run --rm load-tests
```

### Mobile Docker (requires Appium + emulator)

```bash
docker compose -f docker-compose.mobile.yml up appium-server
docker compose -f docker-compose.mobile.yml run --rm mobile-tests
```

## CI/CD

GitHub Actions workflow at `.github/workflows/ci.yml`:

| Job                  | Trigger              | Notes                                          |
|----------------------|----------------------|------------------------------------------------|
| `api-tests`          | push / PR to main    | Starts API server, runs full suite             |
| `ui-tests`           | push / PR to main    | Matrix: Chromium + Firefox                     |
| `load-tests-smoke`   | after `api-tests`    | 1 min, 5 users, headless Locust smoke run      |
| `mobile-tests`       | opt-in               | Requires `ENABLE_MOBILE_TESTS=true` repo var   |

All jobs upload JUnit XML + HTML reports as GitHub Actions artifacts.

## Reports

Reports are written inside each suite after running:

| Suite  | Report location                          |
|--------|------------------------------------------|
| API    | `tests/api/reports/junit/`, `html/`      |
| UI     | `tests/ui/reports/junit/`, `html/`, `screenshots/` |
| Mobile | `tests/mobile/reports/junit/`, `screenshots/` |
| Load   | `tests/load/reports/load/` (HTML + CSV)  |

```bash
# Remove all generated reports
make clean-reports

# Remove reports + Python caches
make clean
```

## Linting

```bash
# Syntax-check all Python test files across all suites
make lint
```

## Project Structure

```
.
├── artifacts/
│   └── api-server/         # Express 5 API server (TypeScript)
├── tests/
│   ├── ui/                 # Playwright + POM tests
│   ├── api/                # HTTPX + Pydantic v2 tests
│   ├── mobile/             # Appium 2.x + POM tests
│   ├── load/               # Locust load tests
│   └── README.md           # Suite-level quick reference
├── Dockerfile.api          # API test image
├── Dockerfile.ui           # UI test image (includes Playwright browsers)
├── Dockerfile.load         # Locust load test image
├── Dockerfile.mobile       # Mobile test image
├── docker-compose.yml      # Orchestrates api-server + test containers
├── docker-compose.mobile.yml # Appium server + emulator + mobile tests
├── .github/workflows/ci.yml  # GitHub Actions CI pipeline
├── Makefile                # Developer-friendly make targets
└── .env.example            # All required environment variables documented
```
