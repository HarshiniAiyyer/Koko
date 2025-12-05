from __future__ import annotations

"""extraction/ -> turns 30 messages into memory"""

"""storage/ ->  We store memory in BOTH: JSON for human-readable overview and Qdrant for semantic retrieval"""

"""retrieval/ -> semantic retrieval from Qdrant"""

"""Export key classes/functions:

extract_memory

store_memory_items

retrieve_relevant_memory

This makes the memory engine cleanly importable."""

"""
High-level interface for the Memory Engine.

This package is responsible for:

- Extracting structured user memory from raw messages
- Scoring confidence levels for each memory item
- Cleaning/deduplicating memory output
- Persisting memory (JSON + Qdrant)
- Retrieving relevant memory for downstream reasoning
"""

from typing import List

from core_ai.memory_engine.schemas.memory_output import MemoryOutput
from core_ai.memory_engine.extraction.memory_extractor import extract_memory
from core_ai.memory_engine.extraction.confidence_engine import (
    apply_confidence_scores,
)
from core_ai.memory_engine.extraction.cleanup import clean_memory_output
from core_ai.memory_engine.storage.memory_store import save_memory_output
from core_ai.memory_engine.storage.vector_store import store_memory_items
from core_ai.memory_engine.retrieval.semantic_retriever import (
    retrieve_relevant_memory,
)

__all__ = [
    "run_memory_pipeline",
    "extract_memory",
    "apply_confidence_scores",
    "clean_memory_output",
    "save_memory_output",
    "store_memory_items",
    "retrieve_relevant_memory",
    "MemoryOutput",
]


def run_memory_pipeline(messages: List[str]) -> MemoryOutput:
    """
    Convenience function that runs the full memory pipeline:

    1. LLM-based extraction (3-tier memory)
    2. Confidence scoring (high / medium / low)
    3. Cleanup & deduplication
    4. Persist to JSON
    5. Index into Qdrant for semantic retrieval

    Args:
        messages: List of user messages.

    Returns:
        Final cleaned MemoryOutput object.
    """
    raw_output = extract_memory(messages)
    scored_output = apply_confidence_scores(raw_output, messages)
    cleaned_output = clean_memory_output(scored_output)

    # Persist
    save_memory_output(cleaned_output)
    store_memory_items(cleaned_output)

    return cleaned_output
