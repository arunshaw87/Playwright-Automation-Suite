from playwright.sync_api import Page, expect
from .base_page import BasePage


class InventoryPage(BasePage):
    URL = "https://www.saucedemo.com/inventory.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._title = page.locator(".title")
        self._inventory_list = page.locator(".inventory_list")
        self._inventory_items = page.locator(".inventory_item")
        self._sort_dropdown = page.locator('[data-test="product-sort-container"]')
        self._cart_badge = page.locator(".shopping_cart_badge")
        self._cart_link = page.locator(".shopping_cart_link")
        self._burger_menu = page.locator("#react-burger-menu-btn")
        self._logout_link = page.locator("#logout_sidebar_link")

    def get_page_title(self) -> str:
        return self._title.inner_text()

    def get_item_count(self) -> int:
        return self._inventory_items.count()

    def get_item_names(self) -> list[str]:
        return self._inventory_items.locator(".inventory_item_name").all_inner_texts()

    def get_item_prices(self) -> list[str]:
        return self._inventory_items.locator(".inventory_item_price").all_inner_texts()

    def add_item_to_cart_by_name(self, item_name: str) -> None:
        item = self._inventory_items.filter(has_text=item_name)
        item.locator("button").click()

    def remove_item_from_cart_by_name(self, item_name: str) -> None:
        item = self._inventory_items.filter(has_text=item_name)
        item.locator("button").click()

    def get_cart_badge_count(self) -> int:
        if not self._cart_badge.is_visible():
            return 0
        return int(self._cart_badge.inner_text())

    def go_to_cart(self) -> None:
        self._cart_link.click()

    def sort_by(self, option_value: str) -> None:
        self._sort_dropdown.select_option(option_value)

    def click_item_by_name(self, item_name: str) -> None:
        self.page.locator(".inventory_item_name", has_text=item_name).click()

    def open_menu(self) -> None:
        self._burger_menu.click()

    def logout(self) -> None:
        self.open_menu()
        self._logout_link.wait_for(state="visible")
        self._logout_link.click()

    def expect_title(self, text: str) -> None:
        expect(self._title).to_have_text(text)

    def expect_item_count(self, count: int) -> None:
        expect(self._inventory_items).to_have_count(count)

    def expect_cart_badge(self, count: int) -> None:
        expect(self._cart_badge).to_have_text(str(count))
