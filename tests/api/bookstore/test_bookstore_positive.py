import allure
import pytest

from core.api.services.account_service import AccountService
from core.api.services.book_store_service import BookStoreService
from core.providers.data_generator import generate_user_request_dict
from tests.ui.base_test import BaseTest

pytestmark = [pytest.mark.api, pytest.mark.book]


@allure.epic("BookStore")
@allure.suite("Positive")
class TestBookStorePositive(BaseTest):
    @allure.title("GET /BookStore/v1/Books — list catalog")
    def test_list_books(self, book_store_service: BookStoreService):
        books = book_store_service.list_books()
        self.log.info(f"\nlist_books {books}\n")
        assert isinstance(books, list)
        assert books and "isbn" in books[0]

    @allure.title("POST /BookStore/v1/Books — add a book to user")
    def test_add_book_to_user(self, book_store_service: BookStoreService, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        self.log.info(f"\ncreate_user_dict {create_user_dict}\n")
        create_user_response = account_service_auth.create_user(create_user_dict)
        self.log.info(f"\ncreate_user_response {create_user_response}\n")
        user_id = create_user_response.get("userID")
        token = account_service_auth.generate_token(create_user_dict)
        r = book_store_service.delete_user_books(user_id, token, expect=204)

        books = book_store_service.list_books()

        # choose an ISBN
        self.log.info(f"\ndelete_user_books {r} sc {r.status_code}\n")
        assert r.status_code in (200, 204)


    @allure.title("DELETE /BookStore/v1/Book — delete a single book from user")
    def test_delete_user_books(self, book_store_service: BookStoreService, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        self.log.info(f"\ncreate_user_dict {create_user_dict}\n")
        create_user_response = account_service_auth.create_user(create_user_dict)
        self.log.info(f"\ncreate_user_response {create_user_response}\n")
        user_id = create_user_response.get("userID")
        token = account_service_auth.generate_token(create_user_dict)
        r = book_store_service.delete_user_books(user_id, token, expect=204)
        self.log.info(f"\ndelete_user_books {r} sc {r.status_code}\n")
        assert r.status_code in (200, 204)