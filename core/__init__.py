import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

log_file = Path.home() / ".gitk_config" / "logs" / "gitk.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

file_handler = RotatingFileHandler(
    filename=log_file,
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8",
)

formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.propagate = False
