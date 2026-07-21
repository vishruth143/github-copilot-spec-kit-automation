"""Structured, per-run, secret-redacting logging for the framework.

Each test-execution run gets its own timestamped folder under `output/`;
this module configures a logger that writes into that run's `logs/`
subdirectory as plain, human-readable text, redacting anything that looks
like a secret (Constitution VII, VIII, XI).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

_REDACT_PATTERN = re.compile(r"(PASSWORD|TOKEN|SECRET|KEY)\s*[:=]\s*\S+", re.IGNORECASE)
_REDACTED_VALUE = r"\1=***REDACTED***"

FRAMEWORK_LOGGER_NAME = "framework_core"


class RedactingFilter(logging.Filter):
    """Redacts log messages that look like they contain a secret value."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact `record`'s message in place if it matches a secret pattern."""
        message = record.getMessage()
        redacted = _REDACT_PATTERN.sub(_REDACTED_VALUE, message)
        if redacted != message:
            record.msg = redacted
            record.args = ()
        return True


def configure_run_logger(logs_dir: Path, *, run_log_filename: str = "run.log") -> logging.Logger:
    """Configure and return the root framework logger for one test run.

    Args:
        logs_dir: The run's `output/<timestamp>/logs/` directory.
        run_log_filename: Name of the whole-run structured log file.

    Returns:
        The configured `framework_core` logger instance.

    """
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(FRAMEWORK_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
    )

    file_handler = logging.FileHandler(logs_dir / run_log_filename, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(RedactingFilter())
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger


def get_test_logger(test_name: str) -> logging.Logger:
    """Return a child logger scoped to a specific test name."""
    return logging.getLogger(f"{FRAMEWORK_LOGGER_NAME}.{test_name}")
