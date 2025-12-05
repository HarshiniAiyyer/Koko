from __future__ import annotations

"""Human-readable storage of memory:

Save final structured memory output into memory.json

Load memory for debugging

Very simple CRUD operations

This file shows you considered persistence and reproducibility."""

import json
import logging
from pathlib import Path
from typing import Optional

from app.core.config.settings import settings
from app.core.memory_engine.schemas.memory_output import MemoryOutput

logger = logging.getLogger(__name__)


def _get_memory_path() -> Path:
    return Path(settings.MEMORY_JSON_PATH)


def save_memory_output(memory_output: MemoryOutput) -> None:
    """
    Save the structured memory output to a JSON file for inspection/debugging.

    Args:
        memory_output: Final MemoryOutput to persist.
    """
    path = _get_memory_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    data = memory_output.model_dump()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info("Saved memory output to %s", path)


def load_memory_output() -> Optional[MemoryOutput]:
    """
    Load the last saved memory output from disk, if present.

    Returns:
        MemoryOutput instance or None if file doesn't exist.
    """
    path = _get_memory_path()
    if not path.exists():
        logger.warning("No memory file found at %s", path)
        return None

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        return MemoryOutput(**data)
    except Exception as e:
        logger.error("Failed to parse memory JSON: %s", e)
        return None
