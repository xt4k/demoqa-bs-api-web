import pytest
import allure

from api_service.book_store_service import BookStoreService
from api_service.account_service import AccountService


pytestmark = [pytest.mark.api, pytest.mark.book]


@allure.epic("BookStore")
@allure.suite("Positive")
class TestBookStorePositive:
    @allure.title("GET /BookStore/v1/Books — list catalog")
    def test_list_books(self, book_store_service: BookStoreService):
        books = book_store_service.list_books()
        assert isinstance(books, list)
        assert books and "isbn" in books[0]

    @allure.title("GET /BookStore/v1/Book — get book by ISBN")
    def test_get_book_by_isbn(self, book_store_service: BookStoreService):
        books = book_store_service.list_books()
        isbn = books[0]["isbn"]
        book = book_store_service.get_book(isbn)
        assert book["isbn"] == isbn
        assert book.get("title")

    @allure.title("POST /BookStore/v1/Books — add a book to user")
    def test_add_book_to_user(self, book_store_service: BookStoreService, account_service: AccountService, user_id: str):
        # ensure clean shelf
        book_store_service.clear_user_books(user_id, expect={204, 200})
        # choose an ISBN
        isbn = book_store_service.list_books()[0]["isbn"]

        r = book_store_service.add_book_to_user(user_id, isbn)
        assert r.status_code in (200, 201)

        user = account_service.get_user(user_id)
        assert any(b["isbn"] == isbn for b in user.get("books", []))

    @allure.title("PUT /BookStore/v1/Books/{ISBN} — replace user's book")
    def test_replace_user_book(self, book_store_service: BookStoreService, account_service: AccountService, user_id: str):
        # prepare: clean and add first book
        catalog = book_store_service.list_books()
        assert len(catalog) >= 2, "Catalog must contain at least 2 books"
        old_isbn, new_isbn = catalog[0]["isbn"], catalog[1]["isbn"]

        book_store_service.clear_user_books(user_id, expect={204, 200})
        book_store_service.add_book_to_user(user_id, old_isbn)

        r = book_store_service.replace_user_book(user_id, old_isbn, new_isbn)
        assert r.status_code == 200

        user = account_service.get_user(user_id)
        isbns = [b["isbn"] for b in user.get("books", [])]
        assert new_isbn in isbns and old_isbn not in isbns

    @allure.title("DELETE /BookStore/v1/Book — delete a single book from user")
    def test_delete_user_book(self, book_store_service: BookStoreService, account_service: AccountService, user_id: str):
        book_store_service.clear_user_books(user_id, expect={204, 200})
        isbn = book_store_service.list_books()[0]["isbn"]
        book_store_service.add_book_to_user(user_id, isbn)

        r = book_store_service.delete_user_book(user_id, isbn)
        assert r.status_code == 204

        user = account_service.get_user(user_id)
        assert all(b["isbn"] != isbn for b in user.get("books", []))

    @allure.title("DELETE /BookStore/v1/Books — clear all user's books")
    def test_clear_user_books(self, book_store_service: BookStoreService, account_service: AccountService, user_id: str):
        # add two books
        catalog = book_store_service.list_books()
        book_store_service.add_book_to_user(user_id, catalog[0]["isbn"])
        book_store_service.add_book_to_user(user_id, catalog[1]["isbn"])

        r = book_store_service.clear_user_books(user_id)
        assert r.status_code in (204, 200)

        user = account_service.get_user(user_id)
        assert user.get("books") in ([], None)
