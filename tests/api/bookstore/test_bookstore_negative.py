import allure
import pytest
from assertpy import assert_that, soft_assertions

from core.api.services.account_service import AccountService
from core.api.services.book_store_service import BookStoreService
from core.config.config import RunCfg
from core.providers.data_generator import generate_user_request_dict, generate_user_request
from core.util.html_report.decorators import html_sub_suite, html_feature, html_title
from tests.ui.base_test import BaseTest

@html_sub_suite("Endpoint 'Account' negative testing")
@html_feature("Endpoint 'Account' negative flow validation")
@allure.epic("Python_ecosystem_automation_testing")
@allure.suite("DemoQA_API_testing")
@allure.sub_suite("Endpoint 'BookStore' negative testing")
@allure.feature("Endpoint 'BookStore' negative flow validation")
@allure.story("Verify endpoint `unhappy-path` functionality")
@allure.label("owner_name", "Other one SDET")
@allure.tag("Functional", "negative", "Unhappy path")
@allure.link("https://some.example.com/", name="Website")
@allure.issue("SOME_JIRA_LINK-3-4-5-6")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.book
@pytest.mark.api
@pytest.mark.negative
class TestBookStoreEndpointNegative(BaseTest):
    @html_title("GET /BookStore/v1/Book — invalid ISBN")
    @allure.title("GET /BookStore/v1/Book — invalid ISBN")
    @allure.testcase("TMS_LINK-BS-2-1")
    def test_get_book_invalid_isbn(self, book_store_service: BookStoreService):
        r_body = book_store_service.get_book("0000000000", expect={400, 404})
        print("r_body[message]" + r_body["message"])
        with soft_assertions():
            assert_that(r_body).is_instance_of(dict)
            assert_that(r_body).contains_key("message")
            assert_that(r_body["message"]).contains("ISBN supplied is not available in Books Collection!")

    @html_title("POST /BookStore/v1/Books/{ISBN} — try to add existed ISBN")
    @allure.title("POST /BookStore/v1/Books/{ISBN} — try to add existed ISBN")
    @allure.testcase("TMS_LINK-BS-2-2")
    def test_add_user_book_again(self, env_info: RunCfg, book_store_service_auth: BookStoreService):
        user_id = env_info.api_user_id
        books_list = book_store_service_auth.list_books()
        self.log.info(f"books_list {books_list}")
        isbn0 = book_store_service_auth.list_books()[0].get("isbn")
        self.log.info(f"isbn0 {isbn0} user_loaded:{env_info.api_user_name}")
        book_store_service_auth.delete_user_books(user_id, expect=204)
        book_store_service_auth.add_book_to_user(user_id=user_id, isbn=isbn0)

        r = book_store_service_auth.add_book_to_user(user_id=user_id, isbn=isbn0, expect=400)
        self.log.info(f"add_book_response {r}")
        with soft_assertions():
            assert_that(r.get("message")).described_as("Error description").contains(
                "ISBN already present in the User's Collection!")
            assert_that(r.get("code")).described_as("books list should be list").is_not_empty()

    @html_title("DELETE /BookStore/v1/Book — delete a single book from user with bad user_id")
    @allure.title("DELETE /BookStore/v1/Book — delete a single book from user with bad user_id")
    @allure.testcase("TMS_LINK-BS-2-3")
    def test_delete_user_books_wrong_id(self, book_store_service: BookStoreService,
                                        account_service_auth: AccountService):
        user_request = generate_user_request()
        self.log.info(f"user_request {user_request}\n")
        create_user_response = account_service_auth.create_user(user_request)
        self.log.info(f"create_user_response {create_user_response}\n")
        token = account_service_auth.generate_token(user_request)
        r = book_store_service.delete_user_books("000", token=token, expect=401)

        self.log.info(f"add_book_response {r}")
        with soft_assertions():
            assert_that(r.json().get("message")).described_as("User id error info").contains("User Id not correct!")
            assert_that(r.json().get("code")).described_as("should be present").is_not_empty()
