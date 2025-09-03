import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class GitkLogger:

    DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        name: str,
        log_level: int = logging.INFO,
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 3,
    ) -> None:
        self.name = name
        self.log_level = log_level

        self._setup_logger(max_bytes, backup_count)

    def _setup_logger(self, max_bytes: int, backup_count: int) -> None:
        log_dir = Path.home() / ".gitk_config" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "gitk.log"

        self.file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )

        formatter = logging.Formatter(
            fmt=self.DEFAULT_FORMAT, datefmt=self.DEFAULT_DATEFMT
        )
        self.file_handler.setFormatter(formatter)

        self.logger = logging.getLogger(self.name)
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(self.log_level)
