"""
Mobile test framework conftest.

Fixtures
--------
android_driver   : function — Appium WebDriver for Android (skips if unavailable)
ios_driver       : function — Appium WebDriver for iOS (skips if unavailable)
driver           : function — Resolves to Android or iOS driver based on MOBILE_PLATFORM
"""
from __future__ import annotations

import logging
import os

import pytest

logger = logging.getLogger(__name__)

MOBILE_PLATFORM = os.environ.get("MOBILE_PLATFORM", "android").lower()
APPIUM_SERVER_URL = os.environ.get("APPIUM_SERVER_URL", "http://localhost:4723")


def pytest_configure(config: pytest.Config) -> None:
    for directory in ("reports/html", "reports/junit", "reports/screenshots"):
        os.makedirs(directory, exist_ok=True)


def _appium_available() -> bool:
    """Return True if the Appium server is reachable."""
    import httpx
    try:
        r = httpx.get(f"{APPIUM_SERVER_URL}/status", timeout=3.0)
        return r.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="function")
def android_driver():
    """
    Function-scoped Appium WebDriver fixture for Android.

    Skips automatically when:
    - Appium Python client is not installed
    - Appium server is not reachable at APPIUM_SERVER_URL
    - ANDROID_APP_PATH / ANDROID_APP_ID is not set
    """
    if not _appium_available():
        pytest.skip(
            f"Appium server not reachable at {APPIUM_SERVER_URL} "
            "— skipping Android tests"
        )

    try:
        from utils.driver_factory import create_driver
        driver = create_driver(platform="android")
    except ImportError as exc:
        pytest.skip(f"Appium client not installed: {exc}")
    except RuntimeError as exc:
        pytest.skip(f"Could not start Android session: {exc}")

    yield driver

    if driver:
        try:
            driver.quit()
        except Exception as exc:
            logger.warning("Error quitting Android driver: %s", exc)


@pytest.fixture(scope="function")
def ios_driver():
    """
    Function-scoped Appium WebDriver fixture for iOS.

    Skips automatically when Appium server is unreachable or iOS
    capabilities are not configured.
    """
    if not _appium_available():
        pytest.skip(
            f"Appium server not reachable at {APPIUM_SERVER_URL} "
            "— skipping iOS tests"
        )

    try:
        from utils.driver_factory import create_driver
        driver = create_driver(platform="ios")
    except ImportError as exc:
        pytest.skip(f"Appium client not installed: {exc}")
    except RuntimeError as exc:
        pytest.skip(f"Could not start iOS session: {exc}")

    yield driver

    if driver:
        try:
            driver.quit()
        except Exception as exc:
            logger.warning("Error quitting iOS driver: %s", exc)


@pytest.fixture(scope="function")
def driver(android_driver, ios_driver):
    """
    Resolves to the appropriate driver based on MOBILE_PLATFORM env var.
    Defaults to android.
    """
    if MOBILE_PLATFORM == "ios":
        return ios_driver
    return android_driver


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("android_driver") or item.funcargs.get("ios_driver")
        if driver:
            try:
                screenshots_dir = "reports/screenshots"
                os.makedirs(screenshots_dir, exist_ok=True)
                safe_name = item.nodeid.replace("::", "_").replace("/", "_")
                path = f"{screenshots_dir}/{safe_name}.png"
                driver.save_screenshot(path)
                logger.info("Failure screenshot saved: %s", path)
            except Exception as exc:
                logger.warning("Could not save screenshot on failure: %s", exc)
