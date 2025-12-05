from __future__ import annotations

"""Contains the scoring logic interface:

A MemoryConfidence enum (HIGH, MEDIUM, LOW)

A helper to map numeric scores to confidence labels

A helper for rule-based boosts (e.g. repeated mentions → increase score)

This plugs into both:

extraction cleanup

storage filtering (optional: skip low-confidence)"""

from enum import Enum


class MemoryConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


def score_to_confidence(
    score: float, high_threshold: float, medium_threshold: float
) -> MemoryConfidence:
    """
    Maps a numeric score in [0,1] to a qualitative confidence label.

    Args:
        score: Numeric score, typically in the range [0, 1].
        high_threshold: Threshold above which confidence is "high".
        medium_threshold: Threshold above which confidence is "medium".

    Returns:
        MemoryConfidence enum value.
    """
    if score >= high_threshold:
        return MemoryConfidence.HIGH
    if score >= medium_threshold:
        return MemoryConfidence.MEDIUM
    return MemoryConfidence.LOW
