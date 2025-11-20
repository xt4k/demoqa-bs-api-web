import allure
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from .base_page import BasePage
from .locators.books_page_locators import BooksPageLocators as Loc


class BooksPage(BasePage):
    """
    Page object for Book Store page.

    Provides operations for:
      - searching books;
      - changing rows-per-page (pagination size);
      - reading book titles from the current grid page;
      - navigating between pages and reading pagination state.
    """


    @allure.step("Search for '{query}' in books list")
    def search(self, query: str) -> None:
        self._type(Loc.SEARCH, query)

    @allure.step("Set {books_per_page} books per page")
    def set_rows_per_page(self, books_per_page: int = 5) -> None:
        selector = self.driver.find_element(*Loc.ROWS_SELECT)
        if selector:
            Select(selector).select_by_value(str(books_per_page))

    @allure.step("Get list of book titles on current page")
    def book_titles(self) -> list[str]:
        els = self.wait.until(EC.presence_of_all_elements_located(Loc.TITLES_SELECTOR))
        titles: list[str] = []
        for el in els:
            text = el.text.strip()
            if text:
                titles.append(text)
        return titles

    @allure.step("Navigate to next page")
    def go_next_page(self) -> None:
        self.driver.find_element(*Loc.NEXT_PAGE_BTN).click()

    @allure.step("Get current page number")
    def current_page_num(self) -> str:
        return self.driver.find_element(*Loc.THIS_PAGE_NUM).get_attribute("value")

    @allure.step("Get total pages number")
    def total_book_pages(self) -> str:
        return self.wait.until(
            EC.visibility_of_element_located(Loc.TOTAL_PAGE_NUM)
        ).text.strip()

    @allure.step("Navigate to previous page")
    def go_previous_page(self) -> None:
        self.driver.find_element(*Loc.PREV_PAGE_BTN).click()
