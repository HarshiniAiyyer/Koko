from __future__ import annotations

""" Define a Pydantic model representing one memory entry, containing:

type → "preference" / "pattern" / "fact"

content → natural language description

evidence → which messages triggered it

confidence → high / medium / low

embedding → optional vector for Qdrant storage

This becomes a node in your memory system."""

from typing import List, Optional, Literal

from pydantic import BaseModel, Field


MemoryType = Literal["preference", "pattern", "fact"]
ConfidenceLabel = Literal["high", "medium", "low"]


class MemoryItem(BaseModel):
    """
    Represents a single memory entry extracted from user messages.

    Attributes:
        type: One of "preference", "pattern", or "fact".
        content: Natural language description of the memory.
        evidence_indices: Optional indices of messages that support this memory.
        confidence: Qualitative label: "high", "medium", or "low".
        embedding: Optional embedding vector for semantic storage.
    """

    type: MemoryType = Field(...)
    content: str = Field(..., min_length=1)
    evidence_indices: Optional[List[int]] = Field(
        default=None,
        description="Indices into the original message list that support this memory.",
    )
    confidence: ConfidenceLabel = Field(
        default="medium",
        description="Qualitative confidence label derived from heuristics.",
    )
    embedding: Optional[List[float]] = Field(
        default=None,
        description="Optional dense vector representation used for vector DB indexing.",
    )

