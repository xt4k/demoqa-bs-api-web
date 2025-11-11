from __future__ import annotations
from utils.config_loader import load_config

CFG = load_config()

BASE_URL: str = CFG.base_url
API_BASE: str = CFG.api_base
ACCOUNT_PREFIX: str = "/Account/v1"
BOOKSTORE_PREFIX: str = "/BookStore/v1"
DEFAULT_TIMEOUT: int = 10

# Optional static creds (might be empty -> tests will create temp users)
STATIC_LOGIN: str = CFG.login
STATIC_PASSWORD: str = CFG.password
