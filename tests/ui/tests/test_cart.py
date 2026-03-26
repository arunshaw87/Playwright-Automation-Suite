import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


ITEM_1 = "Sauce Labs Backpack"
ITEM_2 = "Sauce Labs Bike Light"
ITEM_3 = "Sauce Labs Bolt T-Shirt"


@pytest.mark.smoke
@pytest.mark.cart
class TestAddToCart:
    def test_add_single_item_updates_badge(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart_by_name(ITEM_1)
        inventory.expect_cart_badge(1)

    def test_add_multiple_items_updates_badge(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart_by_name(ITEM_1)
        inventory.add_item_to_cart_by_name(ITEM_2)
        inventory.expect_cart_badge(2)

    def test_add_all_items_shows_correct_badge(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        for name in inventory.get_item_names():
            inventory.add_item_to_cart_by_name(name)
        inventory.expect_cart_badge(6)

    def test_no_badge_when_cart_is_empty(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        badge_count = inventory.get_cart_badge_count()
        assert badge_count == 0


@pytest.mark.regression
@pytest.mark.cart
class TestRemoveFromCart:
    def test_remove_item_from_inventory_updates_badge(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart_by_name(ITEM_1)
        inventory.add_item_to_cart_by_name(ITEM_2)
        inventory.remove_item_from_cart_by_name(ITEM_1)
        inventory.expect_cart_badge(1)

    def test_remove_all_items_clears_badge(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart_by_name(ITEM_1)
        inventory.remove_item_from_cart_by_name(ITEM_1)
        assert inventory.get_cart_badge_count() == 0


@pytest.mark.regression
@pytest.mark.cart
class TestCartPage:
    def test_cart_shows_added_item(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart_by_name(ITEM_1)
        inventory.go_to_cart()
        cart = CartPage(logged_in_page)
        cart.expect_title("Your Cart")
        cart.expect_item_present(ITEM_1)

    def test_cart_shows_multiple_items(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart_by_name(ITEM_1)
        inventory.add_item_to_cart_by_name(ITEM_2)
        inventory.go_to_cart()
        cart = CartPage(logged_in_page)
        cart.expect_item_count(2)

    def test_cart_is_empty_when_nothing_added(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.go_to_cart()
        cart = CartPage(logged_in_page)
        assert cart.is_empty()

    def test_remove_item_from_cart_page(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart_by_name(ITEM_1)
        inventory.add_item_to_cart_by_name(ITEM_2)
        inventory.go_to_cart()
        cart = CartPage(logged_in_page)
        cart.remove_item_by_name(ITEM_1)
        cart.expect_item_count(1)

    def test_continue_shopping_returns_to_inventory(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.go_to_cart()
        cart = CartPage(logged_in_page)
        cart.continue_shopping()
        inventory.expect_title("Products")

    def test_cart_item_prices_are_shown(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart_by_name(ITEM_1)
        inventory.go_to_cart()
        cart = CartPage(logged_in_page)
        prices = cart.get_item_prices()
        assert len(prices) == 1
        assert "$" in prices[0]
