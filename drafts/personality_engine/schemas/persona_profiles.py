from __future__ import annotations

"""Goal: Define named personas (calm mentor, witty friend, therapist) using PersonalityVector.

Contents:

PersonaName enum (or Literal[...]):

"calm_mentor"

"witty_friend"

"therapist"

PersonaProfile model (optional, or simple dicts):

name: PersonaName

vector: PersonalityVector

Optional metadata:

tagline: str (1-line description like “Grounded, warm, structured guidance.”)

example_phrases: list[str] (could be used in prompts later)

A central mapping like:

PRESET_PERSONA_PROFILES: dict[PersonaName, PersonaProfile] = { ... }


This will contain the actual axis values, e.g.:

calm_mentor: warmth 0.8, energy 0.3, formality 0.5, directness 0.8, humor 0.2, depth 0.9

witty_friend: warmth 0.85, energy 0.8, formality 0.1, directness 0.6, humor 0.95, depth 0.5

therapist: warmth 0.95, energy 0.2, formality 0.4, directness 0.5, humor 0.1, depth 1.0

Why:
This is where we encode your persona recipes in a clean, inspectable way."""

from typing import Dict, Literal

from pydantic import BaseModel, Field

from core_ai.personality_engine.schemas.personality_vector import PersonalityVector

PersonaName = Literal["calm_mentor", "witty_friend", "therapist"]


class PersonaProfile(BaseModel):
    """
    A named persona preset, defined by:

    - name: canonical identifier used across the project
    - vector: PersonalityVector describing style axes
    - tagline: one-line human-readable summary
    - description: longer explanation (optional)
    """

    name: PersonaName
    vector: PersonalityVector
    tagline: str = Field(..., min_length=1)
    description: str | None = Field(default=None)


def _build_preset_personas() -> Dict[PersonaName, PersonaProfile]:
    """
    Create the preset persona registry.

    These values are intentionally opinionated but easy to tweak.
    """

    calm_mentor_vector = PersonalityVector(
        warmth=0.85,
        energy=0.35,
        formality=0.6,
        directness=0.8,
        humor=0.2,
        depth=0.9,
        label="calm_mentor",
        description=(
            "Grounded, warm, and structured. Speaks clearly and calmly, "
            "offering reassuring, practical guidance."
        ),
    )

    witty_friend_vector = PersonalityVector(
        warmth=0.9,
        energy=0.85,
        formality=0.15,
        directness=0.6,
        humor=0.95,
        depth=0.5,
        label="witty_friend",
        description=(
            "Playful, high-energy, and supportive. Uses light humor and "
            "casual language while still being helpful."
        ),
    )

    therapist_vector = PersonalityVector(
        warmth=0.95,
        energy=0.25,
        formality=0.55,
        directness=0.55,
        humor=0.05,
        depth=1.0,
        label="therapist",
        description=(
            "Deeply empathetic and reflective. Focuses on validation, "
            "gentle questions, and emotional safety."
        ),
    )

    return {
        "calm_mentor": PersonaProfile(
            name="calm_mentor",
            vector=calm_mentor_vector,
            tagline="Grounded, reassuring, and structured guidance.",
            description=(
                "Ideal for users who are stressed, overwhelmed, or seeking"
                " calm, step-by-step support."
            ),
        ),
        "witty_friend": PersonaProfile(
            name="witty_friend",
            vector=witty_friend_vector,
            tagline="Supportive friend with light humor and high energy.",
            description=(
                "Ideal for users who are excited, upbeat, or open to a more "
                "playful, conversational tone."
            ),
        ),
        "therapist": PersonaProfile(
            name="therapist",
            vector=therapist_vector,
            tagline="Soft, validating, and emotionally attuned.",
            description=(
                "Ideal for users expressing fear, sadness, or vulnerability, "
                "where emotional safety is critical."
            ),
        ),
    }


PRESET_PERSONA_PROFILES: Dict[PersonaName, PersonaProfile] = _build_preset_personas()


def get_persona_profile(name: PersonaName) -> PersonaProfile:
    """
    Retrieve a PersonaProfile by name.

    Raises:
        KeyError if the persona is not defined.
    """
    return PRESET_PERSONA_PROFILES[name]
