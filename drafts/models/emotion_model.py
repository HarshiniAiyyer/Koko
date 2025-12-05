from __future__ import annotations

"""Purpose: Given a message, detect:
sentiment (positive, negative, neutral)
emotion class (anger, fear, joy, sadness, etc.)
arousal (optional simple score)
This feeds directly into the Personality Auto-Selector."""

from typing import Dict

from transformers import pipeline


class EmotionModel:
    """
    Wraps open-source transformer pipelines for:

    - Sentiment analysis (positive / negative / neutral)
    - Emotion classification (joy, sadness, anger, etc.)
    - High-level emotional state estimation, which is later
      used by the Personality Engine to choose an appropriate tone.

    This is deliberately simple but expressive enough to power
    your "adaptive mirroring" idea.
    """

    def __init__(self) -> None:
        # Lazy-initialized members
        self._sentiment_pipe = None
        self._emotion_pipe = None

    @property
    def sentiment_pipe(self):
        """
        Pipeline for coarse sentiment: positive / negative / neutral.
        """
        if self._sentiment_pipe is None:
            # You can swap this with any other sentiment model.
            self._sentiment_pipe = pipeline(
                "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
            )
        return self._sentiment_pipe

    @property
    def emotion_pipe(self):
        """
        Pipeline for fine-grained emotions (joy, fear, anger, etc.).
        """
        if self._emotion_pipe is None:
            # A commonly used multi-class emotion model
            self._emotion_pipe = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=False,
            )
        return self._emotion_pipe

    def get_sentiment(self, text: str) -> Dict[str, float | str]:
        """
        Run sentiment analysis on a single text.

        Returns:
            dict with keys: label (str) and score (float)
        """
        if not text.strip():
            return {"label": "neutral", "score": 0.0}

        result = self.sentiment_pipe(text)[0]
        # result contains {"label": "POSITIVE"/"NEGATIVE", "score": float}
        return {"label": result["label"].lower(), "score": float(result["score"])}

    def get_emotion(self, text: str) -> Dict[str, float | str]:
        """
        Run emotion classification on a single text.

        Returns:
            dict with keys: label (str) and score (float)
        """
        if not text.strip():
            return {"label": "neutral", "score": 0.0}

        result = self.emotion_pipe(text)[0]
        # result contains {"label": "joy"/"anger"/..., "score": float}
        return {"label": result["label"].lower(), "score": float(result["score"])}

    def estimate_state(self, text: str) -> Dict[str, float | str]:
        """
        Combine sentiment and emotion into a simplified emotional state
        that the Personality Engine can consume.

        Example output:
        {
            "state": "stressed",
            "sentiment": "negative",
            "emotion": "fear",
            "confidence": 0.82
        }
        """
        sentiment = self.get_sentiment(text)
        emotion = self.get_emotion(text)

        sent_label = str(sentiment["label"])
        emo_label = str(emotion["label"])
        emo_score = float(emotion["score"])

        # Very lightweight heuristic mapping
        if sent_label == "negative" and emo_label in {"fear", "anxiety", "sadness"}:
            state = "stressed"
        elif sent_label == "negative" and emo_label in {"anger"}:
            state = "frustrated"
        elif sent_label == "positive" and emo_label in {"joy"}:
            state = "excited"
        elif emo_label in {"neutral"}:
            state = "neutral"
        else:
            state = "mixed"

        return {
            "state": state,
            "sentiment": sent_label,
            "emotion": emo_label,
            "confidence": emo_score,
        }
