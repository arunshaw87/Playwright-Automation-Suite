"""
Explicit wait helpers for mobile tests.

Wraps Appium/Selenium waits with clear error messages and
mobile-specific expected conditions.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
POLL_FREQUENCY = 0.5


def wait_for_element_visible(
    driver: Any,
    locator: tuple,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    """Wait until the element located by ``locator`` is visible.

    Returns the WebElement when visible.
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    return WebDriverWait(driver, timeout, poll_frequency=POLL_FREQUENCY).until(
        EC.visibility_of_element_located(locator),
        message=f"Element {locator} not visible after {timeout}s",
    )


def wait_for_element_clickable(
    driver: Any,
    locator: tuple,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    """Wait until the element is clickable and return it."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    return WebDriverWait(driver, timeout, poll_frequency=POLL_FREQUENCY).until(
        EC.element_to_be_clickable(locator),
        message=f"Element {locator} not clickable after {timeout}s",
    )


def wait_for_element_present(
    driver: Any,
    locator: tuple,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    """Wait until the element is present in the DOM (not necessarily visible)."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    return WebDriverWait(driver, timeout, poll_frequency=POLL_FREQUENCY).until(
        EC.presence_of_element_located(locator),
        message=f"Element {locator} not present after {timeout}s",
    )


def wait_for_text_present(
    driver: Any,
    locator: tuple,
    text: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    """Wait until the element contains the expected text."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    return WebDriverWait(driver, timeout, poll_frequency=POLL_FREQUENCY).until(
        EC.text_to_be_present_in_element(locator, text),
        message=f"Text '{text}' not found in element {locator} after {timeout}s",
    )


def swipe_up(driver: Any, duration: int = 800) -> None:
    """Perform an upward swipe gesture (scroll down the screen)."""
    size = driver.get_window_size()
    start_x = size["width"] // 2
    start_y = int(size["height"] * 0.8)
    end_y = int(size["height"] * 0.2)
    driver.swipe(start_x, start_y, start_x, end_y, duration)


def swipe_down(driver: Any, duration: int = 800) -> None:
    """Perform a downward swipe gesture (scroll up the screen)."""
    size = driver.get_window_size()
    start_x = size["width"] // 2
    start_y = int(size["height"] * 0.2)
    end_y = int(size["height"] * 0.8)
    driver.swipe(start_x, start_y, start_x, end_y, duration)
