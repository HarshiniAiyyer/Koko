from __future__ import annotations

"""This is where we define structured, colored, timestamped logging for the entire system.

We will not use Python’s default logging mess.
We make a clean wrapper around it.

Logging philosophy:

Debug logs for developers

Info logs for what’s happening in the pipeline

Warning/Error logs that don’t crash the flow

JSON-safe logging for structured logs, if needed

All logs follow the format:

[2025-01-01 12:30:20] [INFO] [orchestrator] Emotion detected: {...}"""

import json
import logging
from typing import Any, Dict, Optional


_DEFAULT_LOG_FORMAT = (
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_global_logging(level: int = logging.INFO) -> None:
    """
    Configure the root logger with a consistent format.

    Should typically be called once at application startup.
    """
    logging.basicConfig(
        level=level,
        format=_DEFAULT_LOG_FORMAT,
        datefmt=_DATE_FORMAT,
    )


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Retrieve a logger with the given name, ensuring it has a single
    StreamHandler attached with the global format.

    Args:
        name: The logger name/module.
        level: Optional explicit log level override.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(_DEFAULT_LOG_FORMAT, datefmt=_DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Avoid passing logs up to the root logger multiple times
    logger.propagate = False

    return logger


def silence_external_loggers() -> None:
    """
    Reduce noise from verbose third-party libraries.

    This can be called in demo environments or tests.
    """
    noisy_loggers = [
        "transformers",
        "urllib3",
        "httpx",
        "qdrant_client",
    ]
    for name in noisy_loggers:
        logging.getLogger(name).setLevel(logging.WARNING)


def log_debug_payload(
    logger: logging.Logger,
    title: str,
    payload: Dict[str, Any],
    level: int = logging.DEBUG,
) -> None:
    """
    Helper to log a JSON payload in a readable way.

    Example log:
        ▶ MEMORY CONTEXT
        {
          "preferences": [...],
          "facts": [...]
        }
    """
    if not logger.isEnabledFor(level):
        return

    try:
        pretty = json.dumps(payload, indent=2, ensure_ascii=False)
    except TypeError:
        # Fallback: non-serializable objects
        pretty = str(payload)

    logger.log(level, f"▶ {title}\n{pretty}")
