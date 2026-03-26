"""
LoginPage — Page Object for the app's login screen.

Targets the Appium demo app (or any app with username/password login).
Locators use accessibility IDs which work cross-platform (Android + iOS).
Override locators in a subclass if your app uses different identifiers.
"""
from __future__ import annotations

from typing import Any

from pages.base_page import BasePage


class LoginPage(BasePage):
    # Locators — using accessibility IDs for cross-platform compatibility
    @staticmethod
    def _by():
        from appium.webdriver.common.appiumby import AppiumBy
        return AppiumBy

    @property
    def USERNAME_FIELD(self):
        return (self._by().ACCESSIBILITY_ID, "test-Username")

    @property
    def PASSWORD_FIELD(self):
        return (self._by().ACCESSIBILITY_ID, "test-Password")

    @property
    def LOGIN_BUTTON(self):
        return (self._by().ACCESSIBILITY_ID, "test-LOGIN")

    @property
    def ERROR_CONTAINER(self):
        return (self._by().ACCESSIBILITY_ID, "test-Error message")

    def __init__(self, driver: Any) -> None:
        super().__init__(driver)

    def enter_username(self, username: str) -> "LoginPage":
        self.enter_text(self.USERNAME_FIELD, username)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        self.enter_text(self.PASSWORD_FIELD, password)
        return self

    def tap_login(self) -> None:
        self.tap(self.LOGIN_BUTTON)

    def login(self, username: str, password: str) -> None:
        """Complete login flow: fill credentials and tap login button."""
        self.enter_username(username)
        self.enter_password(password)
        self.tap_login()

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_CONTAINER)

    def is_error_displayed(self) -> bool:
        return self.is_displayed(self.ERROR_CONTAINER, timeout=5)

    def is_login_button_displayed(self) -> bool:
        return self.is_displayed(self.LOGIN_BUTTON)
