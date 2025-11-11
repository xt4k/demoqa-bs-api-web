import logging

from tests.base_test import BaseTest
import allure
import pytest
from api_service.book_store_service import BookStoreService

pytestmark = pytest.mark.api


@pytest.mark.book
@pytest.mark.api

@allure.epic("API_Autotesting")
@allure.suite("API_Functionality")
@allure.feature("Happy paths validation")
@allure.story("Check BookStore Endpoints")
@allure.label("owner_name", "Yuriy L.")
@allure.tag("Functional", "positive","Happy paths")
@allure.title("Check BookStore Endpoints")
@allure.severity(allure.severity_level.CRITICAL)
@allure.testcase("TMS_LINK-123456")
@allure.link("https://some.example.com/", name="Website")
@allure.issue("SOME_JIRA_LINK-123")
class TestBookStore(BaseTest):

    @allure.title("GET /BookStore/v1/Books — list catalog")
    def test_list_books(self, book_store_service: BookStoreService):
        r = book_store_service.list_books()
        first= r.__getitem__(0)
        logging.info(f"first book {first}")

        assert isinstance(r, list)
        assert len(r) > 0
        assert r.__getitem__(0).get("isbn") is not None
