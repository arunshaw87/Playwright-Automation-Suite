import logging
import os
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

logger = logging.getLogger(__name__)

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
    for directory in (
        "reports/html",
        "reports/junit",
        "reports/screenshots",
    ):
        os.makedirs(directory, exist_ok=True)


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


@pytest.fixture(scope="session")
def logged_in_browser_context(browser: Browser):
    """
    Session-scoped browser context for all tests that need an authenticated session.
    Each test calling `logged_in_page` gets a fresh page within this authenticated
    context, so the session cookie is reused but tab state is isolated.
    """
    context = browser.new_context(
        base_url=BASE_URL,
        viewport={"width": 1280, "height": 720},
    )
    page = context.new_page()
    from pages.login_page import LoginPage

    login = LoginPage(page)
    login.open()
    login.login(STANDARD_USER, DEFAULT_PASSWORD)
    page.wait_for_url("**/inventory.html")
    page.close()
    yield context
    context.close()


@pytest.fixture(scope="function")
def logged_in_page(logged_in_browser_context: BrowserContext) -> Page:
    """
    Function-scoped page within the session-scoped authenticated context.
    Each test gets a fresh tab so DOM/cart state cannot bleed between tests,
    while re-using the session-level authentication cookie.
    """
    page = logged_in_browser_context.new_page()
    page.goto(f"{BASE_URL}/inventory.html")
    yield page
    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page: Page | None = item.funcargs.get("page") or item.funcargs.get("logged_in_page")  # type: ignore[assignment]
        if page is not None:
            safe_node = item.nodeid.replace("/", "_").replace("::", "_")
            screenshot_path = f"reports/screenshots/{safe_node}.png"
            try:
                page.screenshot(path=screenshot_path, full_page=True)
                logger.info("Failure screenshot saved: %s", screenshot_path)
            except Exception as exc:
                logger.warning(
                    "Could not capture failure screenshot for %s: %s",
                    item.nodeid,
                    exc,
                )
