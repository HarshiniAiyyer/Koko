from __future__ import annotations

from pydantic import BaseModel, Field


class EmotionAnalyzeRequest(BaseModel):
    """Request to analyze emotion"""
    text: str = Field(..., description="Text to analyze")


class EmotionAnalyzeResponse(BaseModel):
    """Response with emotion analysis"""
    state: str = Field(..., description="Emotional state (stressed, excited, neutral, etc.)")
    sentiment: str = Field(..., description="Sentiment (positive, negative, neutral)")
    emotion: str = Field(..., description="Primary emotion (joy, fear, anger, sadness, etc.)")
    confidence: float = Field(..., description="Confidence score 0-1")
