"""Runtime config loader (.properties) via configparser + informative logging."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RunCfg:
    env_name: str
    api_uri: str
    web_url: str
    db_url: Optional[str]
    user_name: str
    password: str
    user_id: Optional[str]
