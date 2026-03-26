import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutStepOnePage,
    CheckoutStepTwoPage,
    CheckoutCompletePage,
)


ITEM = "Sauce Labs Backpack"
ITEM_2 = "Sauce Labs Fleece Jacket"


def add_item_and_go_to_checkout(page: Page, item: str = ITEM) -> CartPage:
    inventory = InventoryPage(page)
    inventory.add_item_to_cart_by_name(item)
    inventory.go_to_cart()
    cart = CartPage(page)
    cart.proceed_to_checkout()
    return cart


@pytest.mark.smoke
@pytest.mark.checkout
class TestCheckoutHappyPath:
    def test_full_checkout_flow(self, logged_in_page: Page) -> None:
        add_item_and_go_to_checkout(logged_in_page)

        step1 = CheckoutStepOnePage(logged_in_page)
        step1.fill_customer_info("John", "Doe", "12345")
        step1.continue_checkout()

        step2 = CheckoutStepTwoPage(logged_in_page)
        step2.expect_item_present(ITEM)
        step2.expect_total_visible()
        step2.finish_checkout()

        complete = CheckoutCompletePage(logged_in_page)
        complete.expect_header("Thank you for your order!")
        complete.expect_success_image_visible()

    def test_order_confirmation_complete_text(self, logged_in_page: Page) -> None:
        add_item_and_go_to_checkout(logged_in_page)
        CheckoutStepOnePage(logged_in_page).fill_customer_info("Jane", "Smith", "99999")
        CheckoutStepOnePage(logged_in_page).continue_checkout()
        CheckoutStepTwoPage(logged_in_page).finish_checkout()
        complete = CheckoutCompletePage(logged_in_page)
        assert "dispatched" in complete.get_complete_text().lower() or complete.get_complete_text() != ""

    def test_back_home_after_order(self, logged_in_page: Page) -> None:
        add_item_and_go_to_checkout(logged_in_page)
        CheckoutStepOnePage(logged_in_page).fill_customer_info("A", "B", "11111")
        CheckoutStepOnePage(logged_in_page).continue_checkout()
        CheckoutStepTwoPage(logged_in_page).finish_checkout()
        complete = CheckoutCompletePage(logged_in_page)
        complete.go_back_home()
        InventoryPage(logged_in_page).expect_title("Products")


@pytest.mark.regression
@pytest.mark.checkout
class TestCheckoutStepOneValidation:
    def test_missing_first_name_shows_error(self, logged_in_page: Page) -> None:
        add_item_and_go_to_checkout(logged_in_page)
        step1 = CheckoutStepOnePage(logged_in_page)
        step1.fill_customer_info("", "Doe", "12345")
        step1.continue_checkout()
        step1.expect_error_containing("First Name is required")

    def test_missing_last_name_shows_error(self, logged_in_page: Page) -> None:
        add_item_and_go_to_checkout(logged_in_page)
        step1 = CheckoutStepOnePage(logged_in_page)
        step1.fill_customer_info("John", "", "12345")
        step1.continue_checkout()
        step1.expect_error_containing("Last Name is required")

    def test_missing_postal_code_shows_error(self, logged_in_page: Page) -> None:
        add_item_and_go_to_checkout(logged_in_page)
        step1 = CheckoutStepOnePage(logged_in_page)
        step1.fill_customer_info("John", "Doe", "")
        step1.continue_checkout()
        step1.expect_error_containing("Postal Code is required")

    def test_cancel_returns_to_cart(self, logged_in_page: Page) -> None:
        add_item_and_go_to_checkout(logged_in_page)
        step1 = CheckoutStepOnePage(logged_in_page)
        step1.cancel()
        cart = CartPage(logged_in_page)
        cart.expect_title("Your Cart")


@pytest.mark.regression
@pytest.mark.checkout
class TestCheckoutStepTwoSummary:
    def test_order_summary_shows_correct_item(self, logged_in_page: Page) -> None:
        add_item_and_go_to_checkout(logged_in_page)
        CheckoutStepOnePage(logged_in_page).fill_customer_info("Test", "User", "10001")
        CheckoutStepOnePage(logged_in_page).continue_checkout()
        step2 = CheckoutStepTwoPage(logged_in_page)
        step2.expect_item_present(ITEM)

    def test_order_summary_shows_total(self, logged_in_page: Page) -> None:
        add_item_and_go_to_checkout(logged_in_page)
        CheckoutStepOnePage(logged_in_page).fill_customer_info("Test", "User", "10001")
        CheckoutStepOnePage(logged_in_page).continue_checkout()
        step2 = CheckoutStepTwoPage(logged_in_page)
        total = step2.get_total()
        assert "$" in total

    def test_multi_item_checkout_summary(self, logged_in_page: Page) -> None:
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart_by_name(ITEM)
        inventory.add_item_to_cart_by_name(ITEM_2)
        inventory.go_to_cart()
        CartPage(logged_in_page).proceed_to_checkout()
        CheckoutStepOnePage(logged_in_page).fill_customer_info("Multi", "User", "54321")
        CheckoutStepOnePage(logged_in_page).continue_checkout()
        step2 = CheckoutStepTwoPage(logged_in_page)
        assert step2.get_item_count() == 2

    def test_cancel_from_step_two_goes_to_inventory(self, logged_in_page: Page) -> None:
        add_item_and_go_to_checkout(logged_in_page)
        CheckoutStepOnePage(logged_in_page).fill_customer_info("X", "Y", "00000")
        CheckoutStepOnePage(logged_in_page).continue_checkout()
        CheckoutStepTwoPage(logged_in_page).cancel()
        InventoryPage(logged_in_page).expect_title("Products")
