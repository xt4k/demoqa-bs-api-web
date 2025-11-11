import random
import string

import allure

@allure.step("Generate a random username")
def random_username(prefix: str = "user") -> str:
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{suffix}"

@allure.step("Generate a random valid password")
def generate_password() -> str:
    core = "1Aa@"
    tail = ''.join(random.choices(string.ascii_letters + string.digits + "_-", k=9))
    return core + tail

@allure.step("Generate a random user request dict")
def generate_user_request_dict() -> dict:
    return {"userName": random_username(), "password": generate_password()}
