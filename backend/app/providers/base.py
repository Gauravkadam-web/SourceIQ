from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel


class LLMProviderInterface(ABC):
    """Abstract interface for LLM question-answering generation."""

    @abstractmethod
    async def generate_grounded_answer(
        self,
        system_instruction: str,
        user_prompt: str,
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        """Generates grounded answer with structured citation format."""
        pass


class EmbeddingProviderInterface(ABC):
    """Abstract interface for dense vector embedding generation."""

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text chunks."""
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """Generates embedding for a single user search query."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the output vector dimension for this embedding model."""
        pass
