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

from core_ai.emotion_engine.analyzers.sentiment_analyzer import analyze_sentiment
from core_ai.emotion_engine.analyzers.emotion_classifier import classify_emotion
from core_ai.emotion_engine.state.state_estimator import estimate_state


def analyze_emotion(message: str) -> Dict[str, str | float]:
    """
    Convenience function that runs sentiment + emotion + state estimation
    in a single call.

    Args:
        message: The user's message text.

    Returns:
        Dict with keys: state, sentiment, emotion, confidence.
    """
    sentiment = analyze_sentiment(message)
    emotion = classify_emotion(message)
    state = estimate_state(sentiment, emotion)
    return state


__all__ = ["analyze_emotion", "estimate_state", "analyze_sentiment", "classify_emotion"]
