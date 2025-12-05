from __future__ import annotations

"""This file will contain the ResponsePipeline class, which executes the end-to-end flow:

User message
    ↓
Emotion Engine → emotional_state
    ↓
Memory Engine → retrieve relevant memories → memory context
    ↓
LLM generates neutral reply (content-focused)
    ↓
Personality Engine → tone-rewritten “after” version
    ↓
Return structure with “before/after + reasoning”


Here’s the detailed plan:

🏗 Class: ResponsePipeline
init(self, llm_client, memory_store, vector_store, emotion_analyzer)

Injected dependencies:

LLMClient → generating neutral response & style rewriting

MemoryStore → extracted memories (JSON)

VectorStore (Qdrant) → semantic memory retrieval

EmotionAnalyzer → sentiment + emotion classification

We don’t hardcode these inside; we inject them.
This makes architecture professional and testable.

Stored as attributes."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from core_ai.models import LLMClient
from core_ai.personality_engine import apply_personality
from core_ai.personality_engine.schemas.persona_profiles import PersonaName


class PipelineOutput(BaseModel):
    """
    Final output of the end-to-end response pipeline.

    This is intentionally rich so you can:
    - Inspect emotional reasoning
    - See which memories were used
    - Compare before/after personality tone
    - Render a nice demo UI
    """

    user_message: str = Field(..., description="The raw input message from the user.")
    emotional_state: Dict[str, str | float] | None = Field(
        default=None,
        description="Emotional state inferred from the user's message.",
    )
    semantic_memory: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of semantically retrieved memory snippets (vector DB).",
    )
    structured_memory: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured memory summary (preferences, patterns, facts, etc.).",
    )
    neutral_reply: str = Field(
        ...,
        description="Content-focused reply generated before tone styling.",
    )
    persona_name: PersonaName = Field(
        ...,
        description="The persona used to style the final reply.",
    )
    persona_reason: str = Field(
        ...,
        description="Why this persona was selected (based on emotional state and/or request).",
    )
    final_reply: str = Field(
        ...,
        description="The styled reply after applying the persona tone.",
    )


class ResponsePipeline:
    """
    End-to-end orchestration of the conversational response flow.

    Responsibilities:
    - Analyze emotional state from the user's message (Emotion Engine)
    - Retrieve relevant memories (Memory Engine + Vector DB)
    - Generate a neutral assistant reply (LLM core)
    - Apply personality tone and produce before/after output (Personality Engine)

    Dependencies are injected to keep the system modular and testable.
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        memory_store: Optional[Any] = None,
        vector_store: Optional[Any] = None,
        emotion_analyzer: Optional[Any] = None,
    ) -> None:
        """
        Args:
            llm_client: Core LLM client used for neutral reply and persona rewriting.
            memory_store: Component responsible for serving structured memory, expected
                to expose a method like:
                    get_all() -> Dict[str, Any]
            vector_store: Component for semantic memory retrieval, expected to expose
                a method like:
                    search(query: str, top_k: int) -> List[Dict[str, Any]]
            emotion_analyzer: Component for emotional state detection, expected to expose:
                    analyze(text: str) -> Dict[str, str | float]
        """
        self.llm_client = llm_client or LLMClient()
        self.memory_store = memory_store
        self.vector_store = vector_store
        self.emotion_analyzer = emotion_analyzer

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run(
        self,
        user_message: str,
        requested_persona: Optional[PersonaName] = None,
        top_k_memories: int = 5,
    ) -> PipelineOutput:
        """
        Execute the full response pipeline for a single user message.

        Args:
            user_message: The latest input from the user.
            requested_persona: Optional explicit persona selection (manual override).
            top_k_memories: How many semantic memory items to retrieve from the vector store.

        Returns:
            PipelineOutput describing emotional state, memory usage,
            neutral and styled replies, and persona selection reasoning.
        """
        # 1. Emotional state
        emotional_state = self._analyze_emotion(user_message=user_message)

        # 2. Memory context
        semantic_memory, structured_memory = self._retrieve_memory_context(
            user_message=user_message,
            top_k=top_k_memories,
        )

        # 3. Neutral reply (content-focused, no style)
        neutral_reply = self._generate_neutral_reply(
            user_message=user_message,
            semantic_memory=semantic_memory,
            structured_memory=structured_memory,
        )

        # 4. Apply personality tone (before/after)
        personality_result = self._apply_personality(
            neutral_reply=neutral_reply,
            emotional_state=emotional_state,
            requested_persona=requested_persona,
        )

        return PipelineOutput(
            user_message=user_message,
            emotional_state=emotional_state,
            semantic_memory=semantic_memory,
            structured_memory=structured_memory,
            neutral_reply=neutral_reply,
            persona_name=personality_result["persona_name"],
            persona_reason=personality_result["reason"],
            final_reply=personality_result["after"],
        )

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _analyze_emotion(
        self,
        user_message: str,
    ) -> Dict[str, str | float] | None:
        """
        Use the Emotion Engine to derive the current emotional state.

        Returns:
            Dict like:
            {
                "state": "stressed" | "excited" | "neutral" | "mixed",
                "sentiment": "positive" | "negative" | "neutral",
                "emotion": "fear" | "joy" | "anger" | "sadness" | "neutral",
                "confidence": float,
            }
            or None if no emotion_analyzer is configured.
        """
        if self.emotion_analyzer is None:
            return None

        try:
            return self.emotion_analyzer.analyze(user_message)
        except Exception:
            # Fail-soft: do not break the pipeline if emotion analysis fails
            return None

    def _retrieve_memory_context(
        self,
        user_message: str,
        top_k: int = 5,
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Retrieve relevant memories for the current message.

        Combines:
        - semantic_memory: from vector DB (if configured)
        - structured_memory: from JSON/DB memory store (if configured)
        """
        semantic_memory: List[Dict[str, Any]] = []
        structured_memory: Dict[str, Any] = {}

        # Semantic from vector DB (if any)
        if self.vector_store is not None:
            try:
                # Expected shape: list of dicts with at least "text" field
                semantic_memory = self.vector_store.search(
                    query=user_message,
                    top_k=top_k,
                )
            except Exception:
                semantic_memory = []

        # Structured memory (facts, preferences, patterns)
        if self.memory_store is not None:
            try:
                # Expected to return something like:
                # {
                #   "preferences": [...],
                #   "emotional_patterns": [...],
                #   "facts": [...]
                # }
                structured_memory = self.memory_store.get_all()
            except Exception:
                structured_memory = {}

        return semantic_memory, structured_memory

    def _generate_neutral_reply(
        self,
        user_message: str,
        semantic_memory: List[Dict[str, Any]],
        structured_memory: Dict[str, Any],
    ) -> str:
        """
        Generate a neutral, content-focused reply using the LLM.

        This step:
        - Uses the user message + selected memories as context
        - Avoids any stylistic personality choices
        - Focuses purely on being accurate, helpful, and concise
        """
        # Format memory into a compact, LLM-friendly string
        memory_context_lines: List[str] = []

        if structured_memory:
            memory_context_lines.append("Structured memory:")
            for key, value in structured_memory.items():
                memory_context_lines.append(f"- {key}: {value}")

        if semantic_memory:
            memory_context_lines.append("\nRelevant past snippets:")
            for item in semantic_memory:
                text = item.get("text") or item.get("content") or ""
                if text:
                    memory_context_lines.append(f"- {text}")

        memory_context_str = "\n".join(memory_context_lines) if memory_context_lines else "None."

        system_prompt = (
            "You are an AI assistant generating a neutral, content-focused reply.\n"
            "You have access to:\n"
            "- The user's latest message\n"
            "- A summary of relevant memories (preferences, patterns, facts)\n"
            "- Retrieved past snippets\n\n"
            "Your goals:\n"
            "- Be accurate, clear, and helpful.\n"
            "- Do NOT adopt any particular persona or stylistic tone.\n"
            "- Avoid humor or emotional flourishes; keep the tone neutral.\n"
            "- Keep the response reasonably concise while complete.\n"
        )

        user_prompt = f"""
User message:
{user_message}

Memory context:
{memory_context_str}

Now, produce a neutral reply that directly addresses the user's message,
optionally using relevant memory context when appropriate.
"""

        reply = self.llm_client.generate(
            user_prompt=user_prompt.strip(),
            system_prompt=system_prompt.strip(),
            temperature=0.3,
            max_tokens=512,
        )

        return reply.strip()

    def _apply_personality(
        self,
        neutral_reply: str,
        emotional_state: Dict[str, str | float] | None,
        requested_persona: Optional[PersonaName],
    ) -> Dict[str, Any]:
        """
        Delegate to the Personality Engine to transform the neutral reply
        into a persona-styled reply (before/after).
        """
        result = apply_personality(
            neutral_reply=neutral_reply,
            emotional_state=emotional_state,
            requested_persona=requested_persona,
            llm_client=self.llm_client,
        )
        return result


