"""Account service: thin wrapper over HttpClient."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Union

import allure
from requests import Response, Session

from core.http.http_client import HttpClient
from core.util.html_report.html_report_decorator import html_step

StatusSpec = Union[int, Sequence[int], set]


class AccountClient(HttpClient):
    """Service layer for DemoQA Account API (no extra config/validation)."""
    ACC_PATH = "/Account/v1"
    ACC_USR_PATH = f"{ACC_PATH}/User"

    def __init__(self, *, is_auth: bool = False, session: Optional[Session] = None) -> None:
        super().__init__(is_auth=is_auth, session=session)

    @html_step("Account: Create user")
    @allure.step("Account: Create user")
    def create_user_request(self, body: Dict[str, Any], expect: StatusSpec=201) -> Response:
        return self.post(self.ACC_USR_PATH, payload=body, expected_status_code=expect)

    @html_step("Account: Generate token for body")
    @allure.step("Account: Generate token for {body}")
    def generate_token_request(self, body: Dict[str, Any],expect: StatusSpec = 200) -> Response:
        return self.post(f"{self.ACC_PATH}/GenerateToken", payload=body, expected_status_code=expect)

    @html_step("Account: Get user user_id")
    @allure.step("Account: Get user {user_id}")
    def get_user_response(self, user_id: str, token: Optional[str], expect: StatusSpec) -> Response:
        headers = {"Authorization": f"Bearer {token}"}
        return self.get(f"{self.ACC_USR_PATH}/{user_id}", headers=headers, expected_status_code=expect)

    @html_step("Account: Delete user user_id")
    @allure.step("Account: Delete user {user_id}")
    def delete_user_request(self, user_id: str, *, token: Optional[str], expect: StatusSpec) -> Response:
        return self.delete(f"{self.ACC_USR_PATH}/{user_id}", token=token, expected_status_code=expect)

    @html_step("Account: Check authorization for body")
    @allure.step("Account: Check authorization for {body}")
    def is_authorized_request(self, body: Dict[str, Any], expect: StatusSpec = 200) -> Response:
        return self.post(f"{self.ACC_PATH}/Authorized", payload=body, expected_status_code=expect)
