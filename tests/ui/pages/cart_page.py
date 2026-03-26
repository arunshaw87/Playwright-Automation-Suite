from playwright.sync_api import Page, expect
from .base_page import BasePage


class CartPage(BasePage):
    URL = "https://www.saucedemo.com/cart.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._title = page.locator(".title")
        self._cart_items = page.locator(".cart_item")
        self._checkout_btn = page.locator('[data-test="checkout"]')
        self._continue_shopping_btn = page.locator('[data-test="continue-shopping"]')

    def get_page_title(self) -> str:
        return self._title.inner_text()

    def get_cart_item_count(self) -> int:
        return self._cart_items.count()

    def get_item_names(self) -> list[str]:
        return self._cart_items.locator(".inventory_item_name").all_inner_texts()

    def get_item_prices(self) -> list[str]:
        return self._cart_items.locator(".inventory_item_price").all_inner_texts()

    def remove_item_by_name(self, item_name: str) -> None:
        item = self._cart_items.filter(has_text=item_name)
        item.locator("button").click()

    def proceed_to_checkout(self) -> None:
        self._checkout_btn.click()

    def continue_shopping(self) -> None:
        self._continue_shopping_btn.click()

    def is_empty(self) -> bool:
        return self._cart_items.count() == 0

    def expect_title(self, text: str) -> None:
        expect(self._title).to_have_text(text)

    def expect_item_count(self, count: int) -> None:
        expect(self._cart_items).to_have_count(count)

    def expect_item_present(self, item_name: str) -> None:
        expect(self._cart_items.filter(has_text=item_name)).to_be_visible()
