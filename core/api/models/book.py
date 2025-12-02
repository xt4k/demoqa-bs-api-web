from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class Book:
    isbn: str
    title: Optional[str] = None
    subTitle: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
