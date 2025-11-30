# tests/support/demoqa_flows.py
from __future__ import annotations

import contextlib
import os
from typing import Any, Dict, Tuple

import allure

from core.api.services.account_service import AccountService
from core.api.services.book_store_service import BookStoreService
from core.providers.data_generator import generate_user_request_dict

UserDict = Dict[str, Any]


@allure.step("DemoQA: Create user via /Account/v1/User")
def create_demo_user(account_service: AccountService) -> UserDict:
    """Create a new DemoQA user with random valid credentials."""
    body = generate_user_request_dict()
    response_json = account_service.create_user(body)
    user_id = response_json["userID"]

    return {
        "username": body["userName"],
        "password": body["password"],
        "userId": user_id,
    }


@allure.step("DemoQA: Login user via /Account/v1/Login")
def login_demo_user(account_service: AccountService, user: UserDict) -> UserDict:
    """Login DemoQA user and attach token/expires."""
    login_body = {
        "userName": user["username"],
        "password": user["password"],
    }
    # AccountService inherits HttpClient.post()
    resp = account_service.post(
        "/Account/v1/Login",
        payload=login_body,
        expected_status_code=200,
    )
    data = resp.json()

    user["userId"] = data.get("userId", user.get("userId"))
    user["token"] = data["token"]
    user["expires"] = data["expires"]
    return user


@allure.step("DemoQA: Create and login temporary user")
def create_and_login_temp_user(account_service: AccountService) -> UserDict:
    """Create a random user and login it in one step."""
    user = create_demo_user(account_service)
    return login_demo_user(account_service, user)


@allure.step("DemoQA: Ensure test user from env or create temporary")
def ensure_test_user(account_service: AccountService) -> Tuple[UserDict, bool]:
    """
    Try to login DEMOQA_USER/DEMOQA_PASS from env,
    otherwise create a temporary user.

    Returns (user_dict, needs_cleanup).
    """
    env_user = os.getenv("DEMOQA_USER")
    env_pass = os.getenv("DEMOQA_PASS")

    if env_user and env_pass:
        user: UserDict = {"username": env_user, "password": env_pass}
        user = login_demo_user(account_service, user)
        return user, False

    user = create_and_login_temp_user(account_service)
    return user, True


@allure.step("DemoQA: Cleanup user (books + account)")
def cleanup_demo_user(
    account_service: AccountService,
    book_store_service: BookStoreService,
    user: UserDict,
) -> None:
    """Best-effort cleanup: delete all books and then delete the user."""
    user_id = user.get("userId")
    token = user.get("token")

    if not user_id or not token:
        return

    with contextlib.suppress(Exception):
        book_store_service.delete_user_books(user_id, token=token)

    with contextlib.suppress(Exception):
        account_service.delete_user(user_id, token=token)
