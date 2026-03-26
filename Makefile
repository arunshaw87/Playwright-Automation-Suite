.PHONY: help \
        install install-api install-ui install-load install-mobile \
        test-api test-ui test-load test-mobile test-all test-smoke \
        docker-build docker-test-api docker-test-ui docker-test-load \
        lint lint-api lint-ui lint-load lint-mobile \
        clean clean-reports

PYTHON     := python3.13
API_BASE_URL  ?= http://localhost:80
UI_BASE_URL   ?= https://www.saucedemo.com
BROWSER       ?= chromium
LOCUST_HOST   ?= $(API_BASE_URL)

# ------------------------------------------------------------------
# Default target — print help
# ------------------------------------------------------------------

help:
	@echo "E2E Test Framework — available targets:"
	@echo ""
	@echo "  Setup"
	@echo "    install           Install all test suite dependencies"
	@echo "    install-api       Install API test dependencies only"
	@echo "    install-ui        Install UI test dependencies only"
	@echo "    install-load      Install Locust load test dependencies only"
	@echo "    install-mobile    Install mobile test dependencies only"
	@echo ""
	@echo "  Run tests"
	@echo "    test-smoke        API health smoke (always works)"
	@echo "    test-api          Full API test suite"
	@echo "    test-ui           UI tests via Playwright (default: chromium)"
	@echo "    test-load         Locust smoke profile (headless, 1 min)"
	@echo "    test-mobile       Mobile tests (requires Appium server)"
	@echo "    test-all          API + UI + load tests"
	@echo ""
	@echo "  Docker"
	@echo "    docker-build      Build all test Docker images"
	@echo "    docker-test-api   Run API tests in Docker"
	@echo "    docker-test-ui    Run UI tests in Docker"
	@echo "    docker-test-load  Run load tests (smoke) in Docker"
	@echo ""
	@echo "  Quality"
	@echo "    lint              Lint all Python test suites (py_compile)"
	@echo "    lint-api          Lint API test suite"
	@echo "    lint-ui           Lint UI test suite"
	@echo "    lint-load         Lint load test suite"
	@echo "    lint-mobile       Lint mobile test suite"
	@echo ""
	@echo "  Cleanup"
	@echo "    clean-reports     Remove all generated reports"
	@echo "    clean             Remove reports + Python cache files"
	@echo ""
	@echo "  Variables (override on the CLI, e.g. make test-ui BROWSER=firefox)"
	@echo "    API_BASE_URL      $(API_BASE_URL)"
	@echo "    UI_BASE_URL       $(UI_BASE_URL)"
	@echo "    BROWSER           $(BROWSER)"
	@echo "    LOCUST_HOST       $(LOCUST_HOST)"

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

# Smoke — always runs (API health endpoint only)
test-smoke:
	cd tests/api && API_BASE_URL=$(API_BASE_URL) \
	$(PYTHON) -m pytest tests/test_health.py -v -m smoke --tb=short

# Full API suite (non-health tests skip gracefully on 404)
test-api:
	cd tests/api && API_BASE_URL=$(API_BASE_URL) \
	$(PYTHON) -m pytest tests/ -v --tb=short

# UI tests (Playwright, targets saucedemo.com by default)
test-ui:
	cd tests/ui && BASE_URL=$(UI_BASE_URL) \
	$(PYTHON) -m pytest tests/ --browser=$(BROWSER) -v --tb=short

# Load test — smoke profile (1 min, 5 users, headless)
test-load:
	cd tests/load && ./run_smoke.sh $(LOCUST_HOST)

# Mobile tests — skips automatically if Appium server is unreachable
test-mobile:
	cd tests/mobile && $(PYTHON) -m pytest tests/ -v --tb=short

# Run API + UI + load together
test-all: test-api test-ui test-load

# ------------------------------------------------------------------
# Docker
# ------------------------------------------------------------------

docker-build:
	docker build -t e2e-api-tests    -f Dockerfile.api    .
	docker build -t e2e-ui-tests     -f Dockerfile.ui     .
	docker build -t e2e-load-tests   -f Dockerfile.load   .
	docker build -t e2e-mobile-tests -f Dockerfile.mobile .

docker-test-api:
	docker compose run --rm api-tests

docker-test-ui:
	docker compose run --rm ui-tests

docker-test-load:
	docker compose run --rm load-tests

# ------------------------------------------------------------------
# Lint (syntax check via py_compile — no extra install needed)
# ------------------------------------------------------------------

lint: lint-api lint-ui lint-load lint-mobile

lint-api:
	$(PYTHON) -m py_compile \
	tests/api/conftest.py \
	tests/api/models/responses.py \
	tests/api/utils/validators.py \
	tests/api/utils/data_factory.py \
	tests/api/utils/retry.py \
	tests/api/tests/test_health.py \
	tests/api/tests/test_auth.py \
	tests/api/tests/test_users.py \
	tests/api/tests/test_products.py
	@echo "API lint: OK"

lint-ui:
	$(PYTHON) -m py_compile \
	tests/ui/conftest.py \
	tests/ui/pages/base_page.py \
	tests/ui/pages/login_page.py \
	tests/ui/pages/inventory_page.py \
	tests/ui/pages/cart_page.py \
	tests/ui/tests/test_login.py \
	tests/ui/tests/test_inventory.py \
	tests/ui/tests/test_cart.py \
	tests/ui/tests/test_checkout.py
	@echo "UI lint: OK"

lint-load:
	$(PYTHON) -m py_compile \
	tests/load/locustfile.py \
	tests/load/config/load_profiles.py \
	tests/load/utils/auth_helper.py
	@echo "Load lint: OK"

lint-mobile:
	$(PYTHON) -m py_compile \
	tests/mobile/conftest.py \
	tests/mobile/pages/base_page.py \
	tests/mobile/pages/login_page.py \
	tests/mobile/pages/home_page.py \
	tests/mobile/pages/product_list_page.py \
	tests/mobile/pages/product_detail_page.py \
	tests/mobile/utils/driver_factory.py \
	tests/mobile/utils/wait_helpers.py \
	tests/mobile/tests/test_login.py \
	tests/mobile/tests/test_navigation.py \
	tests/mobile/tests/test_product_browse.py
	@echo "Mobile lint: OK"

# ------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------

clean-reports:
	rm -rf tests/api/reports tests/ui/reports tests/mobile/reports tests/load/reports

clean: clean-reports
	find tests/ -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find tests/ -name "*.pyc" -delete 2>/dev/null || true
	find tests/ -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
