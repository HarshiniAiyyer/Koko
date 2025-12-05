from __future__ import annotations

"""Goal: Provide hardcoded illustrative examples of tone transformation that you can:

Use in the README

Show in the UI

Use in tests / demos

Contents:

A small data structure like:

EXAMPLE_NEUTRAL = "To improve your sleep, reduce screen exposure at night."
EXAMPLE_PERSONA_NAMES = ["calm_mentor", "witty_friend", "therapist"]


Optional helper:

def generate_example_transformations(rewriter: PersonaRewriter) -> list[dict]:
    # calls rewrite for each persona and returns list of {persona, before, after}


Why:
The assignment explicitly wants “before/after” examples; this file makes it repeatable and neat."""

from typing import Any, Dict, List, Optional

from app.core.models import LLMClient
from app.core.personality_engine.schemas.persona_profiles import (
    PersonaProfile,
    PRESET_PERSONA_PROFILES,
)
from app.core.personality_engine.rendering.persona_rewriter import PersonaRewriter


# A simple canonical neutral reply you can reuse in docs / UI demos
DEFAULT_NEUTRAL_EXAMPLE = (
    "To improve your sleep, try going to bed at a consistent time each night, "
    "reducing screen use 60 minutes before bed, and keeping your room cool and dark."
)


def get_demo_personas() -> List[PersonaProfile]:
    """
    Convenience helper to access a default trio of demo personas.
    """
    return [
        PRESET_PERSONA_PROFILES["calm_mentor"],
        PRESET_PERSONA_PROFILES["witty_friend"],
        PRESET_PERSONA_PROFILES["therapist"],
    ]


def generate_before_after_examples(
    neutral_reply: str | None = None,
    llm_client: Optional[LLMClient] = None,
) -> List[Dict[str, Any]]:
    """
    Generate before/after examples for the default personas.

    This function is intentionally side-effect-free and only performs
    LLM calls when invoked (not at import time), so it's safe to use
    from a UI or CLI demo.

    Args:
        neutral_reply: Optional override for the base reply. If None,
            DEFAULT_NEUTRAL_EXAMPLE is used.
        llm_client: Optional shared LLMClient.

    Returns:
        List of dicts:
        [
            {
                "persona_name": "calm_mentor",
                "before": "...",
                "after": "...",
            },
            ...
        ]
    """
    base_reply = neutral_reply or DEFAULT_NEUTRAL_EXAMPLE
    client = llm_client or LLMClient()
    rewriter = PersonaRewriter(llm_client=client)

    outputs: List[Dict[str, Any]] = []
    for profile in get_demo_personas():
        styled = rewriter.rewrite(
            neutral_reply=base_reply,
            persona_profile=profile,
        )
        outputs.append(
            {
                "persona_name": profile.name,
                "before": base_reply,
                "after": styled,
            }
        )
    return outputs
