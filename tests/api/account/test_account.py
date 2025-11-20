import allure
import pytest
from assertpy import assert_that, soft_assertions

from core.api.services.account_service import AccountService
from core.providers.data_generator import generate_user_request_dict
from tests.ui.base_test import BaseTest


@allure.epic("Python_ecosystem_automation_testing")
@allure.suite("DemoQA_API_testing")
@allure.sub_suite("Endpoint 'Account' functional testing")
@allure.feature("Endpoint 'Account' happy-path validation")
@allure.story("Verify endpoint `happy-path`")
@allure.label("owner_name", "Yuriy L.")
@allure.tag("Functional", "positive", "Happy path")
@allure.title("Test set `Account` endpoint")
@allure.severity(allure.severity_level.CRITICAL)
@allure.testcase("TMS_LINK-1112233")
@allure.link("https://some.example.com/", name="Website")
@allure.issue("SOME_JIRA_LINK-332211")
@pytest.mark.account
@pytest.mark.api
class TestAccountEndpoint(BaseTest):

    @allure.title("Verify POST `/Account/v1/GenerateToken` endpoint `Generate token` functionality")
    def test_get_user_token(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        account_service_auth.create_user(create_user_dict)
        r = account_service_auth.generate_token_request(body=create_user_dict)
        assert r.status_code == 200
        assert r.json().get("status") == "Success"
        assert r.json().get("result") == "User authorized successfully."
        assert r.json().get("token") is not None

    @allure.title("Verify POST `/Account/v1/User` endpoint (`create user`) functionality")
    def test_create_user(self, account_service_auth: AccountService):
        r = account_service_auth.create_user_request(generate_user_request_dict())
        self.log.info(f"\ncreated user response {r.json()}\n")
        with soft_assertions():
            assert_that(r.status_code).is_equal_to(201)
            assert_that(r.json().get("userID")).is_not_none()

    @allure.title("Verify `GET /Account/v1/User/{UUID}` endpoint (`Get User`) functionality")
    def test_get_user(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        create_user_response = account_service_auth.create_user(create_user_dict)
        self.log.info(f"\ncreate_user_response {create_user_response}\n")
        user_id = create_user_response.get("userID")
        token = account_service_auth.generate_token(create_user_dict)
        r_dict = account_service_auth.get_user(user_id, token=token)
        self.log.info(f"\nget user response {r_dict}\n")
        with soft_assertions():
            assert_that(r_dict.get("username")).is_equal_to(create_user_dict.get("userName"))
            assert_that(r_dict.get("books")).is_instance_of(list)

    @allure.title("Verify POST `/Account/v1/Authorized` endpoint (`Authorized`) functionality")
    def test_authorized(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        account_service_auth.create_user(create_user_dict)
        account_service_auth.generate_token(create_user_dict)
        r = account_service_auth.is_authorized_request(create_user_dict)
        with (soft_assertions()):
            assert_that(r.status_code).is_equal_to(200)
            assert_that(r.text) \
                .described_as(f"Expected 'true', got '{r.text}'") \
                .is_in("true")

    @allure.title("Verify DELETE /Account/v1/User/{UUID} endpoint (`Delete user`) functionality")
    def test_delete_user(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        self.log.info(f"\ncreate_user_dict {create_user_dict}\n")
        create_user_response = account_service_auth.create_user(create_user_dict)
        self.log.info(f"\ncreate_user_response {create_user_response}\n")
        user_id = create_user_response.get("userID")
        token = account_service_auth.generate_token(create_user_dict)
        response_delete = account_service_auth.delete_user(user_id, token=token)
        self.log.info(f"\ndelete_user_response {response_delete}\n")
        assert_that(response_delete.status_code).is_equal_to(204)
        response_get_deleted = account_service_auth.get_user_response(user_id, token=token, expect=401)
        self.log.info(f"\nget_deleted_user {response_get_deleted}\n")
        with (soft_assertions()):
            assert_that(response_get_deleted.status_code).is_equal_to(401)
            assert_that(response_get_deleted.json().get("message")).is_equal_to("User not found!")
