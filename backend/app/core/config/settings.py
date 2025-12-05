import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

class Settings:
    """
    Centralized configuration for models, vector DB, thresholds, and file paths.
    """

    # --- API Keys ---
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
    HF_API_TOKEN: str | None = os.getenv("HF_API_TOKEN")

    # --- LLM Model Config ---
    # Recommended: Llama3 70B or Mixtral via Groq
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3-8b-8192")

    # --- Embeddings ---
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    # --- Vector DB (Qdrant) ---
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION: str = os.getenv(
        "QDRANT_COLLECTION", "user_memory"
    )

    # --- Confidence thresholds ---
    HIGH_CONFIDENCE_THRESHOLD: float = float(
        os.getenv("HIGH_CONFIDENCE_THRESHOLD", 0.75)
    )
    MEDIUM_CONFIDENCE_THRESHOLD: float = float(
        os.getenv("MEDIUM_CONFIDENCE_THRESHOLD", 0.40)
    )

    # --- File Paths ---
    MEMORY_JSON_PATH: str = os.getenv(
        "MEMORY_JSON_PATH", "data/memory.json"
    )

settings = Settings()
