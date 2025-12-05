from __future__ import annotations

""" #### vector store.py
Plan:

Create Qdrant collection if missing

Upsert memory items:

use embedding model to generate vector

attach metadata:

type

confidence

content

Provide helper:
store_memory_items(items: List[MemoryItem])"""

import logging
import os
import uuid
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config.settings import settings
from app.core.models import EmbeddingModel
from app.core.memory_engine.schemas.memory_output import MemoryOutput
from app.core.memory_engine.schemas.memory_item import MemoryItem

logger = logging.getLogger(__name__)


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


def _ensure_collection(client: QdrantClient, vector_size: int) -> None:
    """
    Ensure that the Qdrant collection for user memory exists.
    If not, create it.
    """
    collections = client.get_collections().collections
    names = {c.name for c in collections}
    if settings.QDRANT_COLLECTION in names:
        return

    logger.info("Creating Qdrant collection '%s'", settings.QDRANT_COLLECTION)
    client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=qmodels.VectorParams(
            size=vector_size,
            distance="Cosine",
        ),
    )


def _memory_item_to_payload(item: MemoryItem) -> dict:
    """
    Convert a MemoryItem to a Qdrant payload dict.
    """
    return {
        "type": item.type,
        "content": item.content,
        "confidence": item.confidence,
        "evidence_indices": item.evidence_indices or [],
    }


def store_memory_items(memory_output: MemoryOutput) -> None:
    """
    Embed and store all memory items in Qdrant.

    This is called after cleanup, so memory output is deduplicated.

    Args:
        memory_output: Final MemoryOutput to index.
    """
    client = _get_qdrant_client()
    embedder = EmbeddingModel()

    all_items: List[MemoryItem] = (
        list(memory_output.preferences)
        + list(memory_output.patterns)
        + list(memory_output.facts)
    )

    if not all_items:
        logger.info("No memory items to store in vector DB.")
        return

    contents = [item.content for item in all_items]
    vectors = embedder.embed_batch(contents)

    # Ensure collection is ready
    vector_size = len(vectors[0]) if vectors else 0
    if vector_size == 0:
        logger.warning("Embedding vector size is 0. Skipping Qdrant storage.")
        return

    _ensure_collection(client, vector_size)

    points = []
    for item, vector in zip(all_items, vectors):
        payload = _memory_item_to_payload(item)
        point_id = str(uuid.uuid4())
        points.append(
            qmodels.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
        )

    client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points,
    )
    logger.info("Stored %d memory items in Qdrant.", len(points))
