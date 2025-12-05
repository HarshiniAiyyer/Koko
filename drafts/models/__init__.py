#Expose:EmbeddingModel, LLMClient, EmotionModel

"""
Core model abstractions for the AI layer.

This package exposes:
- EmbeddingModel: for semantic vector representations
- LLMClient: for Groq-based LLM calls
- EmotionModel: for sentiment + emotion classification
"""

from .embeddings import EmbeddingModel
from .llm_client import LLMClient
from .emotion_model import EmotionModel

__all__ = ["EmbeddingModel", "LLMClient", "EmotionModel"]
