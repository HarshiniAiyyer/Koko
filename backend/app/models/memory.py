from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    """Single memory item"""
    type: str = Field(..., description="Type: preference, pattern, or fact")
    content: str = Field(..., description="Memory content")
    confidence: str = Field(..., description="Confidence level: high, medium, low")
    evidence_indices: Optional[List[int]] = Field(None, description="Message indices supporting this memory")


class MemoryExtractRequest(BaseModel):
    """Request to extract memory from messages"""
    messages: List[str] = Field(..., description="List of user messages")


class MemoryExtractResponse(BaseModel):
    """Response with extracted memory"""
    preferences: List[MemoryItem] = Field(default_factory=list, description="User preferences")
    patterns: List[MemoryItem] = Field(default_factory=list, description="Emotional/behavioral patterns")
    facts: List[MemoryItem] = Field(default_factory=list, description="Concrete facts")
    stats: Optional[dict] = Field(default_factory=dict, description="User stats (anxiety, etc.)")


class MemoryGetResponse(BaseModel):
    """Response for getting stored memory"""
    preferences: List[MemoryItem] = Field(default_factory=list)
    patterns: List[MemoryItem] = Field(default_factory=list)
    facts: List[MemoryItem] = Field(default_factory=list)
    stats: Optional[dict] = Field(default_factory=dict)
    total_items: int = Field(..., description="Total memory items")
