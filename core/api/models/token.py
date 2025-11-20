from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TokenDto:
    token: str
    expires: str
    status: str
    result: str
