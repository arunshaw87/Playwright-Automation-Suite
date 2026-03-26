"""
ProductListPage — Page Object for the product catalogue / list screen.
"""
from __future__ import annotations

from typing import Any

from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class ProductListPage(BasePage):
    SORT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-Modal Selector Button")
    PRODUCT_ITEMS = (
        AppiumBy.XPATH,
        "//*[@content-desc='test-Item title']",
    )
    FIRST_PRODUCT_TITLE = (
        AppiumBy.XPATH,
        "(//*[@content-desc='test-Item title'])[1]",
    )

    def __init__(self, driver: Any) -> None:
        super().__init__(driver)

    def get_product_titles(self) -> list[str]:
        """Return a list of visible product title strings."""
        try:
            elements = self.driver.find_elements(*self.PRODUCT_ITEMS)
            return [el.text for el in elements]
        except Exception:
            return []

    def tap_first_product(self) -> None:
        self.tap(self.FIRST_PRODUCT_TITLE)

    def tap_sort(self) -> None:
        self.tap(self.SORT_BUTTON)

    def scroll_to_bottom(self) -> None:
        for _ in range(3):
            self.swipe_up()

    def scroll_to_top(self) -> None:
        for _ in range(3):
            self.swipe_down()
