"""Account service: thin wrapper over HttpClient."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Union

import allure
from requests import Response, Session

from api_client.http_client import HttpClient

StatusSpec = Union[int, Sequence[int], set]


class AccountService(HttpClient):
    """Service layer for DemoQA Account API (no extra config/validation)."""

    def __init__(self, *, is_auth: bool = False, session: Optional[Session] = None) -> None:
        super().__init__(is_auth=is_auth, session=session)

    @allure.step("Account: Create user")
    def create_user(self, body: Dict[str, Any], expect: StatusSpec = 201) -> Response:
        return self.post("/Account/v1/User", payload=body, expected_status_code=expect)

    @allure.step("Account: Generate token for {username}")
    def generate_token(self, username: str, password: str, *, expect: StatusSpec = 200) -> str:
        r = self.post("/Account/v1/GenerateToken", payload={"userName": username, "password": password},
                      expected_status_code=expect)
        token = (r.json() or {}).get("token", "")
        if not token:
            raise AssertionError(f"Token not returned: {r.text[:300]}")
        return token

    @allure.step("Account: Generate token for {body}")
    def generate_token(self, body: Dict[str, Any]) -> str:
        r = self.post("/Account/v1/GenerateToken", payload=body, expected_status_code=200)
        token = (r.json() or {}).get("token", "")
        if not token:
            raise AssertionError(f"Token not returned: {r.text[:300]}")
        return token

    @allure.step("Account: Get token")
    def get_token(self, body: Dict[str, Any], expect: StatusSpec = 200) -> Response:
        return self.post("/Account/v1/GenerateToken", payload=body, expected_status_code=expect)

    @allure.step("Account: Check authorization for {username}")
    def is_authorized(self, username: str, password: str, *, expect: StatusSpec = 200) -> bool:
        r = self.post("/Account/v1/Authorized", payload={"userName": username, "password": password},
                      expected_status_code=expect)
        return bool(r.json())

    @allure.step("Account: Get user {user_id}")
    def get_user(self, user_id: str, *, token: Optional[str] = None, expect: StatusSpec = 200) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}"} if token else None
        r = self.get(f"/Account/v1/User/{user_id}", headers=headers, expected_status_code=expect)
        return r.json()

    @allure.step("Account: Delete user {user_id}")
    def delete_user(self, user_id: str, *, token: Optional[str] = None, expect: StatusSpec = (200, 204)) -> Response:
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.delete(f"/Account/v1/User/{user_id}", headers=headers, expected_status_code=expect)
