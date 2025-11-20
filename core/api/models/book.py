from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Book:
    isbn: str
    title: Optional[str] = None
    subTitle: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
