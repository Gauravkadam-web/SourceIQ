import uuid
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.qa import CitationDetail


class ComparisonRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=1000, description="Topic or question to compare across documents.")
    document_ids: List[uuid.UUID] = Field(..., min_length=2, max_length=5, description="At least two document IDs to compare.")
    top_k_per_document: Optional[int] = Field(default=3, ge=1, le=5, description="Number of evidence chunks to retrieve per document.")
    similarity_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Optional similarity threshold override.")


class DocumentFinding(BaseModel):
    document_id: uuid.UUID
    document_name: str
    has_sufficient_evidence: bool
    summary: str
    citations: List[CitationDetail] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ComparisonResponse(BaseModel):
    comparison_id: uuid.UUID
    workspace_id: uuid.UUID
    topic: str
    status: str  # "COMPLETED", "INSUFFICIENT_EVIDENCE", "INCOMPARABLE_SCOPES"
    relationship: str  # "AGREEMENT", "DIFFERENCE", "CONTRADICTION", "DIFFERENT_SCOPES", "INSUFFICIENT_EVIDENCE"
    synthesis: str
    scope_notes: Optional[str] = None
    document_findings: List[DocumentFinding]
    latency_ms: float

    model_config = ConfigDict(from_attributes=True)
 