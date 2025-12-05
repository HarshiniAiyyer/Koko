from __future__ import annotations

"""Goal: Make the module easy to import from outside.

Plan:

Re-export the main public interfaces:

PersonalityVector

PersonaProfile / PersonaName enum

select_persona (auto selector)

rewrite_with_persona (high-level wrapper around the rewriter)

This lets other parts of the system do things like:

```from app.core.personality_engine import select_persona, rewrite_with_persona```


without caring about the internal folder layout.
"""

"""
Personality Engine

Responsible for:
- Representing assistant personas as personality vectors
  (warmth, energy, formality, directness, humor, depth)
- Selecting an appropriate persona based on emotional state
- Rewriting a neutral assistant reply into the chosen persona's tone
- Producing before/after tone transformation outputs

This module sits on top of:
- Emotion Engine (core_ai.emotion_engine) for emotional state
- LLMClient (core_ai.models.LLMClient) for style rewriting
"""

from typing import Any, Dict, Optional

from app.core.models import LLMClient
from app.core.personality_engine.schemas.personality_vector import PersonalityVector
from app.core.personality_engine.schemas.persona_profiles import (
    PersonaName,
    PersonaProfile,
    PRESET_PERSONA_PROFILES,
)
from app.core.personality_engine.selector.auto_selector import (
    PersonaSelectionResult,
    select_persona,
)
from app.core.personality_engine.rendering.persona_rewriter import (
    PersonaRewriter,
    rewrite_with_persona,
)


def apply_personality(
    neutral_reply: str,
    emotional_state: Optional[Dict[str, str | float]] = None,
    requested_persona: Optional[PersonaName] = None,
    llm_client: Optional[LLMClient] = None,
) -> Dict[str, Any]:
    """
    High-level helper that:
    1. Selects an appropriate persona (auto or requested)
    2. Rewrites the neutral reply into that persona's tone
    3. Returns a before/after structure for easy UI display.

    Args:
        neutral_reply: The base assistant reply (content-focused, neutral tone).
        emotional_state: Optional emotional signal dict, typically from
            emotion_engine.analyze_emotion(message), with keys:
            - state: "stressed" | "frustrated" | "excited" | "neutral" | "mixed"
            - sentiment: "positive" | "negative" | "neutral"
            - emotion: e.g. "joy", "fear", "anger", ...
            - confidence: 0.0–1.0
        requested_persona: If provided, force this persona instead of auto-selection.
        llm_client: Optional shared LLMClient instance.

    Returns:
        dict with:
        {
            "persona_name": <PersonaName>,
            "reason": <str>,
            "before": <neutral_reply>,
            "after": <styled_reply>,
        }
    """
    selection: PersonaSelectionResult = select_persona(
        emotional_state=emotional_state,
        requested_persona=requested_persona,
    )

    client = llm_client or LLMClient()
    rewriter = PersonaRewriter(llm_client=client)

    styled = rewriter.rewrite(
        neutral_reply=neutral_reply,
        persona_profile=selection.persona_profile,
    )

    return {
        "persona_name": selection.persona_name,
        "reason": selection.reason,
        "before": neutral_reply,
        "after": styled,
    }


__all__ = [
    # Schemas
    "PersonalityVector",
    "PersonaName",
    "PersonaProfile",
    "PRESET_PERSONA_PROFILES",
    # Selection
    "PersonaSelectionResult",
    "select_persona",
    # Rewriting
    "PersonaRewriter",
    "rewrite_with_persona",
    # High-level helper
    "apply_personality",
]
