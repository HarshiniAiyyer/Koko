from __future__ import annotations

"""Computes confidence scores for each memory item via:

Heuristics:

repeated mentions → boost

stronger linguistic indicators ("I always", "I love", etc.) → boost

uncertainty words → reduce

Integration with MemoryConfidence enum

Adds confidence to each MemoryItem."""

from typing import List

from core_ai.config.settings import settings
from core_ai.memory_engine.schemas.memory_output import MemoryOutput
from core_ai.memory_engine.schemas.memory_item import MemoryItem
from core_ai.memory_engine.schemas.confidence_score import (
    MemoryConfidence,
    score_to_confidence,
)


INTENSIFIER_WORDS = {"always", "really", "definitely", "absolutely", "love", "hate"}
FREQUENCY_WORDS = {"usually", "often", "typically", "tend to"}


def _estimate_confidence_score(item: MemoryItem, messages: List[str]) -> float:
    """
    Heuristic confidence scorer.

    Factors considered:
    - Presence of intensifier words in the content
    - Presence of frequency words in the content
    - Basic substring matches against the original messages (very lightweight)

    Returns:
        A float score roughly in [0,1].
    """
    text = item.content.lower()
    score = 0.4  # base score

    if any(w in text for w in INTENSIFIER_WORDS):
        score += 0.3
    if any(w in text for w in FREQUENCY_WORDS):
        score += 0.2

    # Simple evidence-based bump: if content substring appears in messages
    matches = sum(1 for m in messages if item.content.lower() in m.lower())
    if matches >= 3:
        score += 0.2
    elif matches == 2:
        score += 0.1

    return max(0.0, min(score, 1.0))


def _apply_conf_to_items(items: List[MemoryItem], messages: List[str]) -> List[MemoryItem]:
    updated: List[MemoryItem] = []
    for item in items:
        score = _estimate_confidence_score(item, messages)
        conf = score_to_confidence(
            score=score,
            high_threshold=settings.HIGH_CONFIDENCE_THRESHOLD,
            medium_threshold=settings.MEDIUM_CONFIDENCE_THRESHOLD,
        )
        item.confidence = MemoryConfidence(conf).value  # store string label
        updated.append(item)
    return updated


def apply_confidence_scores(
    memory_output: MemoryOutput, messages: List[str]
) -> MemoryOutput:
    """
    Apply heuristic confidence scoring to all memory items.

    Args:
        memory_output: Raw MemoryOutput from the extractor.
        messages: Original user messages.

    Returns:
        Updated MemoryOutput with confidence labels populated.
    """
    return MemoryOutput(
        preferences=_apply_conf_to_items(memory_output.preferences, messages),
        patterns=_apply_conf_to_items(memory_output.patterns, messages),
        facts=_apply_conf_to_items(memory_output.facts, messages),
    )
