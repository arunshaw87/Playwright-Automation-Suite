"""
HomePage — Page Object for the main/home screen after login.
"""
from __future__ import annotations

from typing import Any

from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class HomePage(BasePage):
    PRODUCTS_TITLE = (AppiumBy.ACCESSIBILITY_ID, "test-PRODUCTS")
    MENU_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-Menu")
    CART_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "test-Cart")
    PRODUCT_LIST = (AppiumBy.ACCESSIBILITY_ID, "test-PRODUCTS")

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
