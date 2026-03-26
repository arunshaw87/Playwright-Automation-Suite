"""
ProductDetailPage — Page Object for the individual product detail screen.
"""
from __future__ import annotations

from typing import Any

from pages.base_page import BasePage


class ProductDetailPage(BasePage):
    @staticmethod
    def _by():
        from appium.webdriver.common.appiumby import AppiumBy
        return AppiumBy

    @property
    def PRODUCT_TITLE(self):
        return (self._by().ACCESSIBILITY_ID, "test-Description")

    @property
    def ADD_TO_CART_BUTTON(self):
        return (self._by().ACCESSIBILITY_ID, "test-ADD TO CART")

    @property
    def REMOVE_BUTTON(self):
        return (self._by().ACCESSIBILITY_ID, "test-REMOVE")

    @property
    def BACK_BUTTON(self):
        return (self._by().ACCESSIBILITY_ID, "test-GO BACK")

    @property
    def PRODUCT_PRICE(self):
        return (self._by().ACCESSIBILITY_ID, "test-Price")

    def __init__(self, driver: Any) -> None:
        super().__init__(driver)

    def get_product_title(self) -> str:
        return self.get_text(self.PRODUCT_TITLE)

    def get_product_price(self) -> str:
        return self.get_text(self.PRODUCT_PRICE)

    def tap_add_to_cart(self) -> None:
        self.tap(self.ADD_TO_CART_BUTTON)

    def tap_remove(self) -> None:
        self.tap(self.REMOVE_BUTTON)

    def tap_back(self) -> None:
        self.tap(self.BACK_BUTTON)

    def is_add_to_cart_displayed(self) -> bool:
        return self.is_displayed(self.ADD_TO_CART_BUTTON)
