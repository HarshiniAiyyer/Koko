from __future__ import annotations

"""Plan

Calls EmotionModel.get_emotion() to produce:

{
  "emotion_label": "joy" | "fear" | "anger" | ...,
  "emotion_score": 0.0–1.0
}


Also:

Handles empty text

Normalizes classification

Guarantees consistent schema"""

from typing import Dict

from app.core.models import EmotionModel

# Reuse same EmotionModel instance as sentiment analyzer
_emotion_model: EmotionModel | None = None


def _get_model() -> EmotionModel:
    global _emotion_model
    if _emotion_model is None:
        _emotion_model = EmotionModel()
    return _emotion_model


def classify_emotion(text: str) -> Dict[str, str | float]:
    """
    Run fine-grained emotion classification on a single text.

    Returns:
        {
          "emotion_label": "joy" | "fear" | "anger" | "sadness" | ... | "neutral",
          "emotion_score": float in [0,1]
        }
    """
    model = _get_model()
    result = model.get_emotion(text)
    label = str(result.get("label", "neutral"))
    score = float(result.get("score", 0.0))

    return {
        "emotion_label": label,
        "emotion_score": score,
    }
