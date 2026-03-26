import logging
import os
import pytest
from playwright.sync_api import Browser, Page


logger = logging.getLogger(__name__)

BASE_URL = "https://www.saucedemo.com"
STANDARD_USER = "standard_user"
LOCKED_OUT_USER = "locked_out_user"
PROBLEM_USER = "problem_user"
PERFORMANCE_GLITCH_USER = "performance_glitch_user"
DEFAULT_PASSWORD = "secret_sauce"


def pytest_configure(config: pytest.Config) -> None:
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
    """
    Un-authenticated, function-scoped page in a fresh browser context.
    Used for login tests that start from the login screen.
    """
    context = browser.new_context(
        base_url=BASE_URL,
        viewport={"width": 1280, "height": 720},
    )
    pg = context.new_page()
    yield pg
    context.close()


@pytest.fixture(scope="session")
def auth_storage_state(browser: Browser, tmp_path_factory: pytest.TempPathFactory) -> str:
    """
    Session-scoped fixture that logs in once, saves the browser storage state
    (cookies + localStorage) to a temporary file, and returns the path.

    Each test that needs authentication creates a *fresh* browser context from
    this state snapshot, so:
    - Login cost is paid only once per session (fast).
    - Every test starts with an identical, isolated context (no state bleed).
    """
    state_path = str(tmp_path_factory.mktemp("auth") / "storage_state.json")
    context = browser.new_context(
        base_url=BASE_URL,
        viewport={"width": 1280, "height": 720},
    )
    pg = context.new_page()
    from pages.login_page import LoginPage

    login = LoginPage(pg)
    login.open()
    login.login(STANDARD_USER, DEFAULT_PASSWORD)
    pg.wait_for_url("**/inventory.html")
    context.storage_state(path=state_path)
    context.close()
    return state_path


@pytest.fixture(scope="function")
def logged_in_page(browser: Browser, auth_storage_state: str) -> Page:
    """
    Function-scoped authenticated page.
    Creates a *fresh* browser context from the saved storage state so every
    test starts with a clean cart and DOM — no state bleed between tests.
    """
    context = browser.new_context(
        base_url=BASE_URL,
        viewport={"width": 1280, "height": 720},
        storage_state=auth_storage_state,
    )
    pg = context.new_page()
    pg.goto(f"{BASE_URL}/inventory.html")
    yield pg
    context.close()


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
