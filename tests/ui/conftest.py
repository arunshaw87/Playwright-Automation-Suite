import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright


BASE_URL = "https://www.saucedemo.com"
STANDARD_USER = "standard_user"
LOCKED_OUT_USER = "locked_out_user"
PROBLEM_USER = "problem_user"
PERFORMANCE_GLITCH_USER = "performance_glitch_user"
DEFAULT_PASSWORD = "secret_sauce"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: Quick smoke tests — run on every commit")
    config.addinivalue_line("markers", "regression: Full regression suite")
    config.addinivalue_line("markers", "login: Login-related tests")
    config.addinivalue_line("markers", "inventory: Inventory/product tests")
    config.addinivalue_line("markers", "cart: Shopping cart tests")
    config.addinivalue_line("markers", "checkout: Checkout flow tests")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "base_url": BASE_URL,
        "viewport": {"width": 1280, "height": 720},
        "record_video_dir": None,
    }


@pytest.fixture(scope="function")
def page(browser: Browser) -> Page:
    context = browser.new_context(
        base_url=BASE_URL,
        viewport={"width": 1280, "height": 720},
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="function")
def logged_in_page(page: Page) -> Page:
    from pages.login_page import LoginPage

    login = LoginPage(page)
    login.open()
    login.login(STANDARD_USER, DEFAULT_PASSWORD)
    page.wait_for_url("**/inventory.html")
    yield page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page: Page | None = item.funcargs.get("page") or item.funcargs.get("logged_in_page")  # type: ignore[assignment]
        if page is not None:
            screenshot_path = f"reports/screenshots/{item.nodeid.replace('/', '_').replace('::', '_')}.png"
            try:
                import os
                os.makedirs("reports/screenshots", exist_ok=True)
                page.screenshot(path=screenshot_path, full_page=True)
            except Exception:
                pass
