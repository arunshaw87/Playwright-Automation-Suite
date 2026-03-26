"""
HomePage — Page Object for the main/home screen after login.
"""
from __future__ import annotations

from typing import Any

from pages.base_page import BasePage


class HomePage(BasePage):
    @staticmethod
    def _by():
        from appium.webdriver.common.appiumby import AppiumBy
        return AppiumBy

    @property
    def PRODUCTS_TITLE(self):
        return (self._by().ACCESSIBILITY_ID, "test-PRODUCTS")

    @property
    def MENU_BUTTON(self):
        return (self._by().ACCESSIBILITY_ID, "test-Menu")

    @property
    def CART_BUTTON(self):
        return (self._by().ACCESSIBILITY_ID, "test-Cart")

    def __init__(self, driver: Any) -> None:
        super().__init__(driver)

    def is_products_screen_displayed(self) -> bool:
        return self.is_displayed(self.PRODUCTS_TITLE)

    def tap_menu(self) -> None:
        self.tap(self.MENU_BUTTON)

    def tap_cart(self) -> None:
        self.tap(self.CART_BUTTON)

    def get_page_title(self) -> str:
        return self.get_text(self.PRODUCTS_TITLE)
