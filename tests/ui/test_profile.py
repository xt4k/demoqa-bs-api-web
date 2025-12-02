import allure
import pytest
from assertpy import soft_assertions, assert_that

from core.ui.page_objects.profile_page import ProfilePage
from core.util.html_report.decorators import html_sub_suite, html_feature
from tests.ui.base_test import BaseTest


@html_sub_suite("Endpoint 'BookStore' functional testing")
@html_feature("Endpoint 'BookStore' happy-path validation")
@allure.epic("Python_ecosystem_automation_testing")
@allure.suite("DemoQA_UI_testing")
@allure.sub_suite("DemoQA site Profile page UI testing")
@allure.feature("Profile page UI test set")
@allure.story("Verify Profile functionality by UI testing")
@allure.label("owner_name", "Third AQA")
@allure.tag("Functional", "Profile", "UI")
@allure.severity(allure.severity_level.TRIVIAL)
@allure.link("https://some.example.com/", name="Website")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.slow
@pytest.mark.profile
class TestProfilePage(BaseTest):

    @allure.title("Open Profile when not logged in → should see Login")
    def test_profile_not_logged(self, driver):
        profile_page = ProfilePage(driver)
        profile_page.open_page("/profile")
        not_logged_text = profile_page.not_logged_label_text()
        with (soft_assertions()):
            assert_that(not_logged_text).contains("you are not logged into the Book Store application")
            assert_that(not_logged_text).contains("page to register yourself.")
            assert_that(not_logged_text).contains("login")
            assert_that(profile_page.url_contains("/profile")).is_true()

    @allure.title("Profile shows username for authenticated user")
    def test_profile_authenticated(self, driver):
        profile_page = self.open_page_with_auth_cookies(driver=driver, page_cls=ProfilePage, path="/profile")
        with (soft_assertions()):
            assert_that(profile_page.log_out_btn_text()).is_equal_to("Log out")
            assert_that(profile_page.url_contains("/profile")).is_true()