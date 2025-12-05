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
from core_ai.models import LLMClient, EmbeddingModel, EmotionModel
from core_ai.orchestrator import ResponsePipeline, PipelineOutput
from core_ai.memory_engine import (
    extract_memory,
    run_memory_pipeline,
    retrieve_relevant_memory,
)
from core_ai.personality_engine import apply_personality
from core_ai.emotion_engine import analyze_emotion
from core_ai.config import settings

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
