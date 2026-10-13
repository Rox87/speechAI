"""Logging utility for SpeechAI with optional ANSI colored output."""

import logging
import sys
from typing import Optional
from src.core.config import config


class ColoredFormatter(logging.Formatter):
    """Custom logging formatter with ANSI color coding."""

    GREY = "\x1b[38;20m"
    CYAN = "\x1b[36;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + FORMAT + RESET,
        logging.INFO: CYAN + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + FORMAT + RESET,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


def get_logger(name: str = "SpeechAI", level: Optional[str] = None) -> logging.Logger:
    """Get or create a configured logger instance."""
    logger = logging.getLogger(name)
    log_level = getattr(logging, (level or config.log_level).upper(), logging.INFO)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        handler.setFormatter(ColoredFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    return logger


logger = get_logger("SpeechAI")
