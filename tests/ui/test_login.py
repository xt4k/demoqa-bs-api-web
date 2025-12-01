import allure
from assertpy import soft_assertions, assert_that


from core.ui.page_objects.login_page import LoginPage
from core.ui.page_objects.profile_page import ProfilePage
from core.util.html_report.html_report_decorator import html_title
from tests.ui.base_test import BaseTest


@allure.epic("Login page")
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
