from __future__ import annotations

from typing import Literal, TYPE_CHECKING

import allure
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.logging import Logger
from .locators.base_page_locators import BasePageLocators as Loc

DEFAULT_TIMEOUT = 10
if TYPE_CHECKING:
    from .login_page import LoginPage


class BasePage:
    """Common base page with shared Selenium actions and waits."""
    log: Logger = Logger().get_logger(prefix="BasePage")

    def __init__(self, driver, timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.base_url = (getattr(driver, "base_url")).rstrip("/")
        self.log.info(f"[PAGE] Initializing {self.__class__.__name__} page.")

    @allure.step("Open page `{path}`")
    def open_page(self, path: str = ""):
        self.log.info(f"Open_page:`{path}`")
        self.driver.get(self.base_url + path)

    def __visible(self, locator) -> Literal[False] | WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click_visible(self, locator) -> BasePage:
        self.__visible(locator).click()
        return BasePage(self.driver, timeout=DEFAULT_TIMEOUT)

    @allure.step("Set text {text} to input element")
    def _type(self, locator, text: str) -> None:
        el = self.__visible(locator)
        el.clear()
        el.send_keys(text)

    @allure.step("Return web element text")
    def get_text(self, locator) -> str:
        return self.__visible(locator).text

    @allure.step("Return web element attribute {attribute}")
    def _get_element_attribute(self, locator, attribute: str) -> str:
        return self.__visible(locator).get_attribute(attribute)

    @allure.step("Return if url contains text {fragment}")
    def url_contains(self, fragment: str) -> bool:
        return self.wait.until(EC.url_contains(fragment))

    @allure.step("Get test from `Log out` button")
    def log_out_btn_text(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(Loc.LOG_OUT_BTN)).text

    @allure.step("Return profile `User Name`")
    def logged_user_name(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(Loc.LOGGED_USER_NAME)).text

    @allure.step("Logout from Profile page")
    def logout(self) -> "LoginPage":
        """Click 'Log out' button and return LoginPage instance."""
        self.__visible(Loc.LOG_OUT_BTN).click()
        from .login_page import LoginPage
        return LoginPage(self.driver)
