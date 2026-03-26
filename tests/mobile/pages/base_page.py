"""
BasePage — common interface for all mobile Page Object classes.

Every page object inherits from this class. Provides:
- Explicit wait shortcuts (delegating to wait_helpers)
- Screenshot capture
- Safe tap / send_keys wrappers
- Swipe gestures
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_MOBILE_DIR = Path(__file__).parent.parent


class BasePage:
    DEFAULT_TIMEOUT = int(os.environ.get("MOBILE_ELEMENT_TIMEOUT", "10"))

    def __init__(self, driver: Any) -> None:
        self.driver = driver

    # ------------------------------------------------------------------
    # Wait wrappers (lazy-imported so selenium need not be on PYTHONPATH
    # at import time — only when a driver is actually used)
    # ------------------------------------------------------------------

    def wait_visible(self, locator: tuple, timeout: int | None = None) -> Any:
        from utils.wait_helpers import wait_for_element_visible
        return wait_for_element_visible(
            self.driver, locator, timeout=timeout or self.DEFAULT_TIMEOUT
        )

    def wait_clickable(self, locator: tuple, timeout: int | None = None) -> Any:
        from utils.wait_helpers import wait_for_element_clickable
        return wait_for_element_clickable(
            self.driver, locator, timeout=timeout or self.DEFAULT_TIMEOUT
        )

    def wait_present(self, locator: tuple, timeout: int | None = None) -> Any:
        from utils.wait_helpers import wait_for_element_present
        return wait_for_element_present(
            self.driver, locator, timeout=timeout or self.DEFAULT_TIMEOUT
        )

    def wait_text(
        self, locator: tuple, text: str, timeout: int | None = None
    ) -> Any:
        from utils.wait_helpers import wait_for_text_present
        return wait_for_text_present(
            self.driver, locator, text, timeout=timeout or self.DEFAULT_TIMEOUT
        )

    # ------------------------------------------------------------------
    # Interaction wrappers
    # ------------------------------------------------------------------

    def tap(self, locator: tuple, timeout: int | None = None) -> None:
        element = self.wait_clickable(locator, timeout=timeout)
        element.click()

    def enter_text(
        self, locator: tuple, text: str, clear_first: bool = True
    ) -> None:
        element = self.wait_visible(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        element = self.wait_visible(locator)
        return element.text

    def is_displayed(self, locator: tuple, timeout: int = 3) -> bool:
        from utils.wait_helpers import wait_for_element_visible
        try:
            element = wait_for_element_visible(self.driver, locator, timeout=timeout)
            return element.is_displayed()
        except Exception:
            return False

    def swipe_up(self) -> None:
        from utils.wait_helpers import swipe_up
        swipe_up(self.driver)

    def swipe_down(self) -> None:
        from utils.wait_helpers import swipe_down
        swipe_down(self.driver)

    def take_screenshot(self, name: str) -> str | None:
        """
        Save an Appium base64 screenshot to reports/screenshots/<name>.png.
        Returns the absolute path string, or None on failure.
        """
        import base64
        screenshots_dir = _MOBILE_DIR / "reports" / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        path = screenshots_dir / f"{name}.png"
        try:
            screenshot_b64: str = self.driver.get_screenshot_as_base64()
            path.write_bytes(base64.b64decode(screenshot_b64))
            logger.info("Screenshot saved: %s", path)
            return str(path)
        except Exception as exc:
            logger.warning("Failed to take screenshot: %s", exc)
            return None
