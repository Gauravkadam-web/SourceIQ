import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Workspace display name")
    description: Optional[str] = Field(None, max_length=1000, description="Optional workspace description")


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceResponse(WorkspaceBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    document_count: Optional[int] = Field(0, description="Number of ingested documents")

    model_config = ConfigDict(from_attributes=True)
