"""Runtime config loader (.properties) via configparser + informative logging."""

from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path
from typing import Dict

from api_client.config import RunCfg
from utils.logger import Logger

log = Logger.get_logger("Config", prefix="CONF")


class ConfigLoader:
    """Load env & user config from a fixed directory (CONFIG_DIR)."""
    CONFIG_DIR: Path = Path("config")  # single source of truth

    def __init__(self) -> None:
        self.config_dir = self.CONFIG_DIR

    def load(self) -> RunCfg:
        log.info(f"Loading config from: {self.config_dir.resolve()}")
        common = self._read_flat(self.config_dir / "common.properties", required=True)
        env_key = self._req(common, "test_env").strip()
        user_key = self._req(common, "test_user").strip()
        log.info(f"Selected env='{env_key}', user='{user_key}'")

        env_props = self._read_cfg_file("env", env_key)
        user_props = self._read_cfg_file("user", user_key)

        cfg = RunCfg(
            env_name=env_key,
            api_uri=self._req(env_props, "api"),
            web_url=self._req(env_props, "ui"),
            db_url=env_props.get("db"),
            user_name=self._req(user_props, "username"),
            password=self._req(user_props, "password"),
            user_id=user_props.get("userId"),
        )
        log.info(
            f"Env '{cfg.env_name}': api={cfg.api_uri} ui={cfg.web_url} "
            f"db={cfg.db_url or '-'}; user={cfg.user_name} id={cfg.user_id or '-'}"
        )
        return cfg

    # -------- internal --------
    def _read_cfg_file(self, folder: str, file_name: str) -> Dict[str, str]:
        """Read config/<folder>/<key>.properties into a flat dict."""
        prop_file_name = file_name if file_name.endswith(".properties") else f"{file_name}.properties"
        path = self.config_dir / folder / prop_file_name
        if not path.exists():
            raise FileNotFoundError(f"{folder} properties not found: {path}")
        log.info(f"Reading {folder} file: {path}")
        return self._read_flat(path, required=True)

    @staticmethod
    def _read_flat(path: Path, *, required: bool = False) -> Dict[str, str]:
        if not path.exists():
            if required:
                raise FileNotFoundError(f"Properties file not found: {path}")
            return {}
        raw = path.read_text(encoding="utf-8")
        cp = ConfigParser(interpolation=None)
        cp.read_string("[root]\n" + raw)  # inject dummy section
        return {k: v for k, v in cp["root"].items()}

    @staticmethod
    def _req(mapping: Dict[str, str], key: str) -> str:
        v = mapping.get(key)
        if v is None or str(v).strip() == "":
            raise RuntimeError(f"Missing required key: {key}")
        return str(v).strip()
