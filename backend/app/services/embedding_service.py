from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.core.errors import ProviderError
from app.core.logging import logger
from app.providers.factory import get_embedding_provider


class EmbeddingService:
    BATCH_SIZE: int = 16

    @classmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0),
        retry=retry_if_exception_type(ProviderError),
        reraise=True,
    )
    async def generate_chunk_embeddings(cls, texts: List[str]) -> List[List[float]]:
        """
        Generates dense vector embeddings for chunk texts in batches of 16.
        Uses the pluggable embedding provider configured in .env.
        """
        if not texts:
            return []

        provider = get_embedding_provider()
        all_embeddings: List[List[float]] = []

        for i in range(0, len(texts), cls.BATCH_SIZE):
            batch = texts[i : i + cls.BATCH_SIZE]
            logger.info(f"Generating embeddings for batch {i // cls.BATCH_SIZE + 1} ({len(batch)} chunks)")
            batch_vectors = await provider.embed_texts(batch)
            all_embeddings.extend(batch_vectors)

        return all_embeddings

    @classmethod
    async def generate_query_embedding(cls, query: str) -> List[float]:
        """Generates embedding for a single user query."""
        provider = get_embedding_provider()
        return await provider.embed_query(query)
