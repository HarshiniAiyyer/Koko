from __future__ import annotations

"""This module contains lightweight but frequently used text-cleaning utilities that are important for:

preprocessing user messages

memory extraction

avoiding noisy tokens in vector embeddings

cleaning LLM outputs (e.g., removing ``` fences)"""

import re
from typing import Optional


WHITESPACE_RE = re.compile(r"\s+")
MARKDOWN_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
MARKDOWN_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
MARKDOWN_BOLD_RE = re.compile(r"\*\*(.*?)\*\*")
MARKDOWN_ITALIC_RE = re.compile(r"[_*](.*?)[_*]")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
HTML_TAG_RE = re.compile(r"<[^>]+>")
XML_TAG_RE = re.compile(r"</?[A-Za-z0-9_:-]+[^>]*>")
CONTROL_CHARS_RE = re.compile(r"[\u0000-\u001F\u007F]")


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in a string by collapsing runs of whitespace into
    a single space and stripping leading/trailing spaces.

    This is a safe pre-processing step before sending text to an LLM
    or storing in the vector DB.
    """
    if not text:
        return ""
    return WHITESPACE_RE.sub(" ", text).strip()


def strip_markdown(text: str) -> str:
    """
    Remove common Markdown constructs while preserving readable text.

    This is intentionally conservative: the goal is to reduce noise
    rather than produce perfectly clean plain text.
    """
    if not text:
        return ""

    result = text

    # Remove fenced code blocks ```...```
    result = MARKDOWN_FENCE_RE.sub("", result)

    # Inline code `code` → code
    result = MARKDOWN_INLINE_CODE_RE.sub(r"\1", result)

    # Markdown links [label](url) → label
    result = MARKDOWN_LINK_RE.sub(r"\1", result)

    # Bold and italic markers
    result = MARKDOWN_BOLD_RE.sub(r"\1", result)
    result = MARKDOWN_ITALIC_RE.sub(r"\1", result)

    # Blockquotes: remove leading '>' characters
    result = re.sub(r"^\s*>\s?", "", result, flags=re.MULTILINE)

    return result


def _strip_tags(text: str) -> str:
    """
    Remove generic HTML/XML-like tags from text.

    Used when parsing LLM outputs that may contain XML-style structuring
    or markup that shouldn't be embedded.
    """
    if not text:
        return ""
    result = HTML_TAG_RE.sub("", text)
    result = XML_TAG_RE.sub("", result)
    return result


def extract_plain_text(text: str) -> str:
    """
    Convert potentially formatted or tagged text into plain text.

    Operations:
    - Remove control characters
    - Strip Markdown and simple HTML/XML tags
    - Normalize whitespace
    """
    if not text:
        return ""

    result = text
    result = CONTROL_CHARS_RE.sub("", result)
    result = strip_markdown(result)
    result = _strip_tags(result)
    result = normalize_whitespace(result)
    return result


def clean_text(text: str) -> str:
    """
    General-purpose cleaning function used before:
    - memory extraction
    - embedding for vector search
    - emotion analysis

    It:
    - removes control characters
    - strips markdown and simple tags
    - normalizes whitespace
    - keeps punctuation and casing intact
    """
    return extract_plain_text(text)


def safe_lower(text: Optional[str]) -> str:
    """
    Safely lowercase and strip a string.

    Returns an empty string if the input is None or empty.
    """
    if not text:
        return ""
    return text.lower().strip()
