from __future__ import annotations

"""Plan:

Function:

retrieve_relevant_memory(query: str, top_k: int = 5)


Steps:

Embed query

Query Qdrant collection

Return MemoryItems sorted by score

This is used during response generation to pull relevant memory."""

import os
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config.settings import settings
from app.core.models import EmbeddingModel
from app.core.memory_engine.schemas.memory_item import MemoryItem


def _get_qdrant_client() -> QdrantClient:
    """
    Get Qdrant client with support for both local and cloud instances.
    
    For Qdrant Cloud, set QDRANT_API_KEY in .env file.
    """
    api_key = os.getenv("QDRANT_API_KEY")
    
    # Determine if using HTTPS (cloud) or HTTP (local)
    use_https = api_key is not None or settings.QDRANT_PORT == 443
    
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        api_key=api_key,
        https=use_https,
    )


def retrieve_relevant_memory(
    query: str,
    top_k: int = 5,
) -> List[MemoryItem]:
    """
    Retrieve top-k memory items semantically similar to the query.

    Args:
        query: Natural language query (e.g. the user's new message).
        top_k: Maximum number of memory items to return.

    Returns:
        List of MemoryItem instances constructed from Qdrant payloads.
    """
    client = _get_qdrant_client()
    embedder = EmbeddingModel()

    query_vec = embedder.embed_text(query)
    if not query_vec:
        return []

    search_result = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=query_vec,
        limit=top_k,
        with_payload=True,
    )

    items: List[MemoryItem] = []
    for point in search_result:
        payload = point.payload or {}
        item_type = payload.get("type", "fact")
        content = payload.get("content", "")
        confidence = payload.get("confidence", "medium")
        evidence_indices = payload.get("evidence_indices", [])

        if not content:
            continue

        items.append(
            MemoryItem(
                type=item_type,
                content=content,
                confidence=confidence,
                evidence_indices=evidence_indices,
            )
        )

    return items
