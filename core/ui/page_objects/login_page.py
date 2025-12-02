import allure

from core.ui.page_objects.base_page import BasePage
from core.util.html_report.decorators import html_step
from .locators.login_page_locators import LoginPageLocators as Loc


class LoginPage(BasePage):

    @html_step("Login by username")
    @allure.step("Login by username {username}")
    def login(self, username: str, password: str) -> BasePage:
        self._type(Loc.USERNAME, username)
        self._type(Loc.PASSWORD, password)
        return self.click_visible(Loc.LOGIN_BTN)

    def error_text(self) -> str:
        return self.get_text(Loc.ERROR_MSG)

    @html_step("Return default Username field text")
    @allure.step("Return default Username field text")
    def user_name_default(self):
        return self._get_element_attribute(Loc.USERNAME, "placeholder")

    @html_step("Return default password field text")
    @allure.step("Return default password field text")
    def password_default(self):
        return self._get_element_attribute(Loc.PASSWORD, "placeholder")
