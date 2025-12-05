from __future__ import annotations

"""Central module for generating embeddings.

UPDATED: Now uses Hugging Face Inference API by default for zero-startup latency.
Falls back to local SentenceTransformer if API fails or token is missing.
"""

import logging
import time
from typing import List, Sequence, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

from app.core.config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """
    Hybrid Embedding Model:
    1. Tries HF Inference API (Fast, no RAM usage)
    2. Falls back to local SentenceTransformer (Robust, offline capable)
    """

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model: "SentenceTransformer" | None = None
        self.api_token = settings.HF_API_TOKEN
        # Standard HF Inference API URL for feature extraction
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model_name}"

    @property
    def model(self) -> "SentenceTransformer":
        """
        Lazy-load the local embedding model only if absolutely necessary.
        """
        if self._model is None:
            logger.info("Loading local SentenceTransformer model (Fallback)...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _call_api(self, texts: List[str]) -> List[List[float]] | None:
        """
        Attempt to get embeddings from HF API.
        Returns None if failed, so we can fallback.
        """
        if not self.api_token:
            return None

        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {"inputs": texts, "options": {"wait_for_model": True}}

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"HF API Error {response.status_code}: {response.text}")
                return None
                
            data = response.json()
            
            # HF API returns varying formats depending on model/input
            # For feature-extraction with list input, it usually returns list of lists (embeddings)
            # Or sometimes a 3D array [batch, seq, dim] if not pooled? 
            # BGE models usually return pooled embeddings if using the right pipeline tag, 
            # but raw feature-extraction might return token embeddings.
            
            # Let's validate the shape. We expect List[List[float]].
            if isinstance(data, list) and len(data) > 0:
                # Check if it's a list of floats (single vector) or list of lists (batch)
                if isinstance(data[0], float):
                    # Single vector returned (shouldn't happen if we sent a list, but possible for single item)
                    return [data]
                elif isinstance(data[0], list):
                    # Check if it's [batch, dim] or [batch, seq, dim]
                    if isinstance(data[0][0], list):
                        # It's [batch, seq, dim] - we need to pool it (e.g., mean pooling)
                        # This is getting complicated. 
                        # BGE models on HF Inference API often return [batch, dim] if 'sentence-transformers' library is used on server.
                        # But if it's raw bert, it returns token embeddings.
                        
                        # Simplification: If we get 3D array, we just take the mean (CLS token is usually first, but mean is safer for general STS)
                        # Actually, for BGE, CLS is common.
                        # Let's assume the API works like sentence-transformers if the model card says so.
                        # If not, falling back to local is safer than implementing pooling here.
                        logger.warning("HF API returned 3D array (token embeddings). Falling back to local for correctness.")
                        return None
                    
                    return data
            
            return None

        except Exception as e:
            logger.warning(f"HF API Exception: {e}")
            return None

    def embed_text(self, text: str) -> List[float]:
        """
        Compute a vector embedding for a single text string.
        """
        if not text:
            return []

        # Try API first
        api_result = self._call_api([text])
        if api_result and len(api_result) == 1:
            return api_result[0]

        # Fallback to local
        vec = self.model.encode(text)
        return vec.tolist()

    def embed_batch(self, texts: Sequence[str]) -> List[List[float]]:
        """
        Compute embeddings for a batch of texts.
        """
        if not texts:
            return []
        
        text_list = list(texts)

        # Try API first
        api_result = self._call_api(text_list)
        if api_result and len(api_result) == len(text_list):
            return api_result

        # Fallback to local
        vecs = self.model.encode(text_list)
        return [v.tolist() for v in vecs]
