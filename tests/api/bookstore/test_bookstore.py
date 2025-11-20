import logging

from assertpy import assert_that, soft_assertions
from tests.ui.base_test import BaseTest
import allure
import pytest
from core.api.services.book_store_service import BookStoreService

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
        with soft_assertions():
            assert_that(len(r)).described_as("Books list should not be empty").is_greater_than(0)
            assert_that(r).described_as("Response should contain books list").is_instance_of(list)
            assert_that(r.__getitem__(0).get("isbn")).described_as("Any book must contain ISBN").is_not_none()

