from __future__ import annotations

from typing import Type, TypeVar

import allure
from selenium.webdriver.remote.webdriver import WebDriver

from core.api.services.account_service import AccountService
from core.config.config import ConfigLoader
from core.reporting.html_report_decorator import html_step
from core.util.logging import Logger
from core.providers.data_generator import iso_date_plus_days
from core.ui.page_objects.base_page import BasePage

TPage = TypeVar("TPage", bound=BasePage)


class BaseTest:
    """Base class for UI tests with helpers for authenticated navigation via cookies."""

    log = Logger.get_logger("Test", prefix="ui")

    @html_step("Set DemoQA auth cookies into the current browser session")
    @allure.step("Set DemoQA auth cookies into the current browser session")
    def _set_auth_cookies(self, driver: WebDriver, cfg, token: str) -> None:
        """Set DemoQA auth cookies into the current browser session."""
        next_day = iso_date_plus_days(1)
        self.log.info(f"___tomorrow___{next_day}")

        cookie_base = {"path": "/", "Expires": "Session"}

        cookies = [
            {"name": "token", "value": token},
            {"name": "userName", "value": cfg.ui_user_name},
            {"name": "userID", "value": cfg.ui_user_id},
            {"name": "expires", "value": f"{next_day}T23%3A59%3A59"},
        ]

        for cookie in cookies:
            driver.add_cookie({**cookie_base, **cookie})

    @html_step("Open page with auth by api and cookies")
    @allure.step("Open page with auth by api and cookies")
    def open_page_with_auth_cookies(self, driver: WebDriver, page_cls: Type[TPage], path: str) -> TPage:
        cfg = ConfigLoader().load()
        payload = {"userName": cfg.ui_user_name, "password": cfg.ui_user_password}
        token = AccountService().generate_token(payload, expect=200)

        ui_url = cfg.web_url
        driver.get(ui_url + "/images/Toolsqa.jpg")
        driver.delete_all_cookies()

        self._set_auth_cookies(driver, cfg, token)

        page: TPage = page_cls(driver)
        page.open_page(path=path)
        return page
