from __future__ import annotations

from pydantic import BaseModel, Field


class UserStats(BaseModel):
    """
    User emotional/behavioral stats (0-100 scale).
    """
    anxiety: float = Field(0.0, description="Anxiety level (0-100)")
    paralysis: float = Field(0.0, description="Decision paralysis level (0-100)")
    optimism: float = Field(0.0, description="Optimism level (0-100)")
    stress: float = Field(0.0, description="Stress level (0-100)")
