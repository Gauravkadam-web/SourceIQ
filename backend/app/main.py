from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.core.logging import logger
from app.core.errors import (
    SourceIQError,
    sourceiq_exception_handler,
    global_exception_handler,
)
from app.api.v1.router import api_router
from app.db.session import engine
from app.db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager that automatically verifies and creates database tables on startup."""
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        logger.info("Database extensions and tables verified/created successfully on startup.")
    except Exception as exc:
        logger.warning(f"Database auto-init note: {exc}")
    yield


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="SourceIQ — AI Answers. Verifiable Sources.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Exception Handlers
    app.add_exception_handler(SourceIQError, sourceiq_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # Include API Routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/")
    def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": "0.1.0",
            "tagline": "AI Answers. Verifiable Sources.",
            "docs": "/docs",
        }

    return app


app = create_application()
