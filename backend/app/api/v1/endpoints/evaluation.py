from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.evaluation import EvalReportResponse
from app.evaluation.evaluator import Evaluator

router = APIRouter()


@router.post(
    "/run",
    response_model=EvalReportResponse,
    status_code=status.HTTP_200_OK,
)
async def run_evaluation_benchmark(
    db: Session = Depends(get_db),
) -> EvalReportResponse:
    """
    Executes the curated benchmark suite verifying retrieval hit rate, citation validity,
    and negative control abstention behavior.
    """
    return await Evaluator.run_evaluation(db=db)
