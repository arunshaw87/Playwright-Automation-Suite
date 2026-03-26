"""
ProductListPage — Page Object for the product catalogue / list screen.
"""
from __future__ import annotations

from typing import Any

from pages.base_page import BasePage


class ProductListPage(BasePage):
    @staticmethod
    def _by():
        from appium.webdriver.common.appiumby import AppiumBy
        return AppiumBy

    @property
    def SORT_BUTTON(self):
        return (self._by().ACCESSIBILITY_ID, "test-Modal Selector Button")

    @property
    def PRODUCT_ITEMS(self):
        return (self._by().XPATH, "//*[@content-desc='test-Item title']")

    @property
    def FIRST_PRODUCT_TITLE(self):
        return (self._by().XPATH, "(//*[@content-desc='test-Item title'])[1]")

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
