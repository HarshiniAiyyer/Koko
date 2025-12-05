from __future__ import annotations

"""2️⃣ schemas/personality_vector.py

Goal: Define the numeric representation of personality: your 6 axes.

Contents:

PersonalityVector (Pydantic model)

Fields:

warmth: float (0–1 or 0–100, we’ll pick one convention)

energy: float

formality: float

directness: float

humor: float

depth: float

Optional metadata:

label: str | None (e.g., "calm_mentor")

description: str | None (short human description of the style)

Helper methods (not heavy logic, just convenience):

@classmethod def from_dict(cls, data: dict) -> "PersonalityVector"

def blend(self, other: "PersonalityVector", alpha: float) -> "PersonalityVector"
(for future blending, even though we’re not doing slider UI now)

def to_style_keywords(self) -> list[str]

e.g., high warmth + high depth → ["empathetic", "reflective"]

Why:
This file is the mathy, structured heart of the persona system — it makes the personas feel like vectors, not just names in prompts."""

from typing import Literal

from pydantic import BaseModel, Field

PersonalityAxisName = Literal[
    "warmth",
    "energy",
    "formality",
    "directness",
    "humor",
    "depth",
]


class PersonalityVector(BaseModel):
    """
    Numeric representation of a persona style across six axes:

    - warmth: colder/neutral → highly empathetic
    - energy: calm/low-key → high-energy/animated
    - formality: casual → formal
    - directness: indirect/softened → direct/straightforward
    - humor: serious → humorous/playful
    - depth: surface-level → reflective/deep

    Values are normalized to [0.0, 1.0] for each axis.
    """

    warmth: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)
    formality: float = Field(..., ge=0.0, le=1.0)
    directness: float = Field(..., ge=0.0, le=1.0)
    humor: float = Field(..., ge=0.0, le=1.0)
    depth: float = Field(..., ge=0.0, le=1.0)
    label: str | None = Field(
        default=None,
        description="Optional identifier for the persona vector (e.g. 'calm_mentor').",
    )
    description: str | None = Field(
        default=None,
        description="Optional natural language description of the persona.",
    )

    def to_style_keywords(self) -> list[str]:
        """
        Convert the numeric axes into a list of high-level style descriptors.
        Useful for constructing system prompts for persona rewriting.
        """

        def bucket(value: float) -> str:
            if value <= 0.33:
                return "low"
            if value >= 0.67:
                return "high"
            return "medium"

        labels: list[str] = []

        # Warmth
        w = bucket(self.warmth)
        if w == "high":
            labels.append("warm")
            labels.append("empathetic")
        elif w == "medium":
            labels.append("friendly")
        else:
            labels.append("neutral_warmth")

        # Energy
        e = bucket(self.energy)
        if e == "high":
            labels.append("energetic")
            labels.append("enthusiastic")
        elif e == "medium":
            labels.append("steady_energy")
        else:
            labels.append("calm")

        # Formality
        f = bucket(self.formality)
        if f == "high":
            labels.append("formal")
        elif f == "medium":
            labels.append("semi_formal")
        else:
            labels.append("casual")

        # Directness
        d = bucket(self.directness)
        if d == "high":
            labels.append("direct")
        elif d == "medium":
            labels.append("balanced_directness")
        else:
            labels.append("gentle")

        # Humor
        h = bucket(self.humor)
        if h == "high":
            labels.append("humorous")
            labels.append("playful")
        elif h == "medium":
            labels.append("light_humor")
        else:
            labels.append("serious")

        # Depth
        dp = bucket(self.depth)
        if dp == "high":
            labels.append("reflective")
            labels.append("introspective")
        elif dp == "medium":
            labels.append("balanced_depth")
        else:
            labels.append("lightweight")

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_labels: list[str] = []
        for lab in labels:
            if lab not in seen:
                seen.add(lab)
                unique_labels.append(lab)

        return unique_labels

