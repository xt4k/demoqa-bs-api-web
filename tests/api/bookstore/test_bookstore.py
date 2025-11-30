import allure
import pytest
from assertpy import assert_that, soft_assertions

from core.api.services.account_service import AccountService
from core.api.services.book_store_service import BookStoreService
from core.config.config import RunCfg
from core.providers.data_generator import generate_user_request_dict
from core.reporting.html_report_decorator import html_sub_suite, html_feature, html_title
from tests.ui.base_test import BaseTest


@html_sub_suite("Endpoint 'BookStore' functional testing")
@html_feature("Endpoint 'BookStore' happy-path validation")
@allure.epic("Python_ecosystem_automation_testing")
@allure.suite("DemoQA_API_testing")
@allure.sub_suite("Endpoint 'BookStore' functional testing")
@allure.feature("Endpoint 'BookStore' happy-path validation")
@allure.story("Verify endpoint `happy-path`")
@allure.label("owner_name", "Other AQA")
@allure.tag("Functional", "positive", "Happy path")
@allure.severity(allure.severity_level.CRITICAL)
@allure.link("https://some.example.com/", name="Website")
@allure.issue("SOME_JIRA_LINK-2-3-4-5")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.book
@pytest.mark.api
class TestBookStoreEndpoint(BaseTest):
    @html_title("GET /BookStore/v1/Books — list catalog")
    @allure.title("GET /BookStore/v1/Books — list catalog")
    @allure.testcase("TMS_LINK-BS-1-1")
    def test_list_books(self, book_store_service: BookStoreService):
        r = book_store_service.list_books()
        with soft_assertions():
            assert_that(len(r)).described_as("Books list should not be empty").is_greater_than(0)
            assert_that(r).described_as("Response should contain books list").is_instance_of(list)
            assert_that(r[0].get("isbn")).described_as("Any book must contain ISBN").is_not_none()

    @html_title("DELETE /BookStore/v1/Book — delete a single book from user")
    @allure.title("DELETE /BookStore/v1/Book — delete a single book from user")
    @allure.testcase("TMS_LINK-BS-1-2")
    def test_delete_user_books(self, book_store_service: BookStoreService, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        self.log.info(f"\ncreate_user_dict {create_user_dict}\n")
        create_user_response = account_service_auth.create_user(create_user_dict)
        self.log.info(f"\ncreate_user_response {create_user_response}\n")
        user_id = create_user_response.get("userID")
        token = account_service_auth.generate_token(create_user_dict)
        r = book_store_service.delete_user_books(user_id, token=token, expect=204)
        self.log.info(f"\ndelete_user_books {r} sc {r.status_code}\n")
        assert r.status_code in (200, 204)

    @html_title("POST /BookStore/v1/Books — add a book to user with Book ISBN")
    @allure.title("POST /BookStore/v1/Books — add a book to user with Book ISBN")
    @allure.testcase("TMS_LINK-BS-1-3")
    def test_add_book_to_user_shelf(self, env_info: RunCfg, book_store_service_auth: BookStoreService):
        user_id = env_info.api_user_id
        books_list = book_store_service_auth.list_books()
        self.log.info(f"books_list {books_list}")
        isbn0 = book_store_service_auth.list_books()[0].get("isbn")
        self.log.info(f"isbn0 {isbn0} user_loaded:{env_info.api_user_name}")
        book_store_service_auth.delete_user_books(user_id, expect=204)
        r = book_store_service_auth.add_book_to_user(user_id=user_id, isbn=isbn0)
        self.log.info(f"add_book_response {r}")
        with soft_assertions():
            assert_that(len(r)).described_as("Books list should not be empty").is_greater_than(0)
            assert_that(r.get("books")).described_as("books list should be list").is_instance_of(list)
            assert_that(r.get("books")[0].get("isbn")).described_as("Any book must contain ISBN").is_equal_to(isbn0)
