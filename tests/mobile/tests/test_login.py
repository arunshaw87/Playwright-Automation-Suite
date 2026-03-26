"""
Mobile login flow tests.

Covers:
- Valid login navigates to home screen
- Invalid credentials show error message
- Empty fields show validation error
- Login button is present on the login screen

All tests skip when Appium server is unavailable (handled by fixture).
"""
import pytest

from pages.login_page import LoginPage
from pages.home_page import HomePage

VALID_USERNAME = "standard_user"
VALID_PASSWORD = "secret_sauce"
LOCKED_USERNAME = "locked_out_user"
INVALID_PASSWORD = "wrong_password"


@pytest.mark.smoke
@pytest.mark.mobile
@pytest.mark.login
class TestLoginFlow:
    def test_login_button_present_on_launch(self, android_driver) -> None:
        page = LoginPage(android_driver)
        assert page.is_login_button_displayed(), "Login button should be visible on launch"

    def test_valid_login_navigates_to_home(self, android_driver) -> None:
        login_page = LoginPage(android_driver)
        login_page.login(VALID_USERNAME, VALID_PASSWORD)
        home_page = HomePage(android_driver)
        assert home_page.is_products_screen_displayed(), (
            "After valid login, products screen should be displayed"
        )

    def test_invalid_password_shows_error(self, android_driver) -> None:
        page = LoginPage(android_driver)
        page.login(VALID_USERNAME, INVALID_PASSWORD)
        assert page.is_error_displayed(), "Error message should appear for wrong password"
        error_text = page.get_error_message()
        assert "Username and password" in error_text or "incorrect" in error_text.lower()

    def test_locked_user_shows_error(self, android_driver) -> None:
        page = LoginPage(android_driver)
        page.login(LOCKED_USERNAME, VALID_PASSWORD)
        assert page.is_error_displayed(), "Error message should appear for locked user"

    @pytest.mark.parametrize("username,password", [
        ("", VALID_PASSWORD),
        (VALID_USERNAME, ""),
        ("", ""),
    ])
    def test_empty_fields_show_error(
        self, android_driver, username: str, password: str
    ) -> None:
        page = LoginPage(android_driver)
        page.login(username, password)
        assert page.is_error_displayed(), (
            f"Error should be shown for empty credentials: "
            f"username={username!r}, password={password!r}"
        )
