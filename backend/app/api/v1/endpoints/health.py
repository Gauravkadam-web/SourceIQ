import time
from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Health check endpoint validating database connectivity and vector readiness."""
    start_time = time.perf_counter()
    db_status = "healthy"
    vector_status = "unknown"
    latency_ms = 0.0

    try:
        # Check database connectivity
        result = db.execute(text("SELECT 1;")).scalar()
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Check pgvector extension availability
        ext_check = db.execute(
            text("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
        ).scalar()
        if ext_check:
            vector_status = f"enabled (v{ext_check})"
        else:
            vector_status = "not_installed"

    except Exception as e:
        logger.error(f"Healthcheck database check failed: {str(e)}")
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "database": {
            "status": db_status,
            "latency_ms": latency_ms,
            "pgvector": vector_status,
        },
        "providers": {
            "llm": settings.LLM_PROVIDER,
            "llm_model": settings.GEMINI_LLM_MODEL if settings.LLM_PROVIDER == "gemini" else settings.OPENAI_LLM_MODEL,
            "embedding": settings.EMBEDDING_PROVIDER,
            "embedding_model": settings.GEMINI_EMBEDDING_MODEL if settings.EMBEDDING_PROVIDER == "gemini" else settings.OPENAI_EMBEDDING_MODEL,
            "dimensions": settings.EMBEDDING_DIMENSIONS,
        },
    }
