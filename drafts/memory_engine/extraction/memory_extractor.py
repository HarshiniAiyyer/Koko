from __future__ import annotations

"""Turns 30 messages into memory - i.e, heart of the memory engine"""

"""Contains the LLM prompt to extract three-tier memory:

preferences

patterns

facts worth remembering

Implements a function:
extract_memory(messages: list[str]) -> MemoryOutput

Does:

Build the prompt

Call LLMClient.structured_generate()

Validate structure

Convert to Pydantic models

This file is the heart of the memory engine."""

from typing import List, Dict, Any, Optional

from core_ai.models import LLMClient
from core_ai.memory_engine.schemas.memory_item import MemoryItem, MemoryType
from core_ai.memory_engine.schemas.memory_output import MemoryOutput


MEMORY_EXTRACTION_SYSTEM_PROMPT = """
You are an AI specializing in user modeling and memory extraction
for a long-term companion system.

You will be given a list of past messages from a single user.
Your job is to extract three types of memory:

1) User preferences (likes, dislikes, stable preferences, constraints)
2) User emotional or behavioral patterns (how they tend to respond, recurring themes)
3) Concrete facts worth remembering (job, location hints, key personal details)

Follow these rules:
- Be concise but specific.
- Prefer stable, recurring traits over one-off events.
- If unsure, omit rather than hallucinate.
- Always return VALID JSON ONLY, with no extra commentary.
"""


def _build_user_prompt(messages: List[str]) -> str:
    """
    Build a prompt for the model, summarizing the 30 messages
    and asking for structured memory extraction.
    """
    joined = "\n".join(f"- {i}: {m}" for i, m in enumerate(messages))
    prompt = f"""
Here are the user's past messages (index: text):

{joined}

Extract memories in the following JSON format:

{{
  "preferences": [
    {{
      "type": "preference",
      "content": "string",
      "evidence_indices": [int, ...]
    }}
  ],
  "patterns": [
    {{
      "type": "pattern",
      "content": "string",
      "evidence_indices": [int, ...]
    }}
  ],
  "facts": [
    {{
      "type": "fact",
      "content": "string",
      "evidence_indices": [int, ...]
    }}
  ]
}}

- Use arrays (which may be empty) for each key.
- evidence_indices should reference the indices listed above.
- Do not include a 'confidence' field; that will be computed later.
"""
    return prompt.strip()


def _parse_memory_items(raw_list: List[Dict[str, Any]], item_type: MemoryType) -> List[MemoryItem]:
    """
    Convert a raw list of dicts from the LLM into MemoryItem objects.

    Args:
        raw_list: List of dicts from the model.
        item_type: The memory type we expect for this list.

    Returns:
        List of MemoryItem instances.
    """
    items: List[MemoryItem] = []
    for raw in raw_list or []:
        content = str(raw.get("content", "")).strip()
        if not content:
            continue
        evidence_indices = raw.get("evidence_indices", None)
        if isinstance(evidence_indices, list):
            evidence_indices = [int(i) for i in evidence_indices if isinstance(i, int)]
        else:
            evidence_indices = None

        items.append(
            MemoryItem(
                type=item_type,
                content=content,
                evidence_indices=evidence_indices,
            )
        )
    return items


def extract_memory(
    messages: List[str],
    llm_client: Optional[LLMClient] = None,
) -> MemoryOutput:
    """
    Run the LLM-based memory extraction step.

    Args:
        messages: List of user messages (ideally 30, but flexible).
        llm_client: Optional LLMClient instance; if not provided, a default is created.

    Returns:
        MemoryOutput with raw (unscored, uncleaned) MemoryItem lists.
    """
    if llm_client is None:
        llm_client = LLMClient()

    user_prompt = _build_user_prompt(messages)
    raw_json: Dict[str, Any] = llm_client.structured_generate(
        user_prompt=user_prompt,
        system_prompt=MEMORY_EXTRACTION_SYSTEM_PROMPT,
        temperature=0.1,
        max_tokens=1024,
    )

    raw_prefs = raw_json.get("preferences", [])
    raw_patterns = raw_json.get("patterns", [])
    raw_facts = raw_json.get("facts", [])

    preferences = _parse_memory_items(raw_prefs, "preference")
    patterns = _parse_memory_items(raw_patterns, "pattern")
    facts = _parse_memory_items(raw_facts, "fact")

    return MemoryOutput(
        preferences=preferences,
        patterns=patterns,
        facts=facts,
    )
