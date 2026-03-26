import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


VALID_USER = "standard_user"
LOCKED_USER = "locked_out_user"
PROBLEM_USER = "problem_user"
VALID_PASSWORD = "secret_sauce"
WRONG_PASSWORD = "wrong_password"


@pytest.mark.smoke
@pytest.mark.login
class TestLoginSuccess:
    def test_valid_login_redirects_to_inventory(self, page: Page) -> None:
        login = LoginPage(page)
        login.open()
        login.login(VALID_USER, VALID_PASSWORD)
        page.wait_for_url("**/inventory.html")
        assert "inventory.html" in page.url

    def test_valid_login_shows_inventory_title(self, page: Page) -> None:
        login = LoginPage(page)
        login.open()
        login.login(VALID_USER, VALID_PASSWORD)
        page.wait_for_url("**/inventory.html")
        inventory = InventoryPage(page)
        inventory.expect_title("Products")

    def test_valid_login_shows_products(self, page: Page) -> None:
        login = LoginPage(page)
        login.open()
        login.login(VALID_USER, VALID_PASSWORD)
        page.wait_for_url("**/inventory.html")
        inventory = InventoryPage(page)
        assert inventory.get_item_count() > 0


@pytest.mark.regression
@pytest.mark.login
class TestLoginFailure:
    def test_wrong_password_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.open()
        login.login(VALID_USER, WRONG_PASSWORD)
        login.expect_error_containing("Username and password do not match")

    def test_wrong_username_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.open()
        login.login("unknown_user", VALID_PASSWORD)
        login.expect_error_containing("Username and password do not match")

    def test_empty_username_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.open()
        login.login("", VALID_PASSWORD)
        login.expect_error_containing("Username is required")

    def test_empty_password_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.open()
        login.login(VALID_USER, "")
        login.expect_error_containing("Password is required")

    def test_both_empty_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.open()
        login.login("", "")
        login.expect_error_containing("Username is required")

    def test_locked_out_user_shows_error(self, page: Page) -> None:
        login = LoginPage(page)
        login.open()
        login.login(LOCKED_USER, VALID_PASSWORD)
        login.expect_error_containing("Sorry, this user has been locked out")


@pytest.mark.regression
@pytest.mark.login
class TestLoginNavigation:
    def test_url_is_login_page_on_open(self, page: Page) -> None:
        login = LoginPage(page)
        login.open()
        assert page.url == LoginPage.URL

    def test_cannot_access_inventory_without_login(self, page: Page) -> None:
        page.goto("https://www.saucedemo.com/inventory.html")
        assert page.url == LoginPage.URL

    def test_logout_redirects_to_login(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.logout()
        logged_in_page.wait_for_url(LoginPage.URL)
        assert logged_in_page.url == LoginPage.URL

    @pytest.mark.parametrize("username,password", [
        ("standard_user", "secret_sauce"),
        ("problem_user", "secret_sauce"),
        ("performance_glitch_user", "secret_sauce"),
        ("error_user", "secret_sauce"),
    ])
    def test_multiple_valid_users_can_login(
        self, page: Page, username: str, password: str
    ) -> None:
        login = LoginPage(page)
        login.open()
        login.login(username, password)
        page.wait_for_url("**/inventory.html", timeout=15_000)
        assert "inventory.html" in page.url
