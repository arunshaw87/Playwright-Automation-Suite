# UI Test Framework

End-to-end UI test suite for [SauceDemo](https://www.saucedemo.com/) using **Python 3.13**, **Pytest**, and **Playwright** with a Page Object Model (POM) architecture.

## Structure

```
tests/ui/
├── pages/                        # Page Object Model classes
│   ├── base_page.py              # BasePage with shared navigation helpers
│   ├── login_page.py             # LoginPage — locators + actions for login screen
│   ├── inventory_page.py         # InventoryPage — product listing, sort, cart badge
│   ├── product_page.py           # ProductPage — product detail view
│   ├── cart_page.py              # CartPage — cart contents, remove, proceed to checkout
│   └── checkout_page.py          # CheckoutStepOnePage, CheckoutStepTwoPage, CheckoutCompletePage
├── tests/                        # Test files
│   ├── test_login.py             # Login — valid, invalid, locked user, parametrized users
│   ├── test_inventory.py         # Product listing, sorting A-Z / Z-A / price, detail nav
│   ├── test_cart.py              # Add/remove items, badge count, cart page assertions
│   └── test_checkout.py          # Full E2E checkout flow, field validation, order summary
├── conftest.py                   # Browser/page fixtures, logged_in_page, screenshot-on-failure
├── pytest.ini                    # Pytest configuration and marker declarations
├── requirements-ui.txt           # Pinned Python dependencies
└── README.md                     # This file
```

## Prerequisites

- Python 3.13
- pip

## Setup

```bash
cd tests/ui

# Create and activate a virtual environment
python3.13 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements-ui.txt

# Install Playwright browsers (Chromium, Firefox, WebKit)
playwright install
```

## Running Tests

### All tests (Chromium, default)
```bash
pytest tests/ --browser chromium
```

### Smoke tests only
```bash
pytest tests/ -m smoke --browser chromium
```

### Regression suite
```bash
pytest tests/ -m regression --browser chromium
```

### Specific test file
```bash
pytest tests/test_login.py --browser chromium -v
```

### Multi-browser (Chromium + Firefox)
```bash
pytest tests/ --browser chromium --browser firefox
```

### Parallel execution (requires pytest-xdist)
```bash
pytest tests/ -n auto --browser chromium
```

### With HTML report
```bash
pytest tests/ --browser chromium \
    --html=reports/html/report.html \
    --self-contained-html
```

### With JUnit XML (for CI)
```bash
pytest tests/ --browser chromium \
    --junitxml=reports/junit/results.xml
```

### Headed mode (see the browser)
```bash
pytest tests/ --browser chromium --headed
```

## Test Marks

| Mark         | Description                                  |
|--------------|----------------------------------------------|
| `smoke`      | Critical path — run on every commit          |
| `regression` | Full regression suite — run on PRs and nightly |
| `login`      | Login-related tests                          |
| `inventory`  | Product listing and detail tests             |
| `cart`       | Shopping cart tests                          |
| `checkout`   | Checkout flow tests                          |

## Test Credentials (SauceDemo)

| Username                 | Password       | Notes                     |
|--------------------------|----------------|---------------------------|
| `standard_user`          | `secret_sauce` | Standard valid user       |
| `locked_out_user`        | `secret_sauce` | Locked out — login fails  |
| `problem_user`           | `secret_sauce` | Various UI bugs           |
| `performance_glitch_user`| `secret_sauce` | Slow performance          |
| `error_user`             | `secret_sauce` | Random errors             |

## CI Integration

Reports are written to:
- `reports/html/report.html` — Human-readable HTML report
- `reports/junit/results.xml` — JUnit XML for CI parsers (GitHub Actions, Jenkins, etc.)
- `reports/screenshots/` — Screenshots captured automatically on test failure

## Page Object Model

Each page class:
- Wraps all element locators (no raw selectors in tests)
- Exposes action methods (e.g. `login()`, `add_item_to_cart_by_name()`)
- Exposes assertion helpers using `playwright.sync_api.expect` (e.g. `expect_title()`)
- Extends `BasePage` which provides navigation and title helpers
