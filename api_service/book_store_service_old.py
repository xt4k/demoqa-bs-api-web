"""BookStore service wrapper over DemoQA endpoints.
Domain-centric helpers for catalog and user shelf operations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import allure
from requests import Response, Session

from api_client.config_old import ConfigLoader
from api_client.http_client import HttpClient

StatusSpec = Union[int, Sequence[int], set]


class BookStoreService(HttpClient):
    """Service layer for DemoQA BookStore API.

    Responsibilities:
      - Catalog queries (list/get).
      - Shelf management for a user (add/replace/delete/clear).
      - Reuse of HttpClient verbs, auth, and retries.

    Notes:
      - Allure step annotations only; no reporting calls inside methods.
    """

    def __init__(
        self,
        *,
        api_base: Optional[str] = None,
        config_dir: str | Path = "config",
        timeout: float = 10.0,
        is_auth: bool = True,
        session: Optional[Session] = None,
    ) -> None:
        """Initialize service using config or explicit base URL."""
        if api_base is None:
            cfg = ConfigLoader(Path(config_dir)).load()
            super().__init__(api_base=cfg.env.api_base, timeout=timeout, session=session)
            self._cfg = cfg
            if is_auth:
                self.refresh_auth_from_config()
        else:
            super().__init__(api_base=api_base, timeout=timeout, session=session)

    @classmethod
    def adopt(cls, http: HttpClient, *, auto_auth: bool = False) -> "BookStoreService":
        """Adopt an existing HttpClient (shared session, same base)."""
        srv = cls(api_base=http.base, timeout=http.timeout, session=http.s, is_auth=False)
        srv._owns_session = False
        srv._cfg = getattr(http, "_cfg", None)
        srv._token = getattr(http, "_token", None)
        if auto_auth and srv._cfg:
            srv.refresh_auth_from_config()
        return srv

    # ----- catalog -----
    @allure.step("BookStore: List books")
    def list_books(self, *, expect: StatusSpec = 200) -> List[Dict[str, Any]]:
        """Return list of books from catalog."""
        r = self.get("/BookStore/v1/Books", expected_status_code=expect)
        return r.json().get("books", [])

    @allure.step("BookStore: Get book {isbn}")
    def get_book(self, isbn: str, *, expect: StatusSpec = 200) -> Dict[str, Any]:
        """Return single book by ISBN."""
        r = self.get("/BookStore/v1/Book", payload={"ISBN": isbn}, expected_status_code=expect)
        return r.json()

    # ----- user shelf (Bearer required) -----
    @allure.step("BookStore: Add book {isbn} to user {user_id}")
    def add_book_to_user(self, user_id: str, isbn: str, *, token: Optional[str] = None,
                         expect: StatusSpec = 201) -> Response:
        """Add a book to user's shelf; returns raw Response."""
        body = {"userId": user_id, "collectionOfIsbns": [{"isbn": isbn}]}
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.post("/BookStore/v1/Books", payload=body, headers=headers, expected_status_code=expect)

    @allure.step("BookStore: Replace user {user_id} book {old_isbn} → {new_isbn}")
    def replace_user_book(self, user_id: str, old_isbn: str, new_isbn: str, *, token: Optional[str] = None,
                          expect: StatusSpec = 200) -> Response:
        """Replace a book on user's shelf with a new ISBN; returns raw Response."""
        body = {"userId": user_id, "isbn": old_isbn}
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.put(f"/BookStore/v1/Books/{new_isbn}", payload=body, headers=headers, expected_status_code=expect)

    @allure.step("BookStore: Delete user {user_id} book {isbn}")
    def delete_user_book(self, user_id: str, isbn: str, *, token: Optional[str] = None,
                         expect: StatusSpec = 204) -> Response:
        """Delete a specific book from user's shelf; returns raw Response."""
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.delete("/BookStore/v1/Book", payload={"isbn": isbn, "userId": user_id}, headers=headers,
                           expected_status_code=expect)

    @allure.step("BookStore: Clear all books for user {user_id}")
    def clear_user_books(self, user_id: str, *, token: Optional[str] = None, expect: StatusSpec = 204) -> Response:
        """Remove all books from user's shelf; returns raw Response."""
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.delete(f"/BookStore/v1/Books?UserId={user_id}", headers=headers, expected_status_code=expect)
