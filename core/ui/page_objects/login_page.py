import allure

from core.ui.page_objects.base_page import BasePage
from .locators.login_page_locators import LoginPageLocators as Loc


class LoginPage(BasePage):

    @allure.step("Login by username {username}")
    def login(self, username: str, password: str) -> BasePage:
        self._type(Loc.USERNAME, username)
        self._type(Loc.PASSWORD, password)
        return self.click_visible(Loc.LOGIN_BTN)

    def error_text(self) -> str:
        return self.get_text(Loc.ERROR_MSG)

    @allure.step("Return default Username field text")
    def user_name_default(self):
        return self._get_element_attribute(Loc.USERNAME, "placeholder")

    @allure.step("Return default password field text")
    def password_default(self):
        return self._get_element_attribute(Loc.PASSWORD, "placeholder")
