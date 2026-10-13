import json
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.errors import ProviderError
from app.core.logging import logger
from app.providers.base import LLMProviderInterface, EmbeddingProviderInterface


class GeminiLLMProvider(LLMProviderInterface):
    """Google Gemini LLM provider implementation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_LLM_MODEL
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. Gemini calls will fail until configured.")

    def _get_client(self) -> genai.Client:
        if not self.api_key:
            raise ProviderError("GEMINI_API_KEY is required to invoke Gemini LLM.")
        return genai.Client(api_key=self.api_key)

    async def generate_grounded_answer(
        self,
        system_instruction: str,
        user_prompt: str,
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        try:
            client = self._get_client()
            config_args: Dict[str, Any] = {
                "system_instruction": system_instruction,
                "temperature": 0.1,
            }
            if response_schema:
                config_args["response_mime_type"] = "application/json"
                config_args["response_schema"] = response_schema

            config = types.GenerateContentConfig(**config_args)
            response = client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config,
            )

            if response_schema:
                try:
                    return json.loads(response.text)
                except Exception:
                    return {"answer": response.text, "status": "GROUNDED", "citations": []}
            return {"answer": response.text}

        except Exception as e:
            logger.error(f"Gemini LLM error: {str(e)}")
            raise ProviderError(f"Gemini LLM generation failed: {str(e)}")


class GeminiEmbeddingProvider(EmbeddingProviderInterface):
    """Google Gemini embedding provider implementation (text-embedding-004, 768 dims)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_EMBEDDING_MODEL
        self._dim = settings.EMBEDDING_DIMENSIONS

    def _get_client(self) -> genai.Client:
        if not self.api_key:
            raise ProviderError("GEMINI_API_KEY is required to generate embeddings.")
        return genai.Client(api_key=self.api_key)

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            client = self._get_client()
            embeddings: List[List[float]] = []
            # Gemini embeds per text or batch
            for text in texts:
                result = client.models.embed_content(
                    model=self.model,
                    contents=text,
                )
                embeddings.append(result.embedding.values)
            return embeddings
        except Exception as e:
            logger.error(f"Gemini embedding batch error: {str(e)}")
            raise ProviderError(f"Gemini embedding generation failed: {str(e)}")

    async def embed_query(self, query: str) -> List[float]:
        try:
            client = self._get_client()
            result = client.models.embed_content(
                model=self.model,
                contents=query,
            )
            return result.embedding.values
        except Exception as e:
            logger.error(f"Gemini query embedding error: {str(e)}")
            raise ProviderError(f"Gemini query embedding failed: {str(e)}")
