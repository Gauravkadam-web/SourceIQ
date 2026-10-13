import json
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from openai import OpenAI
from app.core.config import settings
from app.core.errors import ProviderError
from app.core.logging import logger
from app.providers.base import LLMProviderInterface, EmbeddingProviderInterface


class OpenAILLMProvider(LLMProviderInterface):
    """OpenAI LLM provider implementation (Alternative / Plug-and-play)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_LLM_MODEL
        if not self.api_key:
            logger.warning("OPENAI_API_KEY is not set. OpenAI calls will fail until configured.")

    def _get_client(self) -> OpenAI:
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is required to invoke OpenAI LLM.")
        return OpenAI(api_key=self.api_key)

    async def generate_grounded_answer(
        self,
        system_instruction: str,
        user_prompt: str,
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        try:
            client = self._get_client()
            messages = [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ]
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,
            }
            if response_schema:
                kwargs["response_format"] = {"type": "json_object"}

            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or "{}"
            if response_schema:
                try:
                    return json.loads(content)
                except Exception:
                    return {"answer": content, "status": "GROUNDED", "citations": []}
            return {"answer": content}
        except Exception as e:
            logger.error(f"OpenAI LLM error: {str(e)}")
            raise ProviderError(f"OpenAI generation failed: {str(e)}")


class OpenAIEmbeddingProvider(EmbeddingProviderInterface):
    """OpenAI embedding provider implementation (text-embedding-3-small)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_EMBEDDING_MODEL
        self._dim = 1536

    def _get_client(self) -> OpenAI:
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is required to generate OpenAI embeddings.")
        return OpenAI(api_key=self.api_key)

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            client = self._get_client()
            response = client.embeddings.create(input=texts, model=self.model)
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding batch error: {str(e)}")
            raise ProviderError(f"OpenAI embedding generation failed: {str(e)}")

    async def embed_query(self, query: str) -> List[float]:
        try:
            client = self._get_client()
            response = client.embeddings.create(input=[query], model=self.model)
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI query embedding error: {str(e)}")
            raise ProviderError(f"OpenAI query embedding failed: {str(e)}")
