"""
Mobile test framework conftest.

Fixtures
--------
android_driver   : function — Appium WebDriver for Android (skips if unavailable)
ios_driver       : function — Appium WebDriver for iOS (skips if unavailable)
driver           : function — Resolves to Android or iOS driver based on MOBILE_PLATFORM
"""
from __future__ import annotations

import base64
import logging
import os
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)

MOBILE_PLATFORM = os.environ.get("MOBILE_PLATFORM", "android").lower()
APPIUM_SERVER_URL = os.environ.get("APPIUM_SERVER_URL", "http://localhost:4723")

_MOBILE_DIR = Path(__file__).parent
_REPORTS_DIR = _MOBILE_DIR / "reports"


def pytest_configure(config: pytest.Config) -> None:
    """
    Create report directories and normalise all output paths to absolute so
    that the suite produces consistent artefacts regardless of the working
    directory from which pytest is invoked (e.g. repo root vs tests/mobile/).
    """
    for sub in ("html", "junit", "screenshots"):
        (_REPORTS_DIR / sub).mkdir(parents=True, exist_ok=True)

    html_report = str(_REPORTS_DIR / "html" / "report.html")
    junit_report = str(_REPORTS_DIR / "junit" / "results.xml")

    if hasattr(config, "option"):
        if hasattr(config.option, "htmlpath"):
            config.option.htmlpath = html_report
        if hasattr(config.option, "xmlpath"):
            config.option.xmlpath = junit_report


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
def driver(request):
    """
    Resolves to the appropriate driver based on MOBILE_PLATFORM env var.
    Lazily requests only the needed platform fixture to avoid spinning up
    both Android and iOS sessions.
    Defaults to android.
    """
    fixture_name = "ios_driver" if MOBILE_PLATFORM == "ios" else "android_driver"
    return request.getfixturevalue(fixture_name)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure using Appium base64 screenshot."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = (
            item.funcargs.get("driver")
            or item.funcargs.get("android_driver")
            or item.funcargs.get("ios_driver")
        )
        if drv:
            try:
                screenshots_dir = _REPORTS_DIR / "screenshots"
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                safe_name = item.nodeid.replace("::", "_").replace("/", "_")
                path = screenshots_dir / f"{safe_name}.png"
                screenshot_b64: str = drv.get_screenshot_as_base64()
                path.write_bytes(base64.b64decode(screenshot_b64))
                logger.info("Failure screenshot saved: %s", path)
            except Exception as exc:
                logger.warning("Could not save screenshot on failure: %s", exc)
