"""Account service: thin wrapper over HttpClient."""

from __future__ import annotations

from typing import Optional, Sequence, Union

import allure
from requests import Response, Session

from core.http.http_client import HttpClient
from core.util.html_report.decorators import html_step

StatusSpec = Union[int, Sequence[int], set]


class BookStoreClient(HttpClient):
    """Service layer for DemoQA BookStore API (no extra config/validation)."""
    BS_PATH_BOOKS = "/BookStore/v1/Books"

    def __init__(self, *, is_auth: bool = False, session: Optional[Session] = None) -> None:
        super().__init__(is_auth=is_auth, session=session)

    @html_step("Book_Store: Add book to shelf")
    @allure.step("Book_Store: Add book to shelf")
    def add_user_book_request(self, body, expect: StatusSpec = 201) -> Response:
        return self.post(self.BS_PATH_BOOKS, payload=body, expected_status_code=expect)

    @html_step("Book_Store: Delete user books")
    @allure.step("Book_Store: Delete user {user_id} books")
    def delete_books_request(self, user_id: str, token: str | None = None, expect: StatusSpec=204) -> Response:
        param = {"UserId": user_id}
        return self.delete(f"{self.BS_PATH_BOOKS}", params=param, token= token, expected_status_code=expect)
