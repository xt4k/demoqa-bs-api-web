# conftest.py
from __future__ import annotations

import allure
import pytest

from api_service.account_service import AccountService
from utils.logger import Logger

log = Logger.get_logger("Conftest", prefix="TEST")


@pytest.fixture(scope="function")
@allure.step("Authenticate default user via AccountService")
def account_service_auth(account_service: AccountService) -> AccountService:
    """Return AccountService authenticated with default user from config."""
    return  account_service.authenticate_default()

