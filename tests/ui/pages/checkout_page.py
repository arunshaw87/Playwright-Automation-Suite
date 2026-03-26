from playwright.sync_api import Page, expect
from .base_page import BasePage


class CheckoutStepOnePage(BasePage):
    URL = "https://www.saucedemo.com/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._title = page.locator(".title")
        self._first_name = page.locator('[data-test="firstName"]')
        self._last_name = page.locator('[data-test="lastName"]')
        self._postal_code = page.locator('[data-test="postalCode"]')
        self._continue_btn = page.locator('[data-test="continue"]')
        self._cancel_btn = page.locator('[data-test="cancel"]')
        self._error_message = page.locator('[data-test="error"]')

    def fill_customer_info(
        self,
        first_name: str,
        last_name: str,
        postal_code: str,
    ) -> None:
        self._first_name.fill(first_name)
        self._last_name.fill(last_name)
        self._postal_code.fill(postal_code)

    def continue_checkout(self) -> None:
        self._continue_btn.click()

    def cancel(self) -> None:
        self._cancel_btn.click()

    def get_error_message(self) -> str:
        return self._error_message.inner_text()

    def is_error_visible(self) -> bool:
        return self._error_message.is_visible()

    def expect_error_containing(self, text: str) -> None:
        expect(self._error_message).to_be_visible()
        expect(self._error_message).to_contain_text(text)


class CheckoutStepTwoPage(BasePage):
    URL = "https://www.saucedemo.com/checkout-step-two.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._title = page.locator(".title")
        self._cart_items = page.locator(".cart_item")
        self._summary_subtotal = page.locator(".summary_subtotal_label")
        self._summary_tax = page.locator(".summary_tax_label")
        self._summary_total = page.locator(".summary_total_label")
        self._finish_btn = page.locator('[data-test="finish"]')
        self._cancel_btn = page.locator('[data-test="cancel"]')

    def get_subtotal(self) -> str:
        return self._summary_subtotal.inner_text()

    def get_tax(self) -> str:
        return self._summary_tax.inner_text()

    def get_total(self) -> str:
        return self._summary_total.inner_text()

    def get_item_count(self) -> int:
        return self._cart_items.count()

    def finish_checkout(self) -> None:
        self._finish_btn.click()

    def cancel(self) -> None:
        self._cancel_btn.click()

    def expect_item_present(self, item_name: str) -> None:
        expect(self._cart_items.filter(has_text=item_name)).to_be_visible()

    def expect_total_visible(self) -> None:
        expect(self._summary_total).to_be_visible()


class CheckoutCompletePage(BasePage):
    URL = "https://www.saucedemo.com/checkout-complete.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._header = page.locator('[data-test="complete-header"]')
        self._text = page.locator('[data-test="complete-text"]')
        self._back_home_btn = page.locator('[data-test="back-to-products"]')
        self._pony_express_img = page.locator('[data-test="pony-express"]')

    def get_header(self) -> str:
        return self._header.inner_text()

    def get_complete_text(self) -> str:
        return self._text.inner_text()

    def go_back_home(self) -> None:
        self._back_home_btn.click()

    def expect_header(self, text: str) -> None:
        expect(self._header).to_have_text(text)

    def expect_success_image_visible(self) -> None:
        expect(self._pony_express_img).to_be_visible()
