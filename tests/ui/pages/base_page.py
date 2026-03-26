from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, path: str = "") -> None:
        self.page.goto(path)

    def get_title(self) -> str:
        return self.page.title()

    def wait_for_url(self, url_pattern: str, timeout: int = 10_000) -> None:
        self.page.wait_for_url(url_pattern, timeout=timeout)
