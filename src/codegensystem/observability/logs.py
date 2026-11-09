import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logging(level):
    logger = logging.getLogger("codegensystem")
    logger.setLevel(level)

    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    file = RotatingFileHandler(
        LOG_DIR / "codegensystem.log",
        maxBytes=5_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file.setFormatter(fmt)
    logger.addHandler(file)

    return logger