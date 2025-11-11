import logging
from logging import DEBUG
from pathlib import Path


class Logger:
    @staticmethod
    def get_logger(name: str = "TestLogger", prefix: str = "TEST", log_level: int = DEBUG) -> logging.Logger:
        """
        Create (or reuse) a project logger: console + file logs/run_log.log.
        Prefix is included into every log line.
        """
        logger = logging.getLogger(name)
        if logger.handlers:
            return logger
        # project root by walking up until .git or filesystem root
        root_dir = Path(__file__).resolve().parents[1]
        while root_dir != root_dir.parent and not (root_dir / ".git").exists():
            root_dir = root_dir.parent

        logs_dir = root_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / "run_log.log"

        fmt = logging.Formatter(fmt=f"%(asctime)s {prefix} %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)

        logger.setLevel(log_level)
        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.propagate = False
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
