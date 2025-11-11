import allure
import pytest

from api_service.account_service import AccountService
from tests.base_test import BaseTest
from utils.data_generator import random_username, generate_password, generate_user_request_dict


@allure.epic("Python_ecosystem_automation_testing")
@allure.suite("DemoQA_API_testing")
@allure.sub_suite("Endpoint 'Account'")
@allure.feature("Endpoint 'Account' validation")
@allure.story("Verify endpoint `happy-path`")
@allure.label("owner_name", "Yuriy L.")
@allure.tag("Functional", "positive","Happy paths")
@allure.title("Test set `Account` endpoint")
@allure.severity(allure.severity_level.CRITICAL)
@allure.testcase("TMS_LINK-1112233")
@allure.link("https://some.example.com/", name="Website")
@allure.issue("SOME_JIRA_LINK-332211")
@pytest.mark.account
@pytest.mark.api
class TestAccountEndpoint(BaseTest):

    @allure.title("Verify `get user token` functionality")
    def test_get_user_token(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        account_service_auth.create_user(create_user_dict)
        r = account_service_auth.get_token(body=create_user_dict)
        assert r.status_code == 200
        assert r.json().get("status") == "Success"

    @allure.title("Verify `create user` functionality")
    def test_create_user(self, account_service_auth: AccountService):
        r = account_service_auth.create_user(generate_user_request_dict())
        self.log.info(f"\ncreated user response {r.json()}\n")
        assert r.status_code == 201
        assert r.json().get("userID") is not None

    @allure.title("Verify `get user` functionality")
    def test_get_user(self, account_service_auth: AccountService):
        create_user_dict = generate_user_request_dict()
        create_user_response = account_service_auth.create_user(create_user_dict)
        userId = create_user_response.json().get("userID")
        token =account_service_auth.generate_token(create_user_dict)
        r = account_service_auth.get_user(userId, token="token")
        self.log.info(f"\nget user response {r}\n")
        assert r.status_code == 201
        assert r.json().get("userID") is not None
