import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.qa import QueryRequest, QueryResponse
from app.services.qa_service import QAService

router = APIRouter()


@router.post(
    "/{workspace_id}/qa/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
)
async def query_workspace(
    workspace_id: uuid.UUID,
    request: QueryRequest,
    db: Session = Depends(get_db),
) -> QueryResponse:
    """
    Executes grounded RAG question-answering strictly scoped to the workspace evidence.
    Returns verifiable citations with page provenance, or abstains if evidence is insufficient.
    """
    return await QAService.answer_query(db=db, workspace_id=workspace_id, request=request)
