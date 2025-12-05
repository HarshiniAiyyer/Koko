from __future__ import annotations

"""Purpose: Given a message, detect:
sentiment (positive, negative, neutral)
emotion class (anger, fear, joy, sadness, etc.)
arousal (optional simple score)
This feeds directly into the Personality Auto-Selector.

UPDATED: Now uses LLM (Llama 3) for context-aware classification.
"""

from typing import Dict, Any

from app.core.models.llm_client import LLMClient


class EmotionModel:
    """
    Wraps LLMClient to perform context-aware emotion classification.
    Replaces the old Hugging Face pipeline for better accuracy on nuanced inputs.
    """

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def estimate_state(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using LLM to determine emotional state.
        
        Returns:
        {
            "state": "stressed" | "frustrated" | "excited" | "neutral" | "mixed",
            "sentiment": "positive" | "negative" | "neutral",
            "emotion": "joy" | "fear" | "anger" | "sadness" | "neutral",
            "confidence": float
        }
        """
        if not text.strip():
            return {
                "state": "neutral",
                "sentiment": "neutral",
                "emotion": "neutral",
                "confidence": 0.0
            }

        system_prompt = """You are an expert emotion classifier.
Analyze the user's message and determine the emotional state.

Output strictly valid JSON with this schema:
{
    "state": "stressed" | "frustrated" | "excited" | "neutral" | "mixed" | "sadness",
    "sentiment": "positive" | "negative" | "neutral",
    "emotion": "joy" | "fear" | "anger" | "sadness" | "neutral" | "anxiety",
    "confidence": 0.0 to 1.0
}

CRITICAL RULES:
- If the user mentions a major positive life event (e.g., marriage proposal, promotion, new job, winning), classify as "excited" / "joy".
- Example: "My boyfriend said yes to being my husband" -> state: "excited", emotion: "joy", sentiment: "positive".
- Be sensitive to context and nuance.
"""

        user_prompt = f"""Classify this text:
"{text}"

Return only the JSON object."""

        try:
            result = self.llm_client.structured_generate(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1, # Low temperature for consistent classification
                max_tokens=128
            )
            return result
        except Exception as e:
            print(f"Emotion Classification Failed: {e}")
            # Fallback
            return {
                "state": "neutral",
                "sentiment": "neutral",
                "emotion": "neutral",
                "confidence": 0.0
            }

    # Legacy methods for compatibility (optional, but good to keep if other parts call them)
    def get_sentiment(self, text: str) -> Dict[str, float | str]:
        res = self.estimate_state(text)
        return {"label": res["sentiment"], "score": res["confidence"]}

    def get_emotion(self, text: str) -> Dict[str, float | str]:
        res = self.estimate_state(text)
        return {"label": res["emotion"], "score": res["confidence"]}
