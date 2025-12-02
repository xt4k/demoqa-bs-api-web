"""BookStore service: thin wrapper over HttpClient."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Union

import allure
from requests import Response

from core.api.clients.book_store_client import BookStoreClient
from core.api.models.user_book import UserBook
from core.util.html_report.decorators import html_step

StatusSpec = Union[int, Sequence[int], set]


class BookStoreService:
    """High-level operations for DemoQA BookStore API (no extra config/validation)."""

    def __init__(self, *, client: BookStoreClient) -> None:
        self._client: BookStoreClient = client

    @html_step("BookStore: List books")
    @allure.step("BookStore: List books")
    def list_books(self, *, expect: StatusSpec = 200) -> List[Dict[str, Any]]:
        r = self._client.get("/BookStore/v1/Books", expected_status_code=expect)
        books = r.json().get("books")
        self._client.log.info(f"Books total={len(books)}; first={(books[0].get('title') if books else None)}")
        return books

    @html_step("BookStore: Get book")
    @allure.step("BookStore: Get book {isbn}")
    def get_book(self, isbn: str, *, expect: StatusSpec = 200) -> Dict[str, Any]:
        r = self._client.get("/BookStore/v1/Book", payload={"ISBN": isbn}, expected_status_code=expect)
        return r.json()

    @html_step("BookStore: Delete books for user")
    @allure.step("BookStore: Delete books for user {user_id}")
    def delete_user_books(self, user_id: str, token: str | None = None, expect: StatusSpec = 204) -> Response:
        return self._client.delete_books_request(user_id=user_id, token=token, expect=expect)

    @html_step("BookStore: add books for user book shelf")
    @allure.step("BookStore: add books for user {user_id} book shelf")
    def add_book_to_user(self, user_id: str, isbn: str, expect: int = 201):
        body = UserBook.single(user_id=user_id, isbn=isbn).to_payload()
        r = self._client.add_user_book_request(body=body, expect=expect)
        return r.json()
