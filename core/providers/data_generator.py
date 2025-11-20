import random
import string

import allure

@allure.step("Generate a random username")
def random_username(prefix: str = "auto_user") -> str:
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{suffix}_{now_suffix()}"

@allure.step("Generate a random valid password")
def generate_password() -> str:
    core = "1Aa@"
    tail = ''.join(random.choices(string.ascii_letters + string.digits + "_-", k=9))
    return core + tail

@allure.step("Generate a random user request dict")
def generate_user_request_dict() -> dict:
    return {"userName": random_username(), "password": generate_password()}

@allure.step("Generate a defined user request dict")
def get_user_request_from_tuple(creds:tuple[str,str]) -> dict:
    return {"userName": creds[0], "password": creds[1]}

def now_suffix() -> str:
    import time
    return str(int(time.time() * 1000))

def make_username(prefix: str = "auto_user") -> str:
    # username must be unique per test run
    return f"{prefix}_{now_suffix()}"

def valid_password() -> str:
    # DemoQA rules: 8+ chars, upper, lower, digit, special
    return f"Qwe!{now_suffix()}aA1"


@allure.step("Get a defined delete user books dict")
def get_delete_user_book_dict(user_id:str) -> dict:
    return {"userId": user_id, "message": f"Delete message for user with id:`{user_id}`"}
