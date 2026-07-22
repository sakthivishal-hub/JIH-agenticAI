"""
Central logging configuration for OpportunityOS.
"""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": (
                "%(asctime)s | %(levelname)-8s | "
                "%(name)s | %(message)s"
            ),
        },
        "access": {
            "format": (
                "%(asctime)s | %(levelname)-8s | "
                "%(message)s"
            ),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "opportunityos.log",
            "formatter": "default",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}


def setup_logging() -> None:
    """
    Configure application logging.
    """
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.
    """
    return logging.getLogger(name)