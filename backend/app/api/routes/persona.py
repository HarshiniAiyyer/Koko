from __future__ import annotations

from fastapi import APIRouter
from app.models.persona import PersonaInfo, PersonasResponse

router = APIRouter()


@router.get("/personas", response_model=PersonasResponse)
async def get_personas():
    """
    Get list of available personas with descriptions.
    
    Returns information about all supported personas.
    """
    personas = [
        PersonaInfo(
            name="calm_mentor",
            description="Grounded, warm, supportive guidance with short clear sentences",
            traits=["Empathetic", "Structured", "Reassuring", "Direct"],
        ),
        PersonaInfo(
            name="witty_friend",
            description="Energetic, humorous, casual conversation style",
            traits=["Playful", "Energetic", "Informal", "Humorous"],
        ),
        PersonaInfo(
            name="therapist",
            description="Deep, reflective, professional therapeutic approach",
            traits=["Empathetic", "Reflective", "Patient", "Non-judgmental"],
        ),
    ]
    
    return PersonasResponse(personas=personas)
