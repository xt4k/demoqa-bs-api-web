"""Account service: thin wrapper over HttpClient."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Union

import allure
from requests import Response, Session

from core.http.http_client import HttpClient

StatusSpec = Union[int, Sequence[int], set]


class BookStoreClient(HttpClient):
    """Service layer for DemoQA Account API (no extra config/validation)."""
    BS_PATH_BOOKS = "/BookStore/v1/Books"

    def __init__(self, *, is_auth: bool = False, session: Optional[Session] = None) -> None:
        super().__init__(is_auth=is_auth, session=session)

    @allure.step("Book_Store: Create book")
    def create_user_request(self, body: Dict[str, Any], expect: StatusSpec=200) -> Response:
        return self.post(self.BS_PATH_BOOKS, payload=body, expected_status_code=expect)

    @allure.step("BookStore: List books request")
    def get_user_response(self, user_id: str, *, token: Optional[str], expect: StatusSpec) -> Response:
        headers = {"Authorization": f"Bearer {token}"}
        return self.get(f"{self.BS_PATH_BOOKS}/{user_id}", headers=headers, expected_status_code=expect)

    @allure.step("Account: Delete user {user_id}")
    def delete_books_request(self, user_id: str, *, token: Optional[str], expect: StatusSpec) -> Response:
        headers = {"Authorization": f"Bearer {token}"}
        param = {"UserId": user_id}
        return self.delete(f"{self.BS_PATH_BOOKS}",param=param, headers=headers, expected_status_code=expect)

