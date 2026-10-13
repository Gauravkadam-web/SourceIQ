import pytest
from app.core.config import settings
from app.core.errors import ProviderError
from app.providers.factory import get_llm_provider, get_embedding_provider
from app.providers.gemini_provider import GeminiLLMProvider, GeminiEmbeddingProvider
from app.providers.openai_provider import OpenAILLMProvider, OpenAIEmbeddingProvider


def test_gemini_provider_resolution(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "EMBEDDING_PROVIDER", "gemini")

    llm = get_llm_provider()
    embedding = get_embedding_provider()

    assert isinstance(llm, GeminiLLMProvider)
    assert isinstance(embedding, GeminiEmbeddingProvider)
    assert embedding.dimension == settings.EMBEDDING_DIMENSIONS


def test_openai_provider_resolution(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(settings, "EMBEDDING_PROVIDER", "openai")

    llm = get_llm_provider()
    embedding = get_embedding_provider()

    assert isinstance(llm, OpenAILLMProvider)
    assert isinstance(embedding, OpenAIEmbeddingProvider)


def test_unsupported_provider_raises_error(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "unsupported_llm")
    with pytest.raises(ProviderError):
        get_llm_provider()
