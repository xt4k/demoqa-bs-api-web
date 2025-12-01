"""Account service: thin wrapper over HttpClient."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Union

import allure
from requests import Response, Session

from core.api.clients.account_client import AccountClient
from core.util.html_report.html_report_decorator import html_step

StatusSpec = Union[int, Sequence[int], set]


class AccountService(AccountClient):
    """Service layer for DemoQA Account API (no extra config/validation)."""

    def __init__(self, *, is_auth: bool = False, session: Optional[Session] = None) -> None:
        super().__init__(is_auth=is_auth, session=session)

    @html_step("Account: Create user")
    @allure.step("Account: Create user")
    def create_user(self, body: Dict[str, Any], expect: StatusSpec = 201) -> Dict[str, Any]:
        return self.create_user_request(body, expect=expect).json()

    @html_step("Account: Generate token")
    @allure.step("Account: Generate token for {body}")
    def generate_token(self, body: Dict[str, Any], expect: StatusSpec = 200) -> str:
        r = self.generate_token_request(body, expect=expect)
        token = (r.json() or {}).get("token", "")
        if not token:
            raise AssertionError(f"Token not returned: {r.text[:300]}")
        return token

    @html_step("Account: Get user")
    @allure.step("Account: Get user {user_id}")
    def get_user(self, user_id: str, *, token: Optional[str] = None, expect: StatusSpec = 200) -> Dict[str, Any]:
        r = self.get_user_response(user_id, token=token, expect=expect)
        return r.json()

    @html_step("Account: Delete user")
    @allure.step("Account: Delete user {user_id}")
    def delete_user(self, user_id: str, *, token: Optional[str] = None, expect: StatusSpec = (200, 204)) -> Response:
        return self.delete_user_request(user_id=user_id, expect=expect, token=token)

    @html_step("Account: Check authorization")
    @allure.step("Account: Check authorization for {body}")
    def is_authorized(self, body: Dict[str, Any], expect: StatusSpec = 200) -> bool:
        return bool(self.is_authorized_request(body, expect=expect).text)
