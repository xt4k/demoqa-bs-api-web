"""BookStore service: thin wrapper over HttpClient."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import allure
from requests import Session, Response

from core.api.clients.book_store_client import BookStoreClient

StatusSpec = Union[int, Sequence[int], set]


class BookStoreService(BookStoreClient):
    """High-level operations for DemoQA BookStore API (no extra config/validation)."""

    def __init__(self, *, is_auth: bool = False, session: Optional[Session] = None) -> None:
        super().__init__(is_auth=is_auth, session=session)

    @allure.step("BookStore: List books")
    def list_books(self, *, expect: StatusSpec = 200) -> List[Dict[str, Any]]:
        r = self.get("/BookStore/v1/Books", expected_status_code=expect)
        books = r.json().get("books", [])
        self.log.info(f"Books total={len(books)}; first={(books[0].get('title') if books else None)}")
        return books

    @allure.step("BookStore: Get book {isbn}")
    def get_book(self, isbn: str, *, expect: StatusSpec = 200) -> Dict[str, Any]:
        r = self.get("/BookStore/v1/Book", payload={"ISBN": isbn}, expected_status_code=expect)
        return r.json()

    @allure.step("BookStore: Delete books for user {user_id}")
    def delete_user_books(self, user_id: str, token: str, expect: StatusSpec = 200) -> Response:
        return self.delete_books_request(user_id=user_id, token=token,expect= expect)
