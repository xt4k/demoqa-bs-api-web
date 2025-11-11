# conftest.py
from __future__ import annotations

from typing import Generator

import allure
import pytest

from api_client.http_client import HttpClient
from api_service.account_service import AccountService
from api_service.book_store_service import BookStoreService
from utils.allure_api_logger import AllureApiLogger
from utils.logger import Logger

log = Logger.get_logger("Conftest", prefix="TEST")


@pytest.fixture(scope="session")
def http_root() -> Generator[HttpClient, None, None]:
    """Single shared HttpClient + install Allure response-hook."""
    http = HttpClient(is_auth=False)  # token off by default
    AllureApiLogger().install(http.s)  # canonical Requests hook

    cfg = http.cfg
    env_info = (
        f"ENV={cfg.env_name}\n"
        f"API_BASE={cfg.api_uri}\n"
        f"WEB_BASE={cfg.web_url}\n"
        f"TEST_USER={cfg.user_name}\n"
        f"USER_ID={cfg.user_id or ''}\n"
    )
    allure.attach(env_info, name="Environment", attachment_type=allure.attachment_type.TEXT)
    log.info(f"ENV loaded: env={cfg.env_name} api={cfg.api_uri} user={cfg.user_name}")
    try:
        yield http
    finally:
        http.close()
        log.info("HttpClient session closed")


@pytest.fixture(scope="session")
@allure.step("Provide AccountService client")
def account_service(http_root: HttpClient) -> AccountService:
    """Thin wrapper over HttpClient, uses shared Session."""
    srv = AccountService(is_auth=False, session=http_root.s)
    log.info("AccountService uses shared HttpClient session")
    return srv


@pytest.fixture(scope="session")
@allure.step("Provide BookStoreService client")
def book_store_service(http_root: HttpClient) -> BookStoreService:
    """Thin wrapper over HttpClient, uses shared Session."""
    srv = BookStoreService(is_auth=False, session=http_root.s)
    log.info("BookStoreService uses shared HttpClient session")
    return srv
