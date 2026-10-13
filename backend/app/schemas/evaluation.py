from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EvalItemResult(BaseModel):
    id: str
    question: str
    category: str  # "grounded_fact", "negative_control", "comparison"
    expected_behavior: str
    actual_behavior: str
    passed: bool
    details: Optional[str] = None


class EvalRunRequest(BaseModel):
    workspace_id: Optional[str] = None
    run_llm_judge: bool = Field(default=False, description="Whether to include model-judged metrics")


class EvalReportResponse(BaseModel):
    total_questions: int
    passed_count: int
    retrieval_hit_rate_pct: float
    citation_validity_pct: float
    negative_control_abstention_pct: float
    average_latency_ms: float
    is_model_judged: bool = Field(default=False, description="Model-based metrics are labeled as estimates, not ground truth.")
    results: List[EvalItemResult]
