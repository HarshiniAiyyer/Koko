from __future__ import annotations

"""Exports clean public interfaces:

from .cleaning import clean_text, normalize_whitespace, strip_markdown
from .loggers import get_logger
from .helpers import (
    generate_id,
    safe_get,
    flatten_list,
    pretty_json,
)
No logic — just convenience."""

"""
Shared utility helpers for the core AI system.

This package provides:
- Text cleaning utilities
- Logging configuration and helpers
- General-purpose helper functions
"""

from app.core.utils.cleaning import (
    clean_text,
    normalize_whitespace,
    strip_markdown,
    extract_plain_text,
    safe_lower,
)
from app.core.utils.loggers import (
    get_logger,
    configure_global_logging,
    silence_external_loggers,
    log_debug_payload,
)
from app.core.utils.helpers import (
    generate_id,
    safe_get,
    flatten_list,
    pretty_json,
    chunk_text,
    ensure_str,
)

__all__ = [
    # cleaning
    "clean_text",
    "normalize_whitespace",
    "strip_markdown",
    "extract_plain_text",
    "safe_lower",
    # logging
    "get_logger",
    "configure_global_logging",
    "silence_external_loggers",
    "log_debug_payload",
    # helpers
    "generate_id",
    "safe_get",
    "flatten_list",
    "pretty_json",
    "chunk_text",
    "ensure_str",
]
