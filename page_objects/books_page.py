from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage

class BooksPage(BasePage):
    SEARCH = (By.ID, "searchBox")
    ROWS_SELECT = (By.TAG_NAME, "select")
    NEXT_BTN = (By.XPATH, "//button[normalize-space()='Next']")
    PREV_BTN = (By.XPATH, "//button[normalize-space()='Previous']")
    PAGE_LABEL = (By.XPATH, "//span[contains(., 'Page') and contains(., 'of')]")
    ROWS = (By.CSS_SELECTOR, "div.rt-tr-group")

    def open_page(self):
        self.open("books")

    def search(self, query: str):
        self.type(self.SEARCH, query)

    def set_rows(self, label: str = "5 rows"):
        selects = self.driver.find_elements(*self.ROWS_SELECT)
        if selects:
            Select(selects[0]).select_by_visible_text(label)

    def click_next(self):
        self.driver.find_element(*self.NEXT_BTN).click()

    def click_prev(self):
        self.driver.find_element(*self.PREV_BTN).click()
