from __future__ import annotations

"""Goal: Build the style prompt that tells the LLM how to rewrite the reply given a persona.

Contents:

def build_style_instruction(persona_profile: PersonaProfile) -> str

Returns a natural language description like:

“You are a calm mentor: grounded, warm, supportive, using short clear sentences, focusing on reassurance and structured advice. Avoid humor, be gentle but direct.”

def build_rewrite_prompt(neutral_reply: str, persona_profile: PersonaProfile) -> dict | str

If we use a simple text prompt:

Something like:

“Rewrite the following assistant reply in the style of a {persona_name}… [style rules from vector]… Keep the factual content but change the tone only… Reply with just the rewritten message.”

If we want to structure it, it might return { "system": ..., "user": ... } for the LLM client wrapper.

We’ll keep it very LLM-agnostic here — no Groq specifics; those live in llm_client.py in models/.

Why:
This isolates the prompt engineering for tone from the rest of the logic."""

from typing import Tuple

from app.core.personality_engine.schemas.persona_profiles import PersonaProfile


def build_style_instruction(persona_profile: PersonaProfile) -> str:
    """
    Build a natural language instruction summarizing the persona's style.

    This is used as part of the system prompt for the LLM.

    Args:
        persona_profile: The persona definition to describe.

    Returns:
        A single string describing how the assistant should speak.
    """
    vec = persona_profile.vector
    style_keywords = vec.to_style_keywords()

    persona_label = persona_profile.name.replace("_", " ")
    tagline = persona_profile.tagline

    description_parts = [
        f"You are speaking as a **{persona_label}**.",
        f"Tone tagline: {tagline}",
        "",
        "Your style guidelines:",
        "- Stay aligned with the user's emotional safety and needs.",
        "- Maintain the original factual content and intent of the reply.",
        "- Only change the tone, style, and phrasing.",
        "",
        "Personality axes and style indicators:",
        f"- Warmth: {vec.warmth:.2f}",
        f"- Energy: {vec.energy:.2f}",
        f"- Formality: {vec.formality:.2f}",
        f"- Directness: {vec.directness:.2f}",
        f"- Humor: {vec.humor:.2f}",
        f"- Depth: {vec.depth:.2f}",
        "",
        "High-level style descriptors: " + ", ".join(style_keywords),
        "",
        "Key constraints:",
        "- Do NOT introduce new facts.",
        "- Do NOT remove important details.",
        "- Do NOT change the user's meaning or advice content.",
        "- Keep the reply clear, readable, and extremely concise (max 2-3 sentences).",
    ]

    return "\n".join(description_parts)


def build_rewrite_prompts(
    neutral_reply: str,
    persona_profile: PersonaProfile,
) -> Tuple[str, str]:
    """
    Build (system_prompt, user_prompt) pair for the persona rewriting call.

    Args:
        neutral_reply: The base assistant reply in neutral tone.
        persona_profile: The persona used to style the reply.

    Returns:
        (system_prompt, user_prompt) tuple.
    """
    system_prompt = (
        "You are an AI assistant that rewrites replies into a specific tone.\n"
        "You will be given a base assistant reply and a persona description.\n"
        "Your job is to rewrite the reply to match the persona, without "
        "changing the underlying facts or recommendations."
    )

    style_instruction = build_style_instruction(persona_profile)

    user_prompt = f"""
Below is a base assistant reply written in a neutral tone:

--- BASE REPLY START ---
{neutral_reply}
--- BASE REPLY END ---

Rewrite this reply so that it matches the persona described below, while
keeping all factual content and advice intact.
112: 
113: CRITICAL: The rewritten reply must be short and punchy. Maximum 2-3 sentences.

Persona description:
{style_instruction}

Important:
- Only output the rewritten reply text.
- Do not include explanations, notes, or metadata.
- Do not wrap the reply in quotes or markdown fences.
"""

    return system_prompt.strip(), user_prompt.strip()
