import uuid
import pytest
import allure

from core.api.services.book_store_service import BookStoreService

from assertpy import assert_that, soft_assertions


pytestmark = [pytest.mark.api, pytest.mark.book]


@allure.epic("BookStore")
@allure.suite("Negative")
class TestBookStoreNegative:
    @allure.title("GET /BookStore/v1/Book — invalid ISBN")
    def test_get_book_invalid_isbn(self, book_store_service: BookStoreService):
        # get_book returns dict; allow 400/404 by passing expect set
        r_body = book_store_service.get_book("0000000000", expect={400, 404})
        print("r_body[message]"+r_body["message"])
        with soft_assertions():
            assert_that(r_body).is_instance_of(dict)
            assert_that(r_body).contains_key("message")
            assert_that(r_body["message"]).contains("ISBN")


    @allure.title("POST /BookStore/v1/Books — invalid ISBN")
    def test_add_book_invalid_isbn(self, book_store_service: BookStoreService, user_id: str):
        r = book_store_service.add_book_to_user(user_id, "0000000000", expect={400, 404})
        assert r.status_code in (400, 404)
        body = r.json()
        assert "message" in body

    @allure.title("POST /BookStore/v1/Books — unauthorized (no Bearer)")
    def test_add_book_unauthorized(self, user_id: str):
        # Build a BookStoreService without auto-auth (token is missing)
        unauth = BookStoreService(is_auth=False)
        isbn = unauth.list_books()[0]["isbn"]
        r = unauth.add_book_to_user(user_id, isbn, expect={401, 403})
        assert r.status_code in (401, 403)

    @allure.title("PUT /BookStore/v1/Books/{ISBN} — replace with missing old ISBN")
    def test_replace_user_book_not_owned(self, book_store_service: BookStoreService, user_id: str):
        catalog = book_store_service.list_books()
        # ensure shelf is empty
        book_store_service.clear_user_books(user_id, expect={204, 200})
        old_isbn = catalog[0]["isbn"]      # not owned yet
        new_isbn = catalog[1]["isbn"]
        r = book_store_service.replace_user_book(user_id, old_isbn, new_isbn, expect={400, 404})
        assert r.status_code in (400, 404)

    @allure.title("PUT /BookStore/v1/Books/{ISBN} — invalid new ISBN")
    def test_replace_user_book_invalid_new_isbn(self, book_store_service: BookStoreService, user_id: str):
        book_store_service.clear_user_books(user_id, expect={204, 200})
        any_isbn = book_store_service.list_books()[0]["isbn"]
        book_store_service.add_book_to_user(user_id, any_isbn)
        r = book_store_service.replace_user_book(user_id, any_isbn, "0000000000", expect={400, 404})
        assert r.status_code in (400, 404)

    @allure.title("DELETE /BookStore/v1/Book — delete not owned ISBN")
    def test_delete_user_book_not_owned(self, book_store_service: BookStoreService, user_id: str):
        book_store_service.clear_user_books(user_id, expect={204, 200})
        isbn = book_store_service.list_books()[0]["isbn"]
        r = book_store_service.delete_user_book(user_id, isbn, expect={400, 404})
        assert r.status_code in (400, 404)

    @allure.title("DELETE /BookStore/v1/Books — wrong userId")
    def test_clear_user_books_wrong_user(self, book_store_service: BookStoreService):
        fake_user = str(uuid.uuid4())
        r = book_store_service.clear_user_books(fake_user, expect={400, 401, 404})
        assert r.status_code in (400, 401, 404)
