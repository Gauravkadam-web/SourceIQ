import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ChunkData(BaseModel):
    chunk_index: int
    page_number: int
    content: str
    token_count: int


class ChunkResponse(ChunkData):
    id: uuid.UUID
    document_id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidencePassage(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    page_number: int
    chunk_index: int
    content: str
    similarity_score: Optional[float] = None
    surrounding_context: Optional[str] = None
