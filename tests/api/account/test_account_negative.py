import allure
import pytest
from assertpy import assert_that, soft_assertions

from core.api.clients.account_client import AccountClient
from core.api.services.account_service import AccountService
from core.providers.data_generator import generate_user_request_dict
from core.util.html_report.html_report_decorator import html_sub_suite, html_feature, html_title
from tests.ui.base_test import BaseTest

@html_sub_suite("Endpoint 'Account' negative testing")
@html_feature("Endpoint 'Account' negative flow validation")
@allure.epic("Python_ecosystem_automation_testing")
@allure.suite("DemoQA_API_testing")
@allure.sub_suite("Endpoint 'Account' negative testing")
@allure.feature("Endpoint 'Account' negative flow validation")
@allure.story("Verify endpoint `unhappy-path` functionality")
@allure.label("owner_name", "Yuriy L.")
@allure.tag("Functional", "negative", "Unhappy path")
@allure.severity(allure.severity_level.CRITICAL)
@allure.link("https://some.example.com/", name="Website")
@allure.issue("SOME_JIRA_LINK-442211")
@pytest.mark.account
@pytest.mark.api
class TestAccountEndpointNegative(BaseTest):
    @allure.testcase("TMS_LINK-121")
    @html_title("Verify POST `/Account/v1/GenerateToken` endpoint `Generate token` - get token by wrong pass")
    @allure.title("Verify POST `/Account/v1/GenerateToken` endpoint `Generate token` - get token by wrong pass")
    def test_get_user_token_bad_pass(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        account_service_auth.create_user(create_user_dict)
        create_user_dict["password"] = "123"
        r = account_service_auth._client.generate_token_request(body=create_user_dict)
        with soft_assertions():
            assert_that(r.status_code).is_equal_to(200)
            assert_that(r.json().get("status")).is_equal_to("Failed")
            assert_that(r.json().get("result")).is_equal_to("User authorization failed.")

    @allure.testcase("TMS_LINK-122")
    @html_title("Verify POST `/Account/v1/GenerateToken` endpoint `Generate token` - get token by wrong username")
    @allure.title("Verify POST `/Account/v1/GenerateToken` endpoint `Generate token` - get token by wrong username")
    def test_get_user_token_bad_name(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        account_service_auth.create_user(create_user_dict)
        create_user_dict["userName"] = "abcd_12345@@"
        r = account_service_auth._client.generate_token_request(body=create_user_dict)
        with soft_assertions():
            assert_that(r.status_code).is_equal_to(200)
            assert_that(r.json().get("status")).is_equal_to("Failed")
            assert_that(r.json().get("result")).is_equal_to("User authorization failed.")

    @allure.testcase("TMS_LINK-123")
    @html_title("Verify POST `/Account/v1/User` endpoint (`create user`) for create user with same credentials")
    @allure.title("Verify POST `/Account/v1/User` endpoint (`create user`) for create user with same credentials")
    def test_create_user_with_existed_username(self, account_service: AccountService):
        create_user_dict = generate_user_request_dict()
        account_service.create_user(create_user_dict)
        r = account_service._client.create_user_request(create_user_dict)
        self.log.info(f"\ncreated user response {r.json()}\n")
        with soft_assertions():
            assert_that(r.status_code).is_equal_to(406)
            assert_that(r.json().get("message")).is_equal_to("User exists!")

    @allure.testcase("TMS_LINK-124")
    @html_title("Verify `GET /Account/v1/User/{UUID}` endpoint (`Get User`) for bad user_id")
    @allure.title("Verify `GET /Account/v1/User/{UUID}` endpoint (`Get User`) for bad user_id")
    def test_get_user_bad_user_id(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        create_user_response = account_service_auth.create_user(create_user_dict)
        self.log.info(f"\ncreate_user_response {create_user_response}\n")
        usr_id = create_user_response.get("userID") + "1a"
        token = account_service_auth.generate_token(create_user_dict)
        r = account_service_auth._client.get_user_response(usr_id, token=token, expect=401)
        self.log.info(f"\nget user response {r.json()}\n")
        with soft_assertions():
            assert_that(r.status_code).is_equal_to(401)
            assert_that(r.json().get("message")).is_equal_to("User not found!")

    @allure.testcase("TMS_LINK-125")
    @html_title("Verify POST `/Account/v1/Authorized` endpoint (`Authorized`) for non-authorized user")
    @allure.title("Verify POST `/Account/v1/Authorized` endpoint (`Authorized`) for non-authorized user")
    def test_authorized_for_non_authorized_user(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        account_service_auth.create_user(create_user_dict)
        r = account_service_auth._client.is_authorized_request(create_user_dict)
        assert_that(r.status_code).is_equal_to(200)
        assert_that(r.text).described_as(f"Expected 'false', got '{r.text}'").is_in("false")

    @allure.testcase("TMS_LINK-126")
    @html_title("Verify POST `/Account/v1/Authorized` endpoint (`Authorized`) for bad username")
    @allure.title("Verify POST `/Account/v1/Authorized` endpoint (`Authorized`) for bad username")
    def test_authorized_bad_user_name(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        account_service_auth.create_user(create_user_dict)
        create_user_dict["userName"] = "abcd_12345@@"
        r = account_service_auth._client.is_authorized_request(create_user_dict)
        with soft_assertions():
            assert_that(r.status_code).is_equal_to(404)
            assert_that(r.json().get("message")).is_equal_to("User not found!")

    @allure.testcase("TMS_LINK-127")
    @html_title("Verify POST `/Account/v1/Authorized` endpoint (`Authorized`) for bad password")
    @allure.title("Verify POST `/Account/v1/Authorized` endpoint (`Authorized`) for bad password")
    def test_authorized_bad_password(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        account_service_auth.create_user(create_user_dict)
        create_user_dict["password"] = "ab_123"
        r = account_service_auth._client.is_authorized_request(create_user_dict)
        with soft_assertions():
            assert_that(r.status_code).is_equal_to(404)
            assert_that(r.json().get("message")).is_equal_to("User not found!")

    @allure.testcase("TMS_LINK-128")
    @html_title("Verify DELETE /Account/v1/User/{UUID} endpoint (`Delete user`) bad user_id")
    @allure.title("Verify DELETE /Account/v1/User/{UUID} endpoint (`Delete user`) bad user_id")
    def test_delete_user_bad_user_id(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        self.log.info(f"\ncreate_user_dict {create_user_dict}\n")
        create_user_response = account_service_auth.create_user(create_user_dict)
        self.log.info(f"\ncreate_user_response {create_user_response}\n")
        usr_id = create_user_response.get("userID") + "1q"
        token = account_service_auth.generate_token(create_user_dict)
        r = account_service_auth._client.delete_user_request(usr_id, token=token, expect=200)
        self.log.info(f"\ndelete_user_response {r.json()}\n")
        with soft_assertions():
            assert_that(r.status_code).is_equal_to(200)
            assert_that(r.json().get("message")).is_equal_to("User Id not correct!")
