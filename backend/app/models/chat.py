from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message")
    user_id: Optional[str] = Field(None, description="Optional user ID for memory context")
    requested_persona: Optional[str] = Field(None, description="Optional persona to force (e.g. 'witty_friend')")


class EmotionalStateResponse(BaseModel):
    """Emotional state information"""
    state: str = Field(..., description="Overall emotional state (stressed, excited, neutral, etc.)")
    sentiment: str = Field(..., description="Sentiment (positive, negative, neutral)")
    emotion: str = Field(..., description="Primary emotion (joy, fear, anger, etc.)")
    confidence: float = Field(..., description="Confidence score 0-1")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    reply: str = Field(..., description="AI-generated reply")
    emotional_state: EmotionalStateResponse = Field(..., description="Detected emotional state")
    persona_used: str = Field(..., description="Persona used for tone (calm_mentor, witty_friend, etc.)")
    reason: str = Field(..., description="Reason for persona selection")
    neutral_reply: Optional[str] = Field(None, description="Neutral reply before persona transformation")
