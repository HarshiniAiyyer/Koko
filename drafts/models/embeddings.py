from __future__ import annotations

"""Central module for generating embeddings for:
user messages, memory items, personality descriptors, emotional features (optional)

We will use Sentence Transformers (BGE-large) since its:

- open-source
- high-performing
- excellent for semantic memory"""

from typing import List, Sequence

from sentence_transformers import SentenceTransformer

from core_ai.config.settings import settings


class EmbeddingModel:
    """
    Wrapper around an open-source sentence-transformers model
    (e.g. BAAI/bge-large-en-v1.5) used for:

    - Embedding user messages
    - Embedding extracted memory items
    - Embedding any auxiliary text we want to store in Qdrant

    This class is intentionally thin and stateless aside from
    the underlying model instance.
    """

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        """
        Lazy-load the embedding model on first use.
        """
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """
        Compute a vector embedding for a single text string.

        Args:
            text: Input text.

        Returns:
            List[float]: Dense embedding vector.
        """
        if not text:
            return []
        # sentence-transformers returns a numpy array; convert to list for JSON compatibility
        vec = self.model.encode(text)
        return vec.tolist()

    def embed_batch(self, texts: Sequence[str]) -> List[List[float]]:
        """
        Compute embeddings for a batch of texts.

        Args:
            texts: Iterable of input strings.

        Returns:
            List of embedding vectors (each List[float]).
        """
        if not texts:
            return []
        vecs = self.model.encode(list(texts))
        # vecs is a 2D numpy array; convert each row to list
        return [v.tolist() for v in vecs]
