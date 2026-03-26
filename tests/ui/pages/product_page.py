from playwright.sync_api import Page, expect
from .base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._name = page.locator(".inventory_details_name")
        self._description = page.locator(".inventory_details_desc")
        self._price = page.locator(".inventory_details_price")
        self._add_to_cart_btn = page.locator('[data-test^="add-to-cart"]')
        self._remove_btn = page.locator('[data-test^="remove"]')
        self._back_button = page.locator('[data-test="back-to-products"]')

    def get_name(self) -> str:
        return self._name.inner_text()

    def get_description(self) -> str:
        return self._description.inner_text()

    def get_price(self) -> str:
        return self._price.inner_text()

    def add_to_cart(self) -> None:
        self._add_to_cart_btn.click()

    def remove_from_cart(self) -> None:
        self._remove_btn.click()

    def go_back(self) -> None:
        self._back_button.click()

    def expect_name(self, name: str) -> None:
        expect(self._name).to_have_text(name)

    def expect_price_visible(self) -> None:
        expect(self._price).to_be_visible()
