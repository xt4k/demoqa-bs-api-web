import allure
import pytest
from assertpy import assert_that, soft_assertions

from core.api.services.account_service import AccountService
from core.providers.data_generator import generate_user_request_dict, generate_user_request
from core.util.html_report.decorators import html_sub_suite, html_feature, html_title
from tests.ui.base_test import BaseTest


@html_sub_suite("Endpoint 'Account' functional testing")
@html_feature("Endpoint 'Account' happy-path validation")
@allure.epic("Python_ecosystem_automation_testing")
@allure.suite("DemoQA_API_testing")
@allure.sub_suite("Endpoint 'Account' functional testing")
@allure.feature("Endpoint 'Account' happy-path validation")
@allure.story("Verify endpoint `happy-path`")
@allure.label("owner_name", "Yuriy L.")
@allure.tag("Functional", "positive", "Happy path")
@allure.severity(allure.severity_level.BLOCKER)
@allure.link("https://some.example.com/", name="Website")
@allure.issue("SOME_JIRA_LINK-1-2-3-4")
@pytest.mark.account
@pytest.mark.api
@pytest.mark.happy_path
class TestAccountEndpoint(BaseTest):
    @html_title("Verify POST `/Account/v1/GenerateToken` endpoint `Generate token` functionality")
    @allure.title("Verify POST `/Account/v1/GenerateToken` endpoint `Generate token` functionality")
    @allure.testcase("TMS_LINK-A-1-1")
    def test_get_user_token(self, account_service_auth: AccountService):
        user_request = generate_user_request()
        account_service_auth.create_user(user_request)
        r = account_service_auth._client.generate_token_request(body=user_request)
        with (soft_assertions()):
            assert_that(r.status_code).is_equal_to(200)
            assert_that(r.json().get("status")).is_equal_to("Success")
            assert_that(r.json().get("result")).is_equal_to("User authorized successfully.")
            assert_that(r.json().get("status")).is_not_none()

    @html_title("Verify POST `/Account/v1/User` endpoint (`create user`) functionality (with request body as dict)")
    @allure.title("Verify POST `/Account/v1/User` endpoint (`create user`) functionality (with request body as dict)")
    @allure.testcase("TMS_LINK-A-1-2")
    def test_create_user_dict(self, account_service_auth: AccountService):
        r = account_service_auth._client.create_user_request(generate_user_request_dict())
        self.log.info(f"\ncreated user response {r.json()}\n")
        with soft_assertions():
            assert_that(r.status_code).is_equal_to(201)
            assert_that(r.json().get("userID")).is_not_none()

    @html_title("Verify POST `/Account/v1/User` endpoint (`create user`) functionality")
    @allure.title("Verify POST `/Account/v1/User` endpoint (`create user`) functionality")
    @allure.testcase("TMS_LINK-A-1-3")
    def test_create_user(self, account_service_auth: AccountService):
        r = account_service_auth._client.create_user_request(generate_user_request())
        self.log.info(f"\ncreated user response {r.json()}\n")
        with soft_assertions():
            assert_that(r.status_code).is_equal_to(201)
            assert_that(r.json().get("userID")).is_not_none()

    @html_title("Verify `GET /Account/v1/User/{UUID}` endpoint (`Get User`) functionality")
    @allure.title("Verify `GET /Account/v1/User/{UUID}` endpoint (`Get User`) functionality")
    @allure.testcase("TMS_LINK-A-1-4")
    def test_get_user(self, account_service_auth: AccountService):
        user_request = generate_user_request()
        create_user_response = account_service_auth.create_user(user_request)
        self.log.info(f"\ncreate_user_response {create_user_response}\n")
        user_id = create_user_response.get("userID")
        token = account_service_auth.generate_token(user_request)
        r_dict = account_service_auth.get_user(user_id, token=token)
        self.log.info(f"\nget user response {r_dict}\n")
        with soft_assertions():
            assert_that(r_dict.get("username")).is_equal_to(user_request.userName)
            assert_that(r_dict.get("books")).is_instance_of(list)

    @html_title("Verify POST `/Account/v1/Authorized` endpoint (`Authorized`) functionality")
    @allure.title("Verify POST `/Account/v1/Authorized` endpoint (`Authorized`) functionality")
    @allure.testcase("TMS_LINK-A-1-5")
    def test_authorized(self, account_service_auth: AccountService):
        user_request = generate_user_request()
        account_service_auth.create_user(user_request)
        account_service_auth.generate_token(user_request)
        r = account_service_auth._client.is_authorized_request(user_request)
        with (soft_assertions()):
            assert_that(r.status_code).is_equal_to(200)
            assert_that(r.text).described_as(f"Expected 'true', got '{r.text}'").is_in("true")

    @html_title("Verify DELETE /Account/v1/User/{UUID} endpoint (`Delete user`) functionality")
    @allure.title("Verify DELETE /Account/v1/User/{UUID} endpoint (`Delete user`) functionality")
    @allure.testcase("TMS_LINK-A-1-6")
    def test_delete_user(self, account_service_auth: AccountService):
        user_request = generate_user_request()
        self.log.info(f"user_request {user_request}")
        create_user_response = account_service_auth.create_user(user_request)
        self.log.info(f"\ncreate_user_response {create_user_response}\n")
        user_id = create_user_response.get("userID")
        token = account_service_auth.generate_token(user_request)
        response_delete = account_service_auth.delete_user(user_id, token=token)
        self.log.info(f"\ndelete_user_response {response_delete}\n")
        assert_that(response_delete.status_code).is_equal_to(204)
        response_get_deleted = account_service_auth._client.get_user_response(user_id, token=token, expect=401)
        self.log.info(f"\nget_deleted_user {response_get_deleted}\n")
        with (soft_assertions()):
            assert_that(response_get_deleted.status_code).is_equal_to(401)
            assert_that(response_get_deleted.json().get("message")).is_equal_to("User not found!")
