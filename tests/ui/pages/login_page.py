from playwright.sync_api import Page, expect
from .base_page import BasePage


class LoginPage(BasePage):
    URL = "https://www.saucedemo.com/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._username_input = page.locator('[data-test="username"]')
        self._password_input = page.locator('[data-test="password"]')
        self._login_button = page.locator('[data-test="login-button"]')
        self._error_message = page.locator('[data-test="error"]')

    def open(self) -> None:
        self.page.goto(self.URL)

    def login(self, username: str, password: str) -> None:
        self._username_input.fill(username)
        self._password_input.fill(password)
        self._login_button.click()

    def get_error_message(self) -> str:
        return self._error_message.inner_text()

    def is_error_visible(self) -> bool:
        return self._error_message.is_visible()

    def clear_credentials(self) -> None:
        self._username_input.clear()
        self._password_input.clear()

    def expect_error_containing(self, text: str) -> None:
        expect(self._error_message).to_be_visible()
        expect(self._error_message).to_contain_text(text)
