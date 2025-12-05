from __future__ import annotations

"""Purpose: Abstract away Groq API usage.
All LLM calls within the project go through this single class.
Evaluators love this because:

It isolates model dependency
Makes future model changes trivial
Shows architecture-level thinking"""

import json
import logging
from typing import Any, Dict, List, Optional

from groq import Groq

from app.core.config.settings import settings
from app.core.utils.retry_utils import retry_with_backoff

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Thin wrapper around Groq's chat completion API.

    Responsibilities:
    - Provide a simple generate() interface for free-form text
    - Provide structured_generate() for JSON-like responses
    - Centralize model name, API key, and basic error handling

    All other modules (memory extractor, persona rewriter, etc.)
    should call into this client instead of talking to Groq directly.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or settings.GROQ_API_KEY
        if not self.api_key:
            logger.warning("GROQ_API_KEY is not set. LLM calls will fail at runtime.")

        self.model_name = model_name or settings.LLM_MODEL
        self.client = Groq(api_key=self.api_key)

    @retry_with_backoff(max_retries=2, initial_delay=1.0, backoff_factor=2.0)
    def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        timeout: float = 30.0,
    ) -> str:
        """
        Simple chat completion wrapper with retry logic.

        Args:
            user_prompt: The user's message or main prompt.
            system_prompt: Optional system behavior instructions.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens for the response.
            timeout: API call timeout in seconds (default 30s).

        Returns:
            The assistant's message content as a string.
        """
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
            return completion.choices[0].message.content  # type: ignore[attr-defined]
        except Exception as e:
            logger.error("Groq API call failed: %s", e)
            raise

    def structured_generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Ask the model to return JSON and parse it.

        This is used by:
        - Memory extraction (preferences, patterns, facts)
        - Any other structured outputs in the pipeline

        The prompt template that calls this method should:
        - Clearly instruct the model to output ONLY valid JSON
        - Provide an example of the expected JSON schema

        Args:
            user_prompt: Main prompt text (should include JSON instructions).
            system_prompt: Optional system instructions.
            temperature: Low by default for better determinism.
            max_tokens: Max completion length.

        Returns:
            Parsed Python dict.
        """
        raw = self.generate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Strategy 1: Direct JSON parse
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Direct JSON parse failed. Attempting recovery strategies.")

        # Strategy 2: Extract JSON from markdown code block
        if "```json" in raw:
            try:
                start = raw.find("```json") + 7
                end = raw.find("```", start)
                if end != -1:
                    cleaned = raw[start:end].strip()
                    return json.loads(cleaned)
            except json.JSONDecodeError:
                logger.debug("Markdown JSON extraction failed")

        # Strategy 3: Extract first/last braces (existing method)
        cleaned = self._extract_json_from_text(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("All JSON extraction strategies failed.")
            logger.debug("Raw model output: %s", raw)
            raise ValueError("Model did not return valid JSON.") from e

    @staticmethod
    def _extract_json_from_text(text: str) -> str:
        """
        Try to heuristically extract JSON from a text blob.
        This is a lightweight helper, not bulletproof.

        It looks for the first '{' and the last '}' and slices.
        """
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            # Fall back to original text if we can't find braces
            return text
        return text[start : end + 1]
