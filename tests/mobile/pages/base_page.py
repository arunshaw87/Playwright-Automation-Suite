"""
BasePage — common interface for all mobile Page Object classes.

Every page object inherits from this class. Provides:
- Implicit wait on instantiation
- Explicit wait shortcuts (delegating to wait_helpers)
- Screenshot on assertion failure
- Safe tap / send_keys wrappers
"""
from __future__ import annotations

import logging
import os
from typing import Any

from utils.wait_helpers import (
    wait_for_element_visible,
    wait_for_element_clickable,
    wait_for_element_present,
    wait_for_text_present,
    swipe_up,
    swipe_down,
)

logger = logging.getLogger(__name__)


class BasePage:
    DEFAULT_TIMEOUT = int(os.environ.get("MOBILE_ELEMENT_TIMEOUT", "10"))

    def __init__(self, driver: Any) -> None:
        self.driver = driver

    # ------------------------------------------------------------------
    # Wait wrappers
    # ------------------------------------------------------------------

    def wait_visible(self, locator: tuple, timeout: int | None = None) -> Any:
        return wait_for_element_visible(
            self.driver, locator, timeout=timeout or self.DEFAULT_TIMEOUT
        )

    def wait_clickable(self, locator: tuple, timeout: int | None = None) -> Any:
        return wait_for_element_clickable(
            self.driver, locator, timeout=timeout or self.DEFAULT_TIMEOUT
        )

    def wait_present(self, locator: tuple, timeout: int | None = None) -> Any:
        return wait_for_element_present(
            self.driver, locator, timeout=timeout or self.DEFAULT_TIMEOUT
        )

    def wait_text(
        self, locator: tuple, text: str, timeout: int | None = None
    ) -> Any:
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
        try:
            element = wait_for_element_visible(self.driver, locator, timeout=timeout)
            return element.is_displayed()
        except Exception:
            return False

    def swipe_up(self) -> None:
        swipe_up(self.driver)

    def swipe_down(self) -> None:
        swipe_down(self.driver)

    def take_screenshot(self, name: str) -> str | None:
        """Save a screenshot to reports/screenshots/<name>.png. Returns the path."""
        screenshots_dir = "reports/screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)
        path = f"{screenshots_dir}/{name}.png"
        try:
            self.driver.save_screenshot(path)
            logger.info("Screenshot saved: %s", path)
            return path
        except Exception as exc:
            logger.warning("Failed to take screenshot: %s", exc)
            return None
