"""
Core AI Package - Emotionally Intelligent Conversational Systems

This package provides a sophisticated AI system that combines:
- Emotional intelligence (sentiment and emotion analysis)
- Long-term memory (extraction, storage, and retrieval)
- Adaptive personality (persona selection and tone rewriting)
- Intelligent orchestration (end-to-end response pipeline)
"""

__version__ = "0.1.0"

# Re-export commonly used components for convenience
from app.core.models import LLMClient, EmbeddingModel, EmotionModel
from app.core.orchestrator import ResponsePipeline, PipelineOutput
from app.core.memory_engine import (
    extract_memory,
    run_memory_pipeline,
    retrieve_relevant_memory,
)
from app.core.personality_engine import apply_personality
from app.core.emotion_engine import analyze_emotion
from app.core.config import settings

__all__ = [
    # Core Models
    "LLMClient",
    "EmbeddingModel",
    "EmotionModel",
    # Orchestrator
    "ResponsePipeline",
    "PipelineOutput",
    # Memory Engine
    "extract_memory",
    "run_memory_pipeline",
    "retrieve_relevant_memory",
    # Personality Engine
    "apply_personality",
    # Emotion Engine
    "analyze_emotion",
    # Configuration
    "settings",
]
