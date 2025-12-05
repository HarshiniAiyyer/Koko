from __future__ import annotations

"""Export:

analyze_emotion

estimate_state

This creates a clean top-level API.
"""
"""
Emotion Engine

High-level interface for:

- Running sentiment and emotion analysis on a message
- Estimating a simplified emotional state that the Personality Engine
  can use to adapt tone (e.g., stressed → calm mentor).
"""

from typing import Dict

from app.core.models.emotion_model import EmotionModel

# Singleton instance for efficiency
_emotion_model = EmotionModel()


def analyze_emotion(message: str) -> Dict[str, str | float]:
    """
    Convenience function that runs sentiment + emotion + state estimation
    in a single call using the LLM-based EmotionModel.

    Args:
        message: The user's message text.

    Returns:
        Dict with keys: state, sentiment, emotion, confidence.
    """
    return _emotion_model.estimate_state(message)


__all__ = ["analyze_emotion", "estimate_state", "analyze_sentiment", "classify_emotion"]
