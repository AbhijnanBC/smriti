"""
Structured logging setup.
Reads level from config — not hardcoded.
"""

import logging
import structlog
from pathlib import Path

from smriti.core.paths import LOG_DIR
from smriti.core.config import get_config


def setup_logging() -> None:
    """Configure structured logging from config."""
    config = get_config()
    level = config["logging"]["level"]

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "smriti.log"

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """Return a named structlog logger."""
    return structlog.get_logger(name)