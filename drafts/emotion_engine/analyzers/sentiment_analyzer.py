from __future__ import annotations

"""This folder breaks the emotional inference into two simple, testable units.
sentiment_analyzer.py
Plan

Uses EmotionModel.get_sentiment() to produce:

{
  "sentiment_label": "positive" | "negative" | "neutral",
  "sentiment_score": 0.0–1.0
}

This file:

wraps the raw transformers output

normalizes edge cases

provides clean debugging logs"""

from typing import Dict

from core_ai.models import EmotionModel

# Singleton-ish instance to avoid reloading pipelines repeatedly
_emotion_model: EmotionModel | None = None


def _get_model() -> EmotionModel:
    global _emotion_model
    if _emotion_model is None:
        _emotion_model = EmotionModel()
    return _emotion_model


def analyze_sentiment(text: str) -> Dict[str, str | float]:
    """
    Run coarse sentiment analysis on a single text.

    Returns:
        {
          "sentiment_label": "positive" | "negative" | "neutral",
          "sentiment_score": float in [0,1]
        }
    """
    model = _get_model()
    result = model.get_sentiment(text)
    label = str(result.get("label", "neutral"))
    score = float(result.get("score", 0.0))

    # Normalize any unexpected labels
    if label not in {"positive", "negative", "neutral"}:
        label = "neutral"

    return {
        "sentiment_label": label,
        "sentiment_score": score,
    }
