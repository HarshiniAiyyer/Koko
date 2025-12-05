from __future__ import annotations

"""Goal: Actually call the LLM and produce the tonally transformed response, plus handle the before/after view.

Contents:

A PersonaRewriter class that depends on llm_client:

__init__(self, llm_client)

async def rewrite(self, neutral_reply: str, persona_profile: PersonaProfile) -> str

Uses tone_prompt_builder.build_rewrite_prompt

Calls the LLM

Returns only the rewritten reply text

A convenience function for outside use:

```
def rewrite_with_persona(
    neutral_reply: str,
    persona_name: PersonaName,
    emotional_state: dict | None = None,
) -> dict:
    
    Returns:
    {
        "persona_name": ...,
        "before": neutral_reply,
        "after": styled_reply
    }
```   


Optionally:

rewrite_into_multiple_personas(neutral_reply, [PersonaName]) -> list[BeforeAfterPair]

Handy for showcasing multiple tones in the demo.

Why:
This is where the before/after personality response differences requirement is implemented cleanly."""

from typing import Any, Dict, List, Optional

from core_ai.models import LLMClient
from core_ai.personality_engine.schemas.persona_profiles import (
    PersonaName,
    PersonaProfile,
    PRESET_PERSONA_PROFILES,
)
from core_ai.personality_engine.selector.auto_selector import (
    PersonaSelectionResult,
    select_persona,
)
from core_ai.personality_engine.rendering.tone_prompt_builder import (
    build_rewrite_prompts,
)


class PersonaRewriter:
    """
    Applies persona-based tone to a neutral assistant reply using the LLM.

    This class is intentionally thin: it delegates persona selection to
    the selector module and prompt construction to tone_prompt_builder.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def rewrite(self, neutral_reply: str, persona_profile: PersonaProfile) -> str:
        """
        Rewrite a neutral reply in the style of the given persona.

        Args:
            neutral_reply: Base assistant reply in neutral tone.
            persona_profile: PersonaProfile describing the target style.

        Returns:
            The rewritten reply as a string.
        """
        system_prompt, user_prompt = build_rewrite_prompts(
            neutral_reply=neutral_reply,
            persona_profile=persona_profile,
        )

        styled: str = self.llm_client.generate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=512,
        )
        return styled.strip()

    def rewrite_multiple(
        self,
        neutral_reply: str,
        persona_profiles: List[PersonaProfile],
    ) -> Dict[str, str]:
        """
        Rewrite the same neutral reply into multiple personas.

        Args:
            neutral_reply: Base assistant reply.
            persona_profiles: List of PersonaProfile instances.

        Returns:
            Dict mapping persona_name -> rewritten reply.
        """
        outputs: Dict[str, str] = {}
        for profile in persona_profiles:
            outputs[profile.name] = self.rewrite(
                neutral_reply=neutral_reply,
                persona_profile=profile,
            )
        return outputs


def rewrite_with_persona(
    neutral_reply: str,
    persona_name: Optional[PersonaName] = None,
    emotional_state: Optional[Dict[str, str | float]] = None,
    llm_client: Optional[LLMClient] = None,
) -> Dict[str, Any]:
    """
    Convenience wrapper that:
    - Chooses a persona (requested or auto-selected)
    - Rewrites the reply accordingly
    - Returns a before/after payload, plus selection metadata.

    Args:
        neutral_reply: Base assistant reply.
        persona_name: Optional explicit persona to use.
        emotional_state: Optional emotional state dict from Emotion Engine.
        llm_client: Optional LLMClient instance.

    Returns:
        {
            "persona_name": <PersonaName>,
            "reason": <selection_reason>,
            "before": <neutral_reply>,
            "after": <styled_reply>,
        }
    """
    # If persona_name is provided, we treat it as a manual override
    requested: Optional[PersonaName] = persona_name if persona_name else None

    selection: PersonaSelectionResult = select_persona(
        emotional_state=emotional_state,
        requested_persona=requested,
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
