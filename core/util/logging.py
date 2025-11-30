# core/logging.py
from __future__ import annotations

import logging
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from pathlib import Path
from typing import Optional

# Optional color support on Windows/PyCharm
try:
    from colorama import init as _colorama_init  # pip install colorama
except Exception:  # pragma: no cover
    _colorama_init = None

_LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"
_LOG_FILE_NAME = "run_log.log"


class _ColorFormatter(logging.Formatter):
    """Console formatter that paints log lines depending on level."""
    _RESET = "\033[0m"
    _COLORS = {
        DEBUG: "\033[37m",  # white
        INFO: "\033[37m",  # white
        WARNING: "\033[93m",  # light yellow
        ERROR: "\033[91m",  # light red
        CRITICAL: "\033[1m\033[91m",  # bold light red
    }

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        color = self._COLORS.get(record.levelno, "")
        return f"{color}{msg}{self._RESET}" if color else msg


def _project_root(start: Optional[Path] = None) -> Path:
    """Best effort to find repo root; fall back to CWD."""
    p = (start or Path(__file__)).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


def _build_plain_formatter(prefix: str) -> logging.Formatter:
    fmt = f"%(asctime)s {prefix} %(levelname)s: %(message)s"
    return logging.Formatter(fmt=fmt, datefmt=_LOG_DATE_FMT)


def _build_color_formatter(prefix: str) -> logging.Formatter:
    fmt = f"%(asctime)s {prefix} %(levelname)s: %(message)s"
    return _ColorFormatter(fmt=fmt, datefmt=_LOG_DATE_FMT)


class Logger:
    """
    Centralized logger factory:
      - console (colored) + file 'run_log.log'
      - idempotent (won't add handlers twice)
      - minimal public API (info/warn/error helpers)
    """

    @staticmethod
    def get_logger(
            name: str = "TestLogger",
            prefix: str = "TEST",
            log_level: int = DEBUG,
            use_colors: bool = True,
    ) -> logging.Logger:
        logger = logging.getLogger(name)
        if logger.handlers:
            return logger  # already configured

        if use_colors and _colorama_init:
            _colorama_init(autoreset=True)

        log_path = Path(__file__).resolve().parents[1] / _LOG_FILE_NAME

        # File handler (plain)
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(_build_plain_formatter(prefix))

        # Console handler (colored or plain)
        # ch = logging.StreamHandler()
        import sys
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setFormatter(_build_color_formatter(prefix) if use_colors else _build_plain_formatter(prefix))

        logger.setLevel(log_level)
        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.propagate = False
        logging.captureWarnings(True)

        return logger

    @staticmethod
    def info(logger: logging.Logger, message: str) -> None:
        logger.info(message)

    @staticmethod
    def warn(logger: logging.Logger, message: str) -> None:
        logger.warning(message)

    @staticmethod
    def error(logger: logging.Logger, message: str) -> None:
        logger.error(message)
