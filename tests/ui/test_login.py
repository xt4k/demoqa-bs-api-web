import allure
import pytest
from assertpy import soft_assertions, assert_that


from core.ui.page_objects.login_page import LoginPage
from core.ui.page_objects.profile_page import ProfilePage
from core.util.html_report.decorators import html_title, html_sub_suite, html_feature
from tests.ui.base_test import BaseTest

@html_sub_suite("Endpoint 'BookStore' functional testing")
@html_feature("Endpoint 'BookStore' happy-path validation")
@allure.epic("Python_ecosystem_automation_testing")
@allure.suite("DemoQA_UI_testing")
@allure.sub_suite("DemoQA site Login page UI testing")
@allure.feature("Login page UI test set")
@allure.story("Verify Login functionality by UI testing")
@allure.label("owner_name", "Other AQA")
@allure.tag("Functional", "Login", "UI")
@allure.severity(allure.severity_level.CRITICAL)
@allure.link("https://some.example.com/", name="Website")
@allure.issue("SOME_JIRA_LINK-6-1-2-5")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.slow
@pytest.mark.login
class TestLoginPage(BaseTest):

    @allure.title("Login → Profile (positive)")
    def test_ui_login(self, driver, ui_creds):
        user_name, pwd, _ = ui_creds
        login_page = LoginPage(driver)
        login_page.open_page("/login")
        profile_page = login_page.login(user_name, pwd)

        with (soft_assertions()):
            assert_that(profile_page.logged_user_name()).is_equal_to(user_name)
            assert_that(profile_page.log_out_btn_text()).is_equal_to("Log out")
            assert_that(profile_page.url_contains("/profile")).is_true()

    @allure.title("Logout from Profile → back to Login")
    def test_ui_login_logout(self, driver, ui_creds):
        user_name, pwd, _ = ui_creds
        login_page = LoginPage(driver)
        login_page.open_page("/login")
        profile_page = login_page.login(user_name, pwd)
        with (soft_assertions()):
            assert_that(profile_page.logged_user_name()).is_equal_to(user_name)
            assert_that(profile_page.log_out_btn_text()).is_equal_to("Log out")
            assert_that(profile_page.url_contains("/profile")).is_true()

        login_page = profile_page.logout()
        with (soft_assertions()):
            assert_that(login_page.url_contains("/login")).is_true()
            assert_that(login_page.user_name_default()).contains("UserName")
            assert_that(login_page.password_default()).contains("Password")

    @allure.title("Logout from Profile → back to Login")
    @html_title("Logout from Profile → back to Login")
    def test_api_login_ui_logout(self, driver):
        profile_page = self.open_page_with_auth_cookies(driver=driver, page_cls=ProfilePage, path="/profile")
        with (soft_assertions()):
            assert_that(profile_page.log_out_btn_text()).is_equal_to("Log out")
            assert_that(profile_page.url_contains("/profile")).is_true()

        login_page = profile_page.logout()
        with (soft_assertions()):
            assert_that(login_page.url_contains("/login")).is_true()
            assert_that(login_page.user_name_default()).contains("UserName")
            assert_that(login_page.password_default()).contains("Password")
