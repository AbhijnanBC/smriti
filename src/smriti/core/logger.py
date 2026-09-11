"""
Structured logging setup.
Reads level from config — not hardcoded.
"""

import logging
import sys

import structlog

from smriti.core.config import get_config
from smriti.core.paths import LOG_DIR


def _utf8_console_stream(stream):
    """
    Return a stream that will not raise UnicodeEncodeError on non-ASCII text.

    On Windows, the console's legacy codepage (e.g. cp1252) cannot encode
    most non-Latin scripts (Kannada, CJK, many symbols). SMRITI processes
    arbitrary user note vaults, so any character a user's notes contain
    must be safely loggable. reconfigure() with errors="backslashreplace"
    keeps a crash from ever happening while still surfacing the original
    bytes in escaped form for debugging.
    """
    try:
        stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):
        pass
    return stream


def setup_logging() -> None:
    """Configure structured logging from config."""
    config = get_config()
    level = config["logging"]["level"]

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "smriti.log"

    # structlog falls back to its own PrintLogger (writing straight to
    # sys.stdout) for any logger created before structlog.configure() runs,
    # or if configure() is skipped entirely — so stdout needs the same
    # crash-proofing as the stderr StreamHandler below.
    _utf8_console_stream(sys.stdout)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(_utf8_console_stream(sys.stderr)),
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
