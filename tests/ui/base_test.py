from __future__ import annotations

from typing import Type, TypeVar
from urllib.parse import urlsplit

import allure
from selenium.webdriver.remote.webdriver import WebDriver

from core.api.services.account_service import AccountService
from core.config.config import ConfigLoader
from core.logging import Logger
from core.ui.page_objects.base_page import BasePage

TPage = TypeVar("TPage", bound=BasePage)


class BaseTest:
    """Base class for UI tests with helpers for authenticated navigation via cookies."""

    log = Logger.get_logger("Test", prefix="ui")

    @allure.step("Open page with auth by api and cookies")
    def open_page_with_auth_cookies(self, driver: WebDriver, page_cls: Type[TPage], path: str) -> TPage:
        """
        Log in user via API, inject auth cookies into the browser and return page object.

        Args:
            driver: Selenium WebDriver instance.
            creds: Tuple with (user_name, password).
            page_cls: Page object class to instantiate (e.g. ProfilePage).

        Returns:
            Instance of the requested page class opened in authenticated state.
        """
        cfg = ConfigLoader().load()
        payload = {"userName": cfg.ui_user_name, "password": cfg.ui_user_password}
        token = AccountService().generate_token(payload, expect=200)
        ui_url = cfg.web_url
        driver.get(ui_url + "/images/Toolsqa.jpg")
        driver.delete_all_cookies()

        cookie_base = {"path": "/", "Expires": "Session"}
        self.log.info(f"_____cookie_base__{cookie_base}")

        driver.add_cookie({**cookie_base, "name": "token", "value": token})
        driver.add_cookie({**cookie_base, "name": "userName", "value": cfg.ui_user_name})
        driver.add_cookie({**cookie_base, "name": "userID", "value": cfg.ui_user_id})
        driver.add_cookie({**cookie_base, "name": "expires", "value": "2025-11-25T23%3A55%3A57"})

        page: TPage = page_cls(driver)
        page.open_page(path=path)
        return page
