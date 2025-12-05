from __future__ import annotations

"""This module contains general-purpose helper utilities used across the project."""

import json
import textwrap
import uuid
from typing import Any, Dict, Iterable, List, Sequence, TypeVar


T = TypeVar("T")


def generate_id(prefix: str = "id") -> str:
    """
    Generate a short, prefixed identifier.

    Example:
        generate_id("mem") -> "mem_a3f412bc"
    """
    random_part = uuid.uuid4().hex[:8]
    return f"{prefix}_{random_part}"


def safe_get(
    data: Dict[str, Any],
    path: Sequence[str],
    default: Any = None,
) -> Any:
    """
    Safely traverse nested dictionaries by a path of keys.

    Example:
        safe_get(user, ["profile", "preferences", "color"], "unknown")

    Equivalent to:
        user.get("profile", {}).get("preferences", {}).get("color", "unknown")
    """
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def flatten_list(list_of_lists: Iterable[Iterable[T]]) -> List[T]:
    """
    Flatten an iterable of iterables into a single list.

    Example:
        flatten_list([[1, 2], [3]]) -> [1, 2, 3]
    """
    flat: List[T] = []
    for sublist in list_of_lists:
        flat.extend(sublist)
    return flat


def pretty_json(obj: Any, indent: int = 2) -> str:
    """
    Render an object as pretty-printed JSON.

    Falls back to str(obj) if it is not JSON-serializable.
    """
    try:
        return json.dumps(obj, indent=indent, ensure_ascii=False)
    except TypeError:
        return str(obj)


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks of approximately `chunk_size` characters.

    This is a simple, character-based chunker suitable for:
    - embedding long texts
    - feeding to memory extraction in manageable segments

    Args:
        text: Input string.
        chunk_size: Target maximum characters per chunk.
        overlap: Number of characters of overlap between chunks.

    Returns:
        List of text chunks.
    """
    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0:
        raise ValueError("overlap must be non-negative.")

    # Use textwrap to roughly wrap into lines, then join into chunks
    normalized = " ".join(str(text).split())
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: List[str] = []
    start = 0
    length = len(normalized)

    while start < length:
        end = min(start + chunk_size, length)
        chunk = normalized[start:end]

        # Avoid breaking in the middle of a word if possible
        if end < length:
            last_space = chunk.rfind(" ")
            if last_space != -1 and last_space > chunk_size // 2:
                chunk = chunk[:last_space]
                end = start + last_space

        chunks.append(chunk.strip())
        if end == length:
            break

        start = max(0, end - overlap)

    return chunks


def ensure_str(obj: Any) -> str:
    """
    Ensure the given object is represented as a string.

    - None         -> ""
    - str          -> unchanged
    - other types  -> json.dumps(...) if possible, else str(obj)

    This is especially useful when building prompts or logging payloads.
    """
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj

    try:
        return json.dumps(obj, ensure_ascii=False)
    except TypeError:
        return str(obj)
