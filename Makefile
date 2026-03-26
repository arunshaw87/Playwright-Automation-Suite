.PHONY: help install install-api install-ui install-load install-mobile \
        test test-api test-ui test-load test-mobile test-all \
        docker-build docker-test-api docker-test-ui docker-test-load \
        lint lint-api lint-ui lint-load clean clean-reports

PYTHON := python3.13
API_BASE_URL ?= http://localhost:80
UI_BASE_URL ?= https://www.saucedemo.com
BROWSER ?= chromium

# ------------------------------------------------------------------
# Default target
# ------------------------------------------------------------------

help:
	@echo "E2E Test Framework — available targets:"
	@echo ""
	@echo "  Setup"
	@echo "    install         Install all test suite dependencies"
	@echo "    install-api     Install API test dependencies only"
	@echo "    install-ui      Install UI test dependencies only"
	@echo "    install-load    Install Locust load test dependencies only"
	@echo "    install-mobile  Install mobile test dependencies only"
	@echo ""
	@echo "  Run tests"
	@echo "    test-api        Run API test suite"
	@echo "    test-ui         Run UI test suite (Playwright, default: chromium)"
	@echo "    test-load       Run Locust smoke profile (headless)"
	@echo "    test-mobile     Run mobile tests (requires Appium server)"
	@echo "    test-all        Run API + UI + load tests"
	@echo ""
	@echo "  Docker"
	@echo "    docker-build    Build all test Docker images"
	@echo "    docker-test-api Run API tests in Docker"
	@echo "    docker-test-ui  Run UI tests in Docker"
	@echo "    docker-test-load Run load tests (smoke) in Docker"
	@echo ""
	@echo "  Quality"
	@echo "    lint            Lint all Python test code"
	@echo ""
	@echo "  Cleanup"
	@echo "    clean-reports   Remove all generated reports"
	@echo "    clean           Remove reports + Python cache files"
	@echo ""
	@echo "  Variables"
	@echo "    API_BASE_URL    $(API_BASE_URL)"
	@echo "    UI_BASE_URL     $(UI_BASE_URL)"
	@echo "    BROWSER         $(BROWSER)"

# ------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------

install: install-api install-ui install-load install-mobile

install-api:
	$(PYTHON) -m pip install -r tests/api/requirements-api.txt

install-ui:
	$(PYTHON) -m pip install -r tests/ui/requirements-ui.txt
	$(PYTHON) -m playwright install --with-deps $(BROWSER)

install-load:
	$(PYTHON) -m pip install -r tests/load/requirements-load.txt

install-mobile:
	$(PYTHON) -m pip install -r tests/mobile/requirements-mobile.txt

# ------------------------------------------------------------------
# Run tests
# ------------------------------------------------------------------

test-api:
	cd tests/api && API_BASE_URL=$(API_BASE_URL) $(PYTHON) -m pytest tests/ -v --tb=short

test-ui:
	cd tests/ui && BASE_URL=$(UI_BASE_URL) $(PYTHON) -m pytest tests/ --browser=$(BROWSER) -v --tb=short

test-load:
	cd tests/load && LOCUST_HOST=$(API_BASE_URL) ./run_smoke.sh $(API_BASE_URL)

test-mobile:
	cd tests/mobile && $(PYTHON) -m pytest tests/ -v --tb=short

test-all: test-api test-ui test-load

# Smoke only (health tests — works without a full API)
test-smoke:
	cd tests/api && API_BASE_URL=$(API_BASE_URL) $(PYTHON) -m pytest tests/test_health.py -v -m smoke

# ------------------------------------------------------------------
# Docker
# ------------------------------------------------------------------

docker-build:
	docker build -t e2e-api-tests -f Dockerfile.api .
	docker build -t e2e-ui-tests -f Dockerfile.ui .
	docker build -t e2e-load-tests -f Dockerfile.load .

docker-test-api:
	docker compose run --rm api-tests

docker-test-ui:
	docker compose run --rm ui-tests

docker-test-load:
	docker compose run --rm load-tests

# ------------------------------------------------------------------
# Lint
# ------------------------------------------------------------------

lint: lint-api lint-ui lint-load

lint-api:
	$(PYTHON) -m py_compile tests/api/conftest.py tests/api/models/responses.py \
		tests/api/utils/validators.py tests/api/utils/data_factory.py \
		tests/api/utils/retry.py \
		tests/api/tests/test_health.py tests/api/tests/test_auth.py \
		tests/api/tests/test_users.py tests/api/tests/test_products.py
	@echo "API lint: OK"

lint-ui:
	@echo "UI lint: run 'python -m py_compile' on tests/ui/**/*.py"

lint-load:
	$(PYTHON) -m py_compile tests/load/locustfile.py \
		tests/load/config/load_profiles.py \
		tests/load/utils/auth_helper.py
	@echo "Load lint: OK"

# ------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------

clean-reports:
	rm -rf tests/api/reports tests/ui/reports tests/mobile/reports tests/load/reports

clean: clean-reports
	find tests/ -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find tests/ -name "*.pyc" -delete 2>/dev/null || true
	find tests/ -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
