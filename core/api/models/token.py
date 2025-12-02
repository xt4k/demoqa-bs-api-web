from dataclasses import dataclass, asdict
from typing import Dict, Any

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TokenDto:
    token: str
    expires: str
    status: str
    result: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
