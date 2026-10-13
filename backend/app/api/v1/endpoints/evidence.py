import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.qa import EvidenceInspectionResponse
from app.services.qa_service import QAService

router = APIRouter()


@router.get(
    "/{chunk_id}",
    response_model=EvidenceInspectionResponse,
    status_code=status.HTTP_200_OK,
)
def inspect_evidence_chunk(
    chunk_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> EvidenceInspectionResponse:
    """
    Retrieves full source chunk text and adjacent paragraph context for audit inspection.
    """
    return QAService.get_evidence(db=db, chunk_id=chunk_id)
