import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.schemas.qa import QueryResponse, CitationDetail
from app.services.embedding_service import EmbeddingService
from app.services.qa_service import QAService


def test_evaluation_run_endpoint(client: TestClient, db_session: Session):
    async def mock_answer_query(db, workspace_id, request):
        if "mars" in request.question.lower() or "pet" in request.question.lower():
            return QueryResponse(
                query_id=workspace_id,
                question=request.question,
                answer="I could not find sufficient evidence.",
                status="INSUFFICIENT_EVIDENCE",
                latency_ms=10.0,
                citations=[],
            )
        else:
            return QueryResponse(
                query_id=workspace_id,
                question=request.question,
                answer="Factual verified answer [CIT-1].",
                status="GROUNDED",
                latency_ms=25.0,
                citations=[
                    CitationDetail(
                        citation_key="CIT-1",
                        chunk_id=workspace_id,
                        document_id=workspace_id,
                        document_name="test.pdf",
                        page_number=1,
                        similarity_score=0.95,
                        quoted_snippet="Factual quote",
                    )
                ],
            )

    with patch.object(EmbeddingService, "generate_chunk_embeddings", new_callable=AsyncMock) as mock_embed, \
         patch.object(QAService, "answer_query", side_effect=mock_answer_query):

        mock_embed.return_value = [[0.05] * 768]

        res = client.post("/api/v1/evaluation/run")

        assert res.status_code == 200
        data = res.json()
        assert data["total_questions"] == 5
        assert data["passed_count"] == 5
        assert data["retrieval_hit_rate_pct"] == 100.0
        assert data["citation_validity_pct"] == 100.0
        assert data["negative_control_abstention_pct"] == 100.0
        assert data["is_model_judged"] is False
        assert len(data["results"]) == 5
