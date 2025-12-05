from __future__ import annotations

"""Purpose:
Make orchestrator-level utilities easy to import.

Exports:

ResponsePipeline

PipelineOutput

Nothing else.

This is a simple file."""

"""
Orchestrator

High-level pipeline that wires together:
- Memory Engine
- Emotion Engine
- Personality Engine
- LLM core

The primary entrypoint is `ResponsePipeline`, which:
1) Analyzes emotional state
2) Retrieves relevant memories
3) Generates a neutral, content-focused reply
4) Applies personality tone (before/after)
"""

from core_ai.orchestrator.response_pipeline import PipelineOutput, ResponsePipeline

__all__ = ["PipelineOutput", "ResponsePipeline"]
