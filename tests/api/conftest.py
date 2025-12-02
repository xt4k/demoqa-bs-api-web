from __future__ import annotations

import contextlib
from typing import Any, Generator

import allure
import pytest

from core.api.services.account_service import AccountService
from core.api.services.book_store_service import BookStoreService
from core.providers.data_generator import generate_user_request
from core.util.logging import Logger

log = Logger.get_logger("conftest", prefix="api_test_folder")


@pytest.fixture(scope="function")
@allure.step("Authenticate default user via AccountService")
def account_service_auth(account_service: AccountService) -> AccountService:
    """Return AccountService authenticated with default user from config."""
    account_service._client.authenticate_default()
    return account_service


@pytest.fixture(scope="function")
@allure.step("Authenticate default user via AccountService")
def book_store_service_auth(book_store_service: BookStoreService) -> BookStoreService:
    book_store_service._client.authenticate_default()
    return book_store_service


@pytest.fixture()
def user_id(account_service: AccountService) -> Generator[Any, Any, None]:
    """
    Create a fresh DemoQA user for BookStore tests and clean it up afterwards.
    """
    # Arrange: create user with random valid credentials
    user_request = generate_user_request()
    response = account_service._client.create_user_request(user_request)
    body = response.json()

    uid = body["userID"]

    yield uid

    # Teardown: best-effort delete user, ignore errors if already removed
    with contextlib.suppress(Exception):
        account_service.delete_user(uid)
