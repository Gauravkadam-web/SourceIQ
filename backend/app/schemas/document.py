import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    filename: str
    file_size_bytes: int
    mime_type: str = "application/pdf"


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    filename: str
    file_size_bytes: int
    status: str
    page_count: int
    chunk_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(DocumentUploadResponse):
    error_message: Optional[str] = None
    updated_at: datetime
