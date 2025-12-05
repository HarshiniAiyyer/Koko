from __future__ import annotations

from fastapi import APIRouter, HTTPException
from app.models.memory import (
    MemoryExtractRequest,
    MemoryExtractResponse,
    MemoryGetResponse,
    MemoryItem,
)
from app.core.memory_engine import run_memory_pipeline
from app.core.memory_engine.storage.memory_store import load_memory_output

router = APIRouter()


@router.post("/memory/extract", response_model=MemoryExtractResponse)
async def extract_memory(request: MemoryExtractRequest):
    """
    Extract structured memory from a list of user messages.
    
    Runs the full memory pipeline:
    1. LLM-based extraction
    2. Confidence scoring
    3. Cleanup & deduplication
    4. Persistence to JSON and Qdrant
    """
    try:
        # Run memory pipeline
        memory_output = run_memory_pipeline(request.messages)
        
        # Convert to API response format
        def to_api_item(item):
            return MemoryItem(
                type=item.type,
                content=item.content,
                confidence=item.confidence,
                evidence_indices=item.evidence_indices,
            )
        
        return MemoryExtractResponse(
            preferences=[to_api_item(item) for item in memory_output.preferences],
            patterns=[to_api_item(item) for item in memory_output.patterns],
            facts=[to_api_item(item) for item in memory_output.facts],
            stats=memory_output.stats.model_dump(),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory extraction failed: {str(e)}")


@router.get("/memory", response_model=MemoryGetResponse)
async def get_memory():
    """
    Get stored memory from disk.
    
    Returns the last extracted memory from data/memory.json
    """
    try:
        memory_output = load_memory_output()
        
        if memory_output is None:
            return MemoryGetResponse(
                preferences=[],
                patterns=[],
                facts=[],
                stats={},
                total_items=0,
            )
        
        def to_api_item(item):
            return MemoryItem(
                type=item.type,
                content=item.content,
                confidence=item.confidence,
                evidence_indices=item.evidence_indices,
            )
        
        total = len(memory_output.preferences) + len(memory_output.patterns) + len(memory_output.facts)
        
        return MemoryGetResponse(
            preferences=[to_api_item(item) for item in memory_output.preferences],
            patterns=[to_api_item(item) for item in memory_output.patterns],
            facts=[to_api_item(item) for item in memory_output.facts],
            stats=memory_output.stats.model_dump(),
            total_items=total,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load memory: {str(e)}")
