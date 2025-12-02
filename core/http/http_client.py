"""HTTP client: single source of truth for config & auth; Allure steps; logging; requests-hook installed in conftest."""

from __future__ import annotations

import logging
import threading
from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union, Set, Dict

import allure
import requests
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.api.models.user import UserRequest
from core.config.config import ConfigLoader, RunCfg
from core.providers.data_generator import generate_user_request
from core.util.html_report.decorators import html_step
from core.util.logging import Logger

StatusSpec = Union[int, Sequence[int], Set[int]]


def _mask_headers(headers: Mapping[str, str]) -> dict:
    return {k: ("***" if k.lower() in {"authorization", "proxy-authorization"} else v)
            for k, v in (headers or {}).items()}


def _shorten(s: str, n: int = 500) -> str:
    return s if len(s) <= n else s[:n] + "...<truncated>"


def _as_set(spec: Optional[StatusSpec]) -> Set[int]:
    if spec is None:
        return set()
    if isinstance(spec, int):
        return {spec}
    return set(spec)


class HttpClient:
    _CFG_SINGLETON: RunCfg | None = None
    _BOOT_LOCK = threading.Lock()

    _cfg: Optional[RunCfg] = None
    _token: Optional[str] = None
    _owns_session: bool = True

    def __init__(
            self,
            *,
            cfg: RunCfg | None = None,
            api_base: str | None = None,
            timeout: float = 10.0,
            is_auth: bool = False,
            session: Session | None = None,
            default_headers: Optional[Mapping[str, str]] = None,
            retries: int = 3,
            backoff_factor: float = 0.3,
            status_forcelist: Sequence[int] = (429, 500, 502, 503, 504),
            logger: Optional[logging.Logger] = None,
    ) -> None:
        self.log = logger or Logger.get_logger("HttpClient", prefix="HTTP")

        if cfg is not None:
            self._cfg = cfg
        else:
            self._cfg = self._bootstrap_cfg()

        self.base = (api_base or self.cfg.api_uri).rstrip("/")
        self.timeout = float(timeout)
        self.s: Session = session or requests.Session()
        self._owns_session = session is None

        # defaults
        self.s.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        if default_headers:
            self.s.headers.update(default_headers)

        # retries
        retry = Retry(
            total=retries, connect=retries, read=retries, backoff_factor=backoff_factor,
            status_forcelist=tuple(status_forcelist),
            allowed_methods=frozenset({"GET", "HEAD", "OPTIONS", "DELETE", "PUT"}),
            raise_on_status=False, respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.s.mount("http://", adapter)
        self.s.mount("https://", adapter)

        self.log.info(f"Initialized base={self.base}, timeout={self.timeout}s, authenticated={is_auth}")
        if is_auth:
            self.authenticate_default()

    # ---------- config ----------
    @classmethod
    def _bootstrap_cfg(cls) -> RunCfg:
        if cls._CFG_SINGLETON is None:
            with cls._BOOT_LOCK:
                if cls._CFG_SINGLETON is None:
                    cls._CFG_SINGLETON = ConfigLoader().load()
        return cls._CFG_SINGLETON

    @property
    def cfg(self) -> RunCfg:
        if not self._cfg:
            raise RuntimeError("Config not loaded. HttpClient was not initialized correctly.")
        return self._cfg

    # ---------- auth ----------
    @allure.step("set Bearer token")
    def set_bearer(self, token: str) -> None:
        self._token = token
        self.s.headers.update({"Authorization": f"Bearer {token}"})
        self.log.info("Authorization header set (Bearer ***)")

    @allure.step("clear Bearer token")
    def clear_bearer(self) -> None:
        self.s.headers.pop("Authorization", None)
        self._token = None
        self.log.info("Authorization header cleared")

    @allure.step("authenticate for default user")
    def authenticate_default(self) -> "HttpClient":
        self.log.info(f"Acquiring token for default user '{self.cfg.api_user_name}'")

        user_request = generate_user_request(userName=self.cfg.api_user_name, password=self.cfg.api_user_password)
        token = self._generate_token(user_request)
        self.set_bearer(token)
        self.log.info("Token for default user acquired successfully")
        return self

    @html_step("Base http client: Return generated token")
    @allure.step("Base http client: Return generated token")
    def _generate_token(self, body: UserRequest) -> str:
        r = self.get_generate_token_response(body)
        token = (r.json() or {}).get("token")
        if not token:
            self.log.error("Token was not returned by API")
            raise AssertionError(f"Token not returned: {_shorten(r.text)}")
        return token

    @html_step("Base http client: Get generate token response")
    @allure.step("Base http client: Get generate token response")
    def get_generate_token_response(self, body: Dict[str, Any] | UserRequest, expect: StatusSpec = 200) -> Response:
        payload = body.to_dict() if isinstance(body, UserRequest) else body
        return self.post("/Account/v1/GenerateToken", payload=payload, expected_status_code=expect)

    # ---------- low-level ----------
    @allure.step("send {method} request to {endpoint}")
    def request(
            self,
            method: str,
            endpoint: str,
            *,
            params: Optional[Mapping[str, Any]] = None,
            json: Optional[Any] = None,
            data: Optional[Union[str, bytes]] = None,
            headers: Optional[Mapping[str, str]] = None,
            expected_status_code: Optional[StatusSpec] = None,
            timeout: Optional[float] = None,
    ) -> Response:
        url = f"{self.base}{endpoint}"
        req_headers: MutableMapping[str, str] = {}
        if headers:
            req_headers.update(headers)

        self.log.info(f"→ {method.upper()} {url}")
        if params:
            self.log.debug(f"  params={params}")
        if json is not None:
            self.log.debug(f"  json={_shorten(str(json))}")
        if data is not None:
            self.log.debug(f"  data(len)={len(data) if isinstance(data, (bytes, bytearray)) else len(str(data))}")
        self.log.debug(f"  req_headers={_mask_headers(req_headers)}")

        resp = self.s.request(
            method=method.upper(), url=url, params=params, json=json, data=data,
            headers=req_headers or None, timeout=float(self.timeout if timeout is None else timeout),
        )

        self.log.info(f"← {resp.status_code} {method.upper()} {url} elapsed={getattr(resp, 'elapsed', None)}")
        if expected_status_code is not None:
            allowed = _as_set(expected_status_code)
            if resp.status_code not in allowed:
                try:
                    preview = _shorten(str(resp.json()))
                except Exception:
                    preview = _shorten(resp.text)
                self.log.error(f"Unexpected status {resp.status_code}; expected={sorted(allowed)}; body={preview}")
        return resp

    # ---------- convenience verbs ----------
    @html_step("send POST request to endpoint")
    @allure.step("send POST request to {endpoint}")
    def post(self, endpoint: str, payload: Optional[Any] = None, data_obj: Optional[Any] = None,
             headers: Optional[Mapping[str, str]] = None,
             expected_status_code: Union[int, Sequence[int], Set[int], None] = 200) -> Response:
        return self.request("POST", endpoint, json=payload, data=data_obj, headers=headers,
                            expected_status_code=expected_status_code)

    @allure.step("send GET request to {endpoint}")
    def get(self, endpoint: str, payload: Optional[Mapping[str, Any]] = None,
            headers: Optional[Mapping[str, str]] = None,
            expected_status_code: Union[int, Sequence[int], Set[int], None] = 200) -> Response:
        return self.request("GET", endpoint, params=payload, headers=headers, expected_status_code=expected_status_code)

    @allure.step("send PUT request to {endpoint}")
    def put(self, endpoint: str, payload: Optional[Any] = None,
            headers: Optional[Mapping[str, str]] = None,
            expected_status_code: Union[int, Sequence[int], Set[int], None] = 200) -> Response:
        return self.request("PUT", endpoint, json=payload, headers=headers, expected_status_code=expected_status_code)

    @allure.step("send DELETE request to {endpoint}")
    def delete(self, endpoint: str, params=None, token: str | None = None,
               expected_status_code: Union[int, Sequence[int], Set[int], None] = 204) -> Response:
        if token:
            headers = ({"Authorization": f"Bearer {token}"})
        else:
            headers = self.s.headers
        return self.request("DELETE", endpoint, params=params, headers=headers,
                            expected_status_code=expected_status_code)

    # ---------- lifecycle ----------
    def close(self) -> None:
        if self._owns_session:
            self.s.close()
            self.log.info("Session closed")

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
