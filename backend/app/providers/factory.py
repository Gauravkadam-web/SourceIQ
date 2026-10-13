from app.core.config import settings
from app.core.errors import ProviderError
from app.providers.base import LLMProviderInterface, EmbeddingProviderInterface
from app.providers.gemini_provider import GeminiLLMProvider, GeminiEmbeddingProvider
from app.providers.openai_provider import OpenAILLMProvider, OpenAIEmbeddingProvider


def get_llm_provider() -> LLMProviderInterface:
    """Factory creating the configured LLM provider directly from .env configuration."""
    provider_name = settings.LLM_PROVIDER.lower()
    if provider_name == "gemini":
        return GeminiLLMProvider()
    elif provider_name == "openai":
        return OpenAILLMProvider()
    else:
        raise ProviderError(f"Unsupported LLM provider configured: '{settings.LLM_PROVIDER}'")


def get_embedding_provider() -> EmbeddingProviderInterface:
    """Factory creating the configured Embedding provider directly from .env configuration."""
    provider_name = settings.EMBEDDING_PROVIDER.lower()
    if provider_name == "gemini":
        return GeminiEmbeddingProvider()
    elif provider_name == "openai":
        return OpenAIEmbeddingProvider()
    else:
        raise ProviderError(f"Unsupported Embedding provider configured: '{settings.EMBEDDING_PROVIDER}'")
