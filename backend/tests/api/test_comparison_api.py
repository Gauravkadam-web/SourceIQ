import uuid
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models.workspace import Workspace
from app.db.models.document import Document
from app.db.models.chunk import DocumentChunk
from app.services.embedding_service import EmbeddingService


@pytest.fixture
def comp_workspace(db_session: Session) -> Workspace:
    ws = Workspace(name="Comparison Test Workspace", description="Workspace for comparison tests")
    db_session.add(ws)
    db_session.commit()
    db_session.refresh(ws)
    return ws


def test_comparison_success_between_two_documents(
    client: TestClient, comp_workspace: Workspace, db_session: Session
):
    # Two documents
    doc1 = Document(
        workspace_id=comp_workspace.id,
        filename="report_2023.pdf",
        file_path="/tmp/2023.pdf",
        file_size_bytes=1000,
        status="READY",
    )
    doc2 = Document(
        workspace_id=comp_workspace.id,
        filename="report_2024.pdf",
        file_path="/tmp/2024.pdf",
        file_size_bytes=1000,
        status="READY",
    )
    db_session.add_all([doc1, doc2])
    db_session.commit()

    v = [1.0] + [0.0] * 767
    c1 = DocumentChunk(
        document_id=doc1.id,
        workspace_id=comp_workspace.id,
        page_number=2,
        chunk_index=0,
        content="In 2023, cloud adoption was at 45%.",
        token_count=10,
        embedding=v,
    )
    c2 = DocumentChunk(
        document_id=doc2.id,
        workspace_id=comp_workspace.id,
        page_number=3,
        chunk_index=0,
        content="In 2024, cloud adoption increased to 68%.",
        token_count=10,
        embedding=v,
    )
    db_session.add_all([c1, c2])
    db_session.commit()

    mock_llm_response = {
        "synthesis": "Cloud adoption increased from 45% in 2023 to 68% in 2024.",
        "relationship": "DIFFERENCE",
        "scope_notes": "Sequential timeframes (2023 vs 2024).",
        "findings": [
            {
                "document_id": str(doc1.id),
                "has_sufficient_evidence": True,
                "summary": "Reported 45% cloud adoption [DOC1-CIT-1].",
                "citations": [
                    {
                        "citation_key": "DOC1-CIT-1",
                        "claim": "Reported 45% cloud adoption",
                        "quoted_snippet": "In 2023, cloud adoption was at 45%.",
                    }
                ],
            },
            {
                "document_id": str(doc2.id),
                "has_sufficient_evidence": True,
                "summary": "Reported 68% cloud adoption [DOC2-CIT-1].",
                "citations": [
                    {
                        "citation_key": "DOC2-CIT-1",
                        "claim": "Reported 68% cloud adoption",
                        "quoted_snippet": "In 2024, cloud adoption increased to 68%.",
                    }
                ],
            },
        ],
    }

    with patch.object(EmbeddingService, "generate_query_embedding", new_callable=AsyncMock) as mock_embed, \
         patch("app.services.comparison_service.get_llm_provider") as mock_get_provider:

        mock_embed.return_value = v
        mock_provider_instance = AsyncMock()
        mock_provider_instance.generate_grounded_answer.return_value = mock_llm_response
        mock_get_provider.return_value = mock_provider_instance

        res = client.post(
            f"/api/v1/workspaces/{comp_workspace.id}/comparison/query",
            json={
                "topic": "Cloud adoption rates",
                "document_ids": [str(doc1.id), str(doc2.id)],
                "top_k_per_document": 2,
            },
        )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "COMPLETED"
        assert data["relationship"] == "DIFFERENCE"
        assert "45% in 2023" in data["synthesis"]
        assert len(data["document_findings"]) == 2
        assert data["document_findings"][0]["has_sufficient_evidence"] is True
        assert len(data["document_findings"][0]["citations"]) == 1
        assert data["document_findings"][1]["has_sufficient_evidence"] is True


def test_comparison_abstention_when_zero_evidence_across_documents(
    client: TestClient, comp_workspace: Workspace, db_session: Session
):
    doc1 = Document(
        workspace_id=comp_workspace.id,
        filename="empty1.pdf",
        file_path="/tmp/e1.pdf",
        file_size_bytes=500,
        status="READY",
    )
    doc2 = Document(
        workspace_id=comp_workspace.id,
        filename="empty2.pdf",
        file_path="/tmp/e2.pdf",
        file_size_bytes=500,
        status="READY",
    )
    db_session.add_all([doc1, doc2])
    db_session.commit()

    with patch.object(EmbeddingService, "generate_query_embedding", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = [0.0] * 768

        res = client.post(
            f"/api/v1/workspaces/{comp_workspace.id}/comparison/query",
            json={
                "topic": "Quantum gravity",
                "document_ids": [str(doc1.id), str(doc2.id)],
            },
        )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "INSUFFICIENT_EVIDENCE"
        assert data["relationship"] == "INSUFFICIENT_EVIDENCE"
        for finding in data["document_findings"]:
            assert finding["has_sufficient_evidence"] is False


def test_comparison_rejects_fewer_than_two_documents(client: TestClient, comp_workspace: Workspace):
    single_id = uuid.uuid4()
    res = client.post(
        f"/api/v1/workspaces/{comp_workspace.id}/comparison/query",
        json={
            "topic": "Any topic",
            "document_ids": [str(single_id)],
        },
    )
    assert res.status_code == 422  # Pydantic min_length=2 validation


def test_comparison_rejects_nonexistent_workspace(client: TestClient):
    res = client.post(
        f"/api/v1/workspaces/{uuid.uuid4()}/comparison/query",
        json={
            "topic": "Any topic",
            "document_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
        },
    )
    assert res.status_code == 404
