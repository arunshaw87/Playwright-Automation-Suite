import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage
from pages.product_page import ProductPage


@pytest.mark.smoke
@pytest.mark.inventory
class TestInventoryListing:
    def test_products_are_displayed(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        assert inventory.get_item_count() == 6

    def test_inventory_page_title(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.expect_title("Products")

    def test_all_items_have_names(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        names = inventory.get_item_names()
        assert len(names) == 6
        for name in names:
            assert name.strip() != ""

    def test_all_items_have_prices(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        prices = inventory.get_item_prices()
        assert len(prices) == 6
        for price in prices:
            assert "$" in price


@pytest.mark.regression
@pytest.mark.inventory
class TestInventorySorting:
    def test_sort_by_name_a_to_z(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.sort_by("az")
        names = inventory.get_item_names()
        assert names == sorted(names)

    def test_sort_by_name_z_to_a(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.sort_by("za")
        names = inventory.get_item_names()
        assert names == sorted(names, reverse=True)

    def test_sort_by_price_low_to_high(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.sort_by("lohi")
        prices = inventory.get_item_prices()
        numeric = [float(p.replace("$", "")) for p in prices]
        assert numeric == sorted(numeric)

    def test_sort_by_price_high_to_low(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.sort_by("hilo")
        prices = inventory.get_item_prices()
        numeric = [float(p.replace("$", "")) for p in prices]
        assert numeric == sorted(numeric, reverse=True)


@pytest.mark.regression
@pytest.mark.inventory
class TestProductDetailNavigation:
    ITEM_NAME = "Sauce Labs Backpack"

    def test_click_product_name_opens_detail(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.click_item_by_name(self.ITEM_NAME)
        product = ProductPage(logged_in_page)
        product.expect_name(self.ITEM_NAME)

    def test_product_detail_shows_price(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.click_item_by_name(self.ITEM_NAME)
        product = ProductPage(logged_in_page)
        product.expect_price_visible()

    def test_back_button_returns_to_inventory(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.click_item_by_name(self.ITEM_NAME)
        product = ProductPage(logged_in_page)
        product.go_back()
        inventory.expect_title("Products")
