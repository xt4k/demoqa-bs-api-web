import allure
from assertpy import soft_assertions, assert_that

from core.ui.page_objects.books_page import BooksPage
from tests.ui.base_test import BaseTest


@allure.epic("Books page")
class TestBooksPage(BaseTest):

    @allure.title("Search shows books about JavaScript app")
    def test_books_have_javascript(self, driver):
        books = BooksPage(driver)
        books.open_page("/books")
        books.search("Javascript App")
        titles = books.book_titles()
        self.log.info(f"book_titles_{titles}")
        assert any("JavaScript" in t for t in titles), f"No JS titles in: {titles}"

    @allure.title("Rows-per-page = 5; paginate 1→2 and back 2→1")
    def test_pagination_5_rows_next_prev(self, driver):
        books = BooksPage(driver)
        books.open_page("/books")
        with (soft_assertions()):
            assert_that(books.current_page_num()).is_equal_to("1")
            assert_that(books.total_book_pages()).is_equal_to("1")
            books.set_rows_per_page(5)
            assert_that(books.current_page_num()).is_equal_to("1")
            assert_that(books.total_book_pages()).is_equal_to("2")
            books.go_next_page()
            assert_that(books.current_page_num()).is_equal_to("2")
            assert_that(books.total_book_pages()).is_equal_to("2")
            books.go_previous_page()
            assert_that(books.current_page_num()).is_equal_to("1")
            assert_that(books.total_book_pages()).is_equal_to("2")
