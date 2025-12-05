from __future__ import annotations

"""Defines the structured output of the memory extraction step:

{
  "preferences": [MemoryItem],
  "patterns": [MemoryItem],
  "facts": [MemoryItem]
}


This is what:

the LLM returns (raw)

the cleanup module refines

the vector store indexes

This file ensures EVERY downstream module uses a unified schema."""

from typing import List

from pydantic import BaseModel, Field

from app.core.memory_engine.schemas.memory_item import MemoryItem
from app.core.memory_engine.schemas.user_stats import UserStats


class MemoryOutput(BaseModel):
    """
    Container for all extracted memory, grouped into three categories:

    - preferences: stable likes/dislikes, constraints, and preferences
    - patterns: behavioral or emotional patterns over time
    - facts: concrete factual details worth remembering
    """

    preferences: List[MemoryItem] = Field(default_factory=list)
    patterns: List[MemoryItem] = Field(default_factory=list)
    facts: List[MemoryItem] = Field(default_factory=list)
    stats: UserStats = Field(default_factory=UserStats)
