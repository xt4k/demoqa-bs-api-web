
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class UserDto:
    userName: str
    password: Optional[str]
    discount_type: Optional[str]
    description: Optional[str]
    id: Optional[int] = None

@dataclass_json
@dataclass(frozen=True)
class UserRequest:
    userName: str
    password: str


@dataclass_json
@dataclass(frozen=True)
class UserResponse:
    userID: str
    userName: str
    books: list[int]

