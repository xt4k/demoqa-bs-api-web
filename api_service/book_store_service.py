"""BookStore service: thin wrapper over HttpClient."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import allure
from requests import Response, Session

from api_client.http_client import HttpClient

StatusSpec = Union[int, Sequence[int], set]


class BookStoreService(HttpClient):
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
