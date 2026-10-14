import os
from typing import List, Literal
from pydantic import field_validator, Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "SourceIQ"
    API_V1_STR: str = "/api/v1"

    # Server Bind
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000

    # CORS Allowed Origins
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:1234@localhost:5432/sourceiq_db"

    # Storage (Local disk for development, Supabase Storage for production)
    STORAGE_BACKEND: Literal["local", "supabase"] = "local"
    STORAGE_LOCAL_DIR: str = "./data/uploads"
    SUPABASE_URL: str = Field(default="", validation_alias=AliasChoices("SUPABASE_URL", "supabase_url", "NEXT_PUBLIC_SUPABASE_URL"))
    SUPABASE_KEY: str = Field(default="", validation_alias=AliasChoices("SUPABASE_KEY", "SUPABASE_SERVICE_ROLE_KEY", "supabase_key", "supabase_service_role_key"))
    SUPABASE_STORAGE_BUCKET: str = "sourceiq-documents"
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    MAX_DOCUMENTS_PER_WORKSPACE: int = 10
    ALLOWED_MIME_TYPES: str = "application/pdf"

    # Pluggable AI Provider Architecture
    LLM_PROVIDER: Literal["gemini", "openai", "ollama"] = "gemini"
    EMBEDDING_PROVIDER: Literal["gemini", "openai", "ollama"] = "gemini"

    # Google Gemini Settings
    GEMINI_API_KEY: str = Field(default="", validation_alias=AliasChoices("GEMINI_API_KEY", "GOOGLE_API_KEY", "gemini_api_key", "google_api_key"))
    GEMINI_LLM_MODEL: str = "gemini-3.1-flash-lite"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"

    # OpenAI Settings (Alternative / Switch)
    OPENAI_API_KEY: str = ""
    OPENAI_LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Vector & Retrieval
    EMBEDDING_DIMENSIONS: int = 768
    SIMILARITY_THRESHOLD: float = 0.48
    TOP_K_RETRIEVAL: int = 5

    @field_validator("SIMILARITY_THRESHOLD", mode="before")
    @classmethod
    def calibrate_threshold(cls, v: object) -> float:
        if v is None:
            return 0.48
        try:
            val = float(v)  # type: ignore[arg-type]
            if val == 0.65:
                # Recalibrate legacy default to empirical 0.48
                return 0.48
            return val
        except (ValueError, TypeError):
            return 0.48

    # External Provider Safeguards
    PROVIDER_TIMEOUT_SECONDS: int = 15
    PROVIDER_MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(
        env_file=[
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
            ".env",
        ],
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
