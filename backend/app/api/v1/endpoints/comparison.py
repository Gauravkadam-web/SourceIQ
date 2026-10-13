import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.comparison import ComparisonRequest, ComparisonResponse
from app.services.comparison_service import ComparisonService

router = APIRouter()


@router.post(
    "/{workspace_id}/comparison/query",
    response_model=ComparisonResponse,
    status_code=status.HTTP_200_OK,
)
async def compare_documents(
    workspace_id: uuid.UUID,
    request: ComparisonRequest,
    db: Session = Depends(get_db),
) -> ComparisonResponse:
    """
    Compare a specific topic or question across at least two selected documents in the workspace.
    Produces per-document evidence findings with verified page citations and objective cross-document synthesis.
    """
    return await ComparisonService.compare_documents(db=db, workspace_id=workspace_id, request=request)
