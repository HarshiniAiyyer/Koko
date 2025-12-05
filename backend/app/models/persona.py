from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


class PersonaInfo(BaseModel):
    """Information about a persona"""
    name: str = Field(..., description="Persona name")
    description: str = Field(..., description="Persona description")
    traits: List[str] = Field(..., description="Key personality traits")


class PersonasResponse(BaseModel):
    """Response with available personas"""
    personas: List[PersonaInfo] = Field(..., description="Available personas")
