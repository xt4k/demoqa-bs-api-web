from __future__ import annotations

import json
from typing import Any, Dict, Mapping, Optional

import allure
from requests import PreparedRequest, Response, Session

from core.util.logging import Logger


class AllureApiLogger:
    """Attach cURL / Request & Response JSON / Meta to Allure via Requests response hook."""

    def __init__(self, *, max_body_len: int = 200_000) -> None:
        self.log = Logger.get_logger("AllureApiLogger", prefix="ALOG")
        self.max_body_len = max_body_len

    # -------- helpers --------
    @staticmethod
    def _is_json(ct: Optional[str]) -> bool:
        if not ct:
            return False
        ct = ct.split(";", 1)[0].strip().lower()
        return ct.startswith("application/json") or ct.startswith("text/json") or ct.startswith("application/problem+json")

    def _shorten(self, s: str) -> str:
        return s if len(s) <= self.max_body_len else (s[: self.max_body_len] + "...<truncated>")

    @staticmethod
    def _mask_headers(headers: Mapping[str, str]) -> Dict[str, str]:
        return {k: ("***" if k.lower() in {"authorization", "proxy-authorization"} else v) for k, v in headers.items()}

    @classmethod
    def _curl(cls, prep: PreparedRequest, data_preview: Optional[str]) -> str:
        parts = [f"curl -X {prep.method} '{prep.url}'"]
        for k, v in cls._mask_headers(dict(prep.headers)).items():
            parts.append(f"-H '{k}: {v}'")
        if data_preview:
            parts.append(f"--data-raw '{data_preview}'")
        return " \\\n  ".join(parts)

    @staticmethod
    def _pretty(x: Any) -> str:
        try:
            if isinstance(x, (bytes, bytearray)):
                x = x.decode("utf-8", errors="replace")
            if isinstance(x, str):
                x = json.loads(x)
            return json.dumps(x, ensure_ascii=False, indent=2, sort_keys=True)
        except Exception:
            return x.decode("utf-8", errors="replace") if isinstance(x, (bytes, bytearray)) else str(x)

    # -------- hook --------
    def _on_response(self, resp: Response, *args, **kwargs) -> None:
        """Requests 'response' hook: called for each response."""
        try:
            prep = resp.request  # PreparedRequest
            req_ct = (prep.headers or {}).get("Content-Type")
            body_preview: Optional[str] = None
            if self._is_json(req_ct) and prep.body:
                raw = prep.body if isinstance(prep.body, (bytes, bytearray)) else str(prep.body).encode("utf-8")
                body_preview = self._shorten(self._pretty(raw))

            # cURL
            allure.attach(self._curl(prep, body_preview), name="cURL", attachment_type=allure.attachment_type.TEXT)

            # Request JSON
            if body_preview is not None:
                allure.attach(body_preview, name="Request JSON", attachment_type=allure.attachment_type.JSON)

            # Response Meta
            meta = {
                "status_code": resp.status_code,
                "reason": resp.reason,
                "url": resp.url,
                "headers": self._mask_headers(dict(resp.headers)),
                "elapsed_ms": int(getattr(resp, "elapsed").total_seconds() * 1000) if getattr(resp, "elapsed", None) else None,
            }
            allure.attach(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True),
                          name="Response Meta", attachment_type=allure.attachment_type.JSON)

            # Response JSON
            if self._is_json(resp.headers.get("Content-Type")):
                # ensure content is loaded before pretty-print
                _ = resp.content  # no-op, forces load if stream=True
                allure.attach(self._shorten(self._pretty(resp.text)), name="Response JSON",
                              attachment_type=allure.attachment_type.JSON)
        except Exception as e:
            self.log.debug(f"AllureApiLogger hook failed: {e}")

    # -------- installer --------
    def install(self, session: Session) -> None:
        """Register response hook on a given Session (idempotent)."""
        hooks = session.hooks.get("response") or []
        # avoid installing twice
        if any(getattr(h, "__name__", "") == self._on_response.__name__ for h in hooks):
            return
        session.hooks["response"] = hooks + [self._on_response]
        self.log.info("Allure API logger response hook installed")
