"""
Mobile product browsing tests.

Covers:
- Product list displays items
- Tapping a product opens the detail screen
- Detail screen shows title and price
- Add to Cart functionality
- Back navigation after viewing a product
"""
import pytest

from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.product_list_page import ProductListPage
from pages.product_detail_page import ProductDetailPage

VALID_USERNAME = "standard_user"
VALID_PASSWORD = "secret_sauce"


@pytest.fixture(autouse=True)
def _login(android_driver):
    """Login before each product test."""
    LoginPage(android_driver).login(VALID_USERNAME, VALID_PASSWORD)


@pytest.mark.regression
@pytest.mark.mobile
@pytest.mark.product
class TestProductBrowse:
    def test_product_list_not_empty(self, android_driver) -> None:
        page = ProductListPage(android_driver)
        titles = page.get_product_titles()
        assert len(titles) > 0, "Product list must not be empty"

    def test_product_titles_are_strings(self, android_driver) -> None:
        page = ProductListPage(android_driver)
        titles = page.get_product_titles()
        for title in titles:
            assert isinstance(title, str) and title.strip(), (
                f"Product title must be a non-empty string, got {title!r}"
            )

    def test_tap_first_product_opens_detail(self, android_driver) -> None:
        list_page = ProductListPage(android_driver)
        list_page.tap_first_product()
        detail = ProductDetailPage(android_driver)
        assert detail.is_add_to_cart_displayed(), (
            "Add to Cart button should be visible on product detail screen"
        )

    def test_detail_screen_shows_title(self, android_driver) -> None:
        ProductListPage(android_driver).tap_first_product()
        detail = ProductDetailPage(android_driver)
        title = detail.get_product_title()
        assert title and title.strip(), "Product detail title must not be empty"

    def test_detail_screen_shows_price(self, android_driver) -> None:
        ProductListPage(android_driver).tap_first_product()
        detail = ProductDetailPage(android_driver)
        price = detail.get_product_price()
        assert price and "$" in price, (
            f"Expected price to contain '$', got: {price!r}"
        )

    def test_add_to_cart_then_remove(self, android_driver) -> None:
        ProductListPage(android_driver).tap_first_product()
        detail = ProductDetailPage(android_driver)
        detail.tap_add_to_cart()
        assert detail.is_displayed(detail.REMOVE_BUTTON), (
            "Remove button should appear after adding to cart"
        )
        detail.tap_remove()
        assert detail.is_add_to_cart_displayed(), (
            "Add to Cart button should reappear after removing from cart"
        )

    def test_back_from_detail_returns_to_list(self, android_driver) -> None:
        ProductListPage(android_driver).tap_first_product()
        ProductDetailPage(android_driver).tap_back()
        home = HomePage(android_driver)
        assert home.is_products_screen_displayed(), (
            "Should return to products screen after tapping back"
        )
