from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class SourceIQError(Exception):
    """Base exception for all domain errors in SourceIQ."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class EntityNotFoundError(SourceIQError):
    def __init__(self, message: str = "Requested resource was not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class BadRequestError(SourceIQError):
    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class StorageLimitExceededError(SourceIQError):
    def __init__(self, message: str = "Uploaded document exceeds maximum allowed size"):
        super().__init__(message, status_code=status.HTTP_413_CONTENT_TOO_LARGE)


class ParsingError(SourceIQError):
    def __init__(self, message: str = "Failed to parse document text or format unsupported"):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


class ProviderError(SourceIQError):
    def __init__(self, message: str = "AI Provider service encountered an error"):
        super().__init__(message, status_code=status.HTTP_502_BAD_GATEWAY)


async def sourceiq_exception_handler(request: Request, exc: SourceIQError) -> JSONResponse:
    logger.warning(f"Domain error on {request.method} {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_type": exc.__class__.__name__},
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred.", "error_type": "InternalServerError"},
    )
