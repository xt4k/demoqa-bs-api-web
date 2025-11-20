# conftest.py
from __future__ import annotations

import contextlib
from typing import Generator

import allure
import pytest

from core.http.http_client import HttpClient
from core.api.services.account_service import AccountService
from core.api.services.book_store_service import BookStoreService
from core.http.hooks.allure import AllureApiLogger
from core.logging import Logger
from core.providers.data_generator import generate_user_request_dict

log = Logger.get_logger("conftest", prefix="api_test")


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
        f"TEST_USER={cfg.api_user_name}\n"
        f"USER_ID={cfg.api_user_id or ''}\n"
    )
    allure.attach(env_info, name="Environment", attachment_type=allure.attachment_type.TEXT)
    log.info(f"ENV loaded: env={cfg.env_name} api={cfg.api_uri} user={cfg.api_user_name}")
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

@pytest.fixture()
def user_id(account_service: AccountService) -> str:
    """
    Create a fresh DemoQA user for BookStore tests and clean it up afterwards.
    """
    # Arrange: create user with random valid credentials
    create_user_dict = generate_user_request_dict()
    response = account_service.create_user_request(create_user_dict)
    body = response.json()

    uid = body["userID"]

    yield uid

    # Teardown: best-effort delete user, ignore errors if already removed
    with contextlib.suppress(Exception):
        account_service.delete_user(uid)
