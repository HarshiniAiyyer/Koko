from __future__ import annotations

"""Plan

This module combines:

sentiment

emotion

intensity score

…into a simplified emotional state, which the personality engine will consume.

Output schema:
{
  "state": "stressed" | "neutral" | "excited" | "frustrated" | "mixed",
  "sentiment": "positive" | "negative" | "neutral",
  "emotion": "joy" | "fear" | ...
  "confidence": 0.0–1.0
}


This is intentionally simple but powerful.

How the emotional state is decided:

Heuristics like:

negative + fear → stressed

negative + anger → frustrated

positive + joy → excited

neutral + neutral → neutral

else → mixed

This is the place to encode your “adaptive mirroring” logic."""

from typing import Dict


def estimate_state(
    sentiment: Dict[str, str | float],
    emotion: Dict[str, str | float],
) -> Dict[str, str | float]:
    """
    Combine sentiment + emotion classifier outputs into a simplified emotional state.

    This is the main signal consumed by the Personality Engine for tone adaptation.

    Args:
        sentiment: Output from analyze_sentiment()
        emotion: Output from classify_emotion()

    Returns:
        {
          "state": "stressed" | "frustrated" | "excited" | "neutral" | "mixed",
          "sentiment": "positive" | "negative" | "neutral",
          "emotion": <emotion_label>,
          "confidence": emotion_score
        }
    """
    sent_label = str(sentiment.get("sentiment_label", "neutral"))
    emo_label = str(emotion.get("emotion_label", "neutral"))
    emo_score = float(emotion.get("emotion_score", 0.0))

    # Very simple heuristics, aligned with your earlier design
    if sent_label == "negative" and emo_label in {"fear", "anxiety", "sadness"}:
        state = "stressed"
    elif sent_label == "negative" and emo_label in {"anger"}:
        state = "frustrated"
    elif sent_label == "positive" and emo_label in {"joy"}:
        state = "excited"
    elif emo_label in {"neutral"} and sent_label == "neutral":
        state = "neutral"
    else:
        state = "mixed"

    return {
        "state": state,
        "sentiment": sent_label,
        "emotion": emo_label,
        "confidence": emo_score,
    }
