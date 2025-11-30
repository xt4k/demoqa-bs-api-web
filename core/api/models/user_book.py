from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class BookRef:
    """Single book reference in BookStore API."""
    isbn: str


@dataclass(frozen=True, slots=True)
class UserBook:
    """Domain model for 'add list of books to user' request."""
    userId: str
    books: tuple[BookRef, ...]

    @classmethod
    def single(cls, user_id: str, isbn: str) -> "UserBook":
        """Convenience factory for a single-book payload."""
        return cls(userId=user_id, books=(BookRef(isbn=isbn),))

    @classmethod
    def from_isbns(cls, user_id: str, isbns: Iterable[str]) -> "UserBook":
        return cls(userId=user_id, books=tuple(BookRef(isbn=i) for i in isbns))

    def to_payload(self) -> dict:
        """Convert to API request body."""
        return {
            "userId": self.userId,
            "collectionOfIsbns": [{"isbn": b.isbn} for b in self.books],
        }