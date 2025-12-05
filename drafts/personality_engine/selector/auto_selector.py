from __future__ import annotations

"""Goal: Decide which persona to use for a reply.

We keep this lean, but smart:
It takes current emotional state and (optionally) a requested persona, then chooses the persona + rationale.

Inputs:

emotional_state (from emotion_engine.state_estimator)
Likely something like:

{
    "sentiment": "negative" | "positive" | "neutral",
    "primary_emotion": "anxiety" | "joy" | "sadness" | ...,
    "intensity": float,  # 0–1
}


requested_persona: Optional[PersonaName]

If user explicitly says “use witty friend”, this overrides auto.

Outputs:

A PersonaSelectionResult model:

persona_name: PersonaName

vector: PersonalityVector

reason: str (short explanation like:
"Detected high stress and fear → using 'calm_mentor' for grounded, structured comfort.")

Core functions:

def select_persona(emotional_state, requested_persona: PersonaName | None) -> PersonaSelectionResult

Logic examples:

If requested_persona provided → return that persona + simple reason.

Else:

If primary_emotion in {fear, anxiety, sadness} → "therapist" or "calm_mentor"

If primary_emotion in {joy, excitement} → "witty_friend"

If neutral but sentiment slightly negative → "calm_mentor"

Otherwise default to "calm_mentor"

Why:
This is your auto-detect personality routing."""

from typing import Dict, Optional

from pydantic import BaseModel, Field

from core_ai.personality_engine.schemas.persona_profiles import (
    PersonaName,
    PersonaProfile,
    PRESET_PERSONA_PROFILES,
)


class PersonaSelectionResult(BaseModel):
    """
    Result of persona selection.

    Attributes:
        persona_name: chosen persona identifier
        persona_profile: full PersonaProfile for this persona
        reason: short explanation of why this persona was selected
        emotional_state: the raw emotional state signal used (if any)
    """

    persona_name: PersonaName
    persona_profile: PersonaProfile
    reason: str = Field(..., min_length=1)
    emotional_state: Dict[str, str | float] | None = None


def _default_persona() -> PersonaSelectionResult:
    """
    Fallback persona when no emotional signal is available.
    Defaults to the 'calm_mentor' persona.
    """
    profile: PersonaProfile = PRESET_PERSONA_PROFILES["calm_mentor"]
    return PersonaSelectionResult(
        persona_name="calm_mentor",
        persona_profile=profile,
        reason="No emotional state provided; defaulting to calm mentor.",
        emotional_state=None,
    )


def select_persona(
    emotional_state: Optional[Dict[str, str | float]] = None,
    requested_persona: Optional[PersonaName] = None,
) -> PersonaSelectionResult:
    """
    Select an appropriate persona based on the user's emotional state
    and any explicit persona request.

    Args:
        emotional_state: Dict typically from emotion_engine.analyze_emotion(message), e.g.:
            {
                "state": "stressed" | "frustrated" | "excited" | "neutral" | "mixed",
                "sentiment": "positive" | "negative" | "neutral",
                "emotion": "joy" | "fear" | "anger" | "sadness" | "neutral" | ...,
                "confidence": 0.0–1.0
            }
        requested_persona: If provided, this persona is used directly,
            bypassing auto selection (but still recorded in the reason).

    Returns:
        PersonaSelectionResult with persona_name, profile, and reason.
    """
    # 1. Manual override if user explicitly selected a persona
    if requested_persona is not None:
        profile = PRESET_PERSONA_PROFILES.get(requested_persona)
        if profile is None:
            # Should not happen if PersonaName is used correctly
            profile = PRESET_PERSONA_PROFILES["calm_mentor"]
            reason = (
                f"Requested persona '{requested_persona}' is undefined; "
                "falling back to calm mentor."
            )
        else:
            reason = f"User explicitly requested the '{requested_persona}' persona."
        return PersonaSelectionResult(
            persona_name=profile.name,
            persona_profile=profile,
            reason=reason,
            emotional_state=emotional_state,
        )

    # 2. If we have no emotional signal at all, use default
    if emotional_state is None:
        return _default_persona()

    state = str(emotional_state.get("state", "neutral"))
    sentiment = str(emotional_state.get("sentiment", "neutral"))
    emotion_label = str(emotional_state.get("emotion", "neutral"))
    confidence = float(emotional_state.get("confidence", 0.0))

    # 3. Heuristic mapping from emotional state → persona
    # These rules are deliberately simple but interpretable.
    if state == "stressed" or (
        sentiment == "negative"
        and emotion_label in {"fear", "anxiety", "sadness"}
    ):
        profile = PRESET_PERSONA_PROFILES["therapist"]
        reason = (
            "Detected stressed or anxious emotional state "
            f"(sentiment={sentiment}, emotion={emotion_label}, confidence={confidence:.2f}) "
            "→ using therapist-style persona for emotional safety."
        )
    elif state == "frustrated" or (
        sentiment == "negative" and emotion_label in {"anger"}
    ):
        profile = PRESET_PERSONA_PROFILES["calm_mentor"]
        reason = (
            "Detected frustration or anger "
            f"(sentiment={sentiment}, emotion={emotion_label}, confidence={confidence:.2f}) "
            "→ using calm mentor persona to de-escalate and provide structure."
        )
    elif state == "excited" or (
        sentiment == "positive" and emotion_label in {"joy"}
    ):
        profile = PRESET_PERSONA_PROFILES["witty_friend"]
        reason = (
            "Detected excited or joyful emotional state "
            f"(sentiment={sentiment}, emotion={emotion_label}, confidence={confidence:.2f}) "
            "→ using witty friend persona to match positive energy."
        )
    elif state == "neutral":
        profile = PRESET_PERSONA_PROFILES["calm_mentor"]
        reason = (
            "Detected neutral emotional state "
            f"(sentiment={sentiment}, emotion={emotion_label}, confidence={confidence:.2f}) "
            "→ using calm mentor persona as a balanced default."
        )
    else:
        # 'mixed' or any unexpected combination
        profile = PRESET_PERSONA_PROFILES["calm_mentor"]
        reason = (
            "Detected mixed or ambiguous emotional state "
            f"(state={state}, sentiment={sentiment}, emotion={emotion_label}, "
            f"confidence={confidence:.2f}) → using calm mentor persona as safe fallback."
        )

    return PersonaSelectionResult(
        persona_name=profile.name,
        persona_profile=profile,
        reason=reason,
        emotional_state=emotional_state,
    )
