from app.core.config import Settings


def test_config_defaults():
    settings = Settings()
    assert settings.PROJECT_NAME == "SourceIQ"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.EMBEDDING_DIMENSIONS == 768
    assert settings.SIMILARITY_THRESHOLD == 0.65
    assert settings.LLM_PROVIDER in ["gemini", "openai", "ollama"]
    assert settings.EMBEDDING_PROVIDER in ["gemini", "openai", "ollama"]


def test_cors_origin_parsing():
    settings = Settings(CORS_ORIGINS="http://localhost:3000, http://127.0.0.1:3000 , https://app.sourceiq.ai")
    origins = settings.cors_origin_list
    assert len(origins) == 3
    assert "http://localhost:3000" in origins
    assert "http://127.0.0.1:3000" in origins
    assert "https://app.sourceiq.ai" in origins
