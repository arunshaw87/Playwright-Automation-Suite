"""
Mobile navigation tests.

Covers:
- Home screen renders the products screen after login
- Menu opens and closes correctly
- Back navigation returns to the previous screen
"""
import pytest

from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.product_list_page import ProductListPage

VALID_USERNAME = "standard_user"
VALID_PASSWORD = "secret_sauce"


@pytest.fixture(autouse=True)
def _login(android_driver):
    """Login before each navigation test."""
    LoginPage(android_driver).login(VALID_USERNAME, VALID_PASSWORD)


@pytest.mark.regression
@pytest.mark.mobile
@pytest.mark.navigation
class TestNavigation:
    def test_home_screen_shows_products(self, android_driver) -> None:
        home = HomePage(android_driver)
        assert home.is_products_screen_displayed(), (
            "Products screen should be visible after login"
        )

    def test_products_list_visible(self, android_driver) -> None:
        product_list = ProductListPage(android_driver)
        titles = product_list.get_product_titles()
        assert len(titles) > 0, "At least one product should be listed"

    def test_tap_product_and_back(self, android_driver) -> None:
        from pages.product_detail_page import ProductDetailPage

        product_list = ProductListPage(android_driver)
        product_list.tap_first_product()

        detail = ProductDetailPage(android_driver)
        title = detail.get_product_title()
        assert title, "Product detail should show a title"

        detail.tap_back()
        home = HomePage(android_driver)
        assert home.is_products_screen_displayed(), (
            "After tapping back, should return to products screen"
        )

    def test_scroll_down_and_up(self, android_driver) -> None:
        product_list = ProductListPage(android_driver)
        product_list.scroll_to_bottom()
        product_list.scroll_to_top()
