from __future__ import annotations

"""Responsible for:

Removing duplicates

Merging near-identical items

Filtering out memory items with extremely low value

Normalizing content (“likes coffee” vs “prefers coffee”)

This module ensures clean memory before indexing."""

from typing import Dict, Tuple

from app.core.memory_engine.schemas.memory_item import MemoryItem
from app.core.memory_engine.schemas.memory_output import MemoryOutput


def _normalize_content(text: str) -> str:
    """
    Very simple text normalizer for deduplication.
    """
    return " ".join(text.strip().lower().split())


def _deduplicate_items(items: list[MemoryItem]) -> list[MemoryItem]:
    """
    Deduplicate MemoryItems by (type, normalized content).

    When duplicates are found:
    - Keep the item with the highest confidence (high > medium > low)
    - Merge evidence_indices (union)
    """
    def conf_rank(conf: str) -> int:
        if conf == "high":
            return 3
        if conf == "medium":
            return 2
        return 1

    by_key: Dict[Tuple[str, str], MemoryItem] = {}
    for item in items:
        key = (item.type, _normalize_content(item.content))
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = item
        else:
            # Choose the one with higher confidence
            if conf_rank(item.confidence) > conf_rank(existing.confidence):
                # Merge evidence indices
                merged_evidence = set(existing.evidence_indices or []) | set(
                    item.evidence_indices or []
                )
                item.evidence_indices = sorted(merged_evidence)
                by_key[key] = item
            else:
                merged_evidence = set(existing.evidence_indices or []) | set(
                    item.evidence_indices or []
                )
                existing.evidence_indices = sorted(merged_evidence)
                by_key[key] = existing

    return list(by_key.values())


def clean_memory_output(memory_output: MemoryOutput) -> MemoryOutput:
    """
    Perform basic cleanup on extracted memory:

    - Deduplicate overlapping/identical items
    - (Optionally) filter out very low-value items (currently not aggressive)

    Returns:
        Cleaned MemoryOutput.
    """
    cleaned_prefs = _deduplicate_items(memory_output.preferences)
    cleaned_patterns = _deduplicate_items(memory_output.patterns)
    cleaned_facts = _deduplicate_items(memory_output.facts)

    return MemoryOutput(
        preferences=cleaned_prefs,
        patterns=cleaned_patterns,
        facts=cleaned_facts,
        stats=memory_output.stats,
    )
