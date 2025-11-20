from selenium.webdriver.common.by import By

from core.ui.page_objects.base_page import BasePage


class Sidebar(BasePage):
    """Left panel 'Book Store Application' menu on inner pages."""

    BOOK_APP_HEADER = (By.XPATH, "//div[@class='left-pannel']//div[contains(@class,'header-text') and normalize-space()='Book Store Application']")

    def expand_book_store(self):
        # Idempotent expand — click header if items are not visible yet
        if not self._is_item_visible("Login"):
            self.click(self.BOOK_APP_HEADER)

    def _is_item_visible(self, name: str) -> bool:
        items = self.driver.find_elements(By.XPATH, f"//div[@class='left-pannel']//span[text()='{name}']")
        return bool(items) and items[0].is_displayed()

    def click_item(self, name: str):
        self.expand_book_store()
        self.click((By.XPATH, f"//div[@class='left-pannel']//span[text()='{name}']"))
