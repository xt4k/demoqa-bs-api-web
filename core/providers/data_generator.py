from __future__ import annotations

import datetime
import random
import string

import allure

from core.reporting.html_report_decorator import html_step


def now_suffix() -> str:
    import time
    return str(int(time.time() * 1000))


@allure.step("Generate a random username")
def random_username(prefix: str = "auto_user") -> str:
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{suffix}_{now_suffix()}"


@allure.step("Generate a defined user request dict")
def get_user_request_from_tuple(creds: tuple[str, str]) -> dict:
    return {"userName": creds[0], "password": creds[1]}


@allure.step("Generate a random valid password")
def generate_password() -> str:
    core = "1Aa@"
    tail = ''.join(random.choices(string.ascii_letters + string.digits + "_-", k=9))
    return core + tail


@html_step("Generate a random user request dict")
@allure.step("Generate a random user request dict")
def generate_user_request_dict() -> dict:
    return {"userName": random_username(), "password": generate_password()}


@allure.step("Get a defined delete user books dict")
def get_delete_user_book_dict(user_id: str) -> dict:
    return {"userId": user_id, "message": f"Delete message for user with id:`{user_id}`"}

@html_step("Get a iso-date string with defined day shift")
@allure.step("Get a iso-date string with defined day shift")
def iso_date_plus_days(days: int = 1, base: datetime.datetime | None = None) -> str:
    """
    Return ISO date string (YYYY-MM-DD) for base + days.
    """
    if base is None:
        base = datetime.datetime.now()
    return (base + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
