"""Runtime config loader (.properties) via configparser + informative logging."""

from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import allure

from core.util.html_report.decorators import html_step
from core.util.logging import Logger


@dataclass(frozen=True)
class RunCfg:
    env_name: str
    api_uri: str
    web_url: str
    db_url: Optional[str]
    api_user_name: str
    api_user_password: str
    api_user_id: Optional[str]
    ui_user_name: str
    ui_user_password: str
    ui_user_id: Optional[str]


class ConfigLoader:
    log = Logger.get_logger("Config", prefix="CONF")

    # <project root> = .../demoqa-bs-api-web
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    CONFIG_DIR: Path = PROJECT_ROOT / "config"

    def __init__(self) -> None:
        self.config_dir = self.CONFIG_DIR

    @html_step("Load configuration from files")
    @allure.step("Load configuration from files")
    def load(self) -> RunCfg:
        self.log.info(f"Loading config from: {self.config_dir.resolve()}")
        common = self._read_flat(self.config_dir / "common.properties", required=True)
        api_user_key = self._req(common, "api_test_user").strip()
        env_key = self._req(common, "test_env").strip()
        ui_user_key = self._req(common, "ui_test_user").strip()
        self.log.info(f"Selected env='{env_key}', api_user='{api_user_key}', ui_user='{ui_user_key}'")

        env_props = self._read_cfg_file("env", env_key)
        api_user_props = self._read_cfg_file("user", api_user_key)
        ui_user_props = self._read_cfg_file("user", ui_user_key)

        cfg = RunCfg(
            env_name=env_key,
            api_uri=self._req(env_props, "api"),
            web_url=self._req(env_props, "ui"),
            db_url=env_props.get("db"),
            api_user_name=self._req(api_user_props, "username"),
            api_user_password=self._req(api_user_props, "password"),
            api_user_id=self._req(api_user_props, "userid"),
            ui_user_name=self._req(ui_user_props, "username"),
            ui_user_password=self._req(ui_user_props, "password"),
            ui_user_id=self._req(ui_user_props, "userid"),
        )

        self.log.info(f"Env '{cfg.env_name}': api={cfg.api_uri} ui={cfg.web_url}")
        self.log.info(f"api_user={cfg.api_user_name}; ui_user={cfg.ui_user_name}")
        return cfg

    # -------- internal --------
    def _read_cfg_file(self, folder: str, file_name: str) -> Dict[str, str]:
        """Read config/<folder>/<key>.properties into a flat dict."""
        prop_file_name = file_name if file_name.endswith(".properties") else f"{file_name}.properties"
        path = self.config_dir / folder / prop_file_name
        if not path.exists():
            raise FileNotFoundError(f"{folder} properties not found: {path}")
        self.log.info(f"Reading {folder} file: {path}")
        return self._read_flat(path, required=True)

    @staticmethod
    @html_step("Load properties file")
    @allure.step("Load properties file")
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
    @html_step("check properties presence")
    @allure.step("check properties presence")
    def _req(mapping: Dict[str, str], key: str) -> str:
        v = mapping.get(key)
        if v is None or str(v).strip() == "":
            raise RuntimeError(f"Missing required key: {key}")
        return str(v).strip()
