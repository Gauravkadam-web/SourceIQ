import uuid
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="User question to be answered from evidence.")
    document_ids: Optional[List[uuid.UUID]] = Field(default=None, description="Optional document filter scope.")
    top_k: Optional[int] = Field(default=5, ge=1, le=10, description="Maximum number of chunks to retrieve.")


class CitationDetail(BaseModel):
    citation_key: str
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    page_number: int
    similarity_score: float
    quoted_snippet: str
    claim: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class QueryResponse(BaseModel):
    query_id: uuid.UUID
    question: str
    answer: str
    status: str  # "GROUNDED", "INSUFFICIENT_EVIDENCE", "CITATION_FAILED"
    latency_ms: float
    citations: List[CitationDetail] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class EvidenceInspectionResponse(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    page_number: int
    chunk_index: int
    content: str
    surrounding_context: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
