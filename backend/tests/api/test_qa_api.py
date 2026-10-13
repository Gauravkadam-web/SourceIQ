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
def qa_workspace(db_session: Session) -> Workspace:
    ws = Workspace(name="QA Test Workspace", description="Workspace for QA tests")
    db_session.add(ws)
    db_session.commit()
    db_session.refresh(ws)
    return ws


def test_qa_query_grounded_success(client: TestClient, qa_workspace: Workspace, db_session: Session):
    # Setup ready document and chunk
    doc = Document(
        workspace_id=qa_workspace.id,
        filename="financials.pdf",
        file_path="/tmp/fin.pdf",
        file_size_bytes=1024,
        status="READY",
    )
    db_session.add(doc)
    db_session.commit()

    chunk_vector = [1.0] + [0.0] * 767
    chunk = DocumentChunk(
        document_id=doc.id,
        workspace_id=qa_workspace.id,
        page_number=4,
        chunk_index=0,
        content="Revenue rose 25% year over year driven by cloud migrations.",
        token_count=10,
        embedding=chunk_vector,
    )
    db_session.add(chunk)
    db_session.commit()

    mock_llm_response = {
        "answer": "Revenue rose by 25% due to cloud migrations [CIT-1].",
        "status": "GROUNDED",
        "citations": [
            {
                "citation_key": "CIT-1",
                "claim": "Revenue rose by 25%",
                "quoted_snippet": "Revenue rose 25% year over year",
            }
        ],
    }

    with patch.object(EmbeddingService, "generate_query_embedding", new_callable=AsyncMock) as mock_embed, \
         patch("app.services.qa_service.get_llm_provider") as mock_get_provider:
        
        mock_embed.return_value = chunk_vector
        mock_provider_instance = AsyncMock()
        mock_provider_instance.generate_grounded_answer.return_value = mock_llm_response
        mock_get_provider.return_value = mock_provider_instance

        res = client.post(
            f"/api/v1/workspaces/{qa_workspace.id}/qa/query",
            json={"question": "How much did revenue grow?", "top_k": 3},
        )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "GROUNDED"
        assert "[CIT-1]" in data["answer"]
        assert len(data["citations"]) == 1
        assert data["citations"][0]["citation_key"] == "CIT-1"
        assert data["citations"][0]["page_number"] == 4
        assert data["citations"][0]["document_name"] == "financials.pdf"
        assert data["citations"][0]["chunk_id"] == str(chunk.id)


def test_qa_query_abstention_when_evidence_insufficient(client: TestClient, qa_workspace: Workspace):
    with patch.object(EmbeddingService, "generate_query_embedding", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = [0.0] * 768

        res = client.post(
            f"/api/v1/workspaces/{qa_workspace.id}/qa/query",
            json={"question": "What is the secret formula for cold fusion?", "top_k": 3},
        )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "INSUFFICIENT_EVIDENCE"
        assert "not find sufficient evidence" in data["answer"].lower()
        assert len(data["citations"]) == 0


def test_qa_query_rejects_nonexistent_workspace(client: TestClient):
    random_id = uuid.uuid4()
    res = client.post(
        f"/api/v1/workspaces/{random_id}/qa/query",
        json={"question": "Any question?"},
    )
    assert res.status_code == 404


def test_qa_query_rejects_invalid_document_scope(client: TestClient, qa_workspace: Workspace):
    random_doc_id = uuid.uuid4()
    res = client.post(
        f"/api/v1/workspaces/{qa_workspace.id}/qa/query",
        json={"question": "Any question?", "document_ids": [str(random_doc_id)]},
    )
    assert res.status_code == 404


def test_evidence_inspection_endpoint(client: TestClient, qa_workspace: Workspace, db_session: Session):
    doc = Document(
        workspace_id=qa_workspace.id,
        filename="handbook.pdf",
        file_path="/tmp/h.pdf",
        file_size_bytes=1024,
        status="READY",
    )
    db_session.add(doc)
    db_session.commit()

    v = [0.01] * 768
    c0 = DocumentChunk(document_id=doc.id, workspace_id=qa_workspace.id, page_number=1, chunk_index=0, content="Chapter 1 start.", token_count=5, embedding=v)
    c1 = DocumentChunk(document_id=doc.id, workspace_id=qa_workspace.id, page_number=1, chunk_index=1, content="Target middle passage with key evidence.", token_count=6, embedding=v)
    c2 = DocumentChunk(document_id=doc.id, workspace_id=qa_workspace.id, page_number=2, chunk_index=2, content="Chapter 2 continuation.", token_count=5, embedding=v)
    db_session.add_all([c0, c1, c2])
    db_session.commit()

    # Inspect c1
    res = client.get(f"/api/v1/evidence/{c1.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["chunk_id"] == str(c1.id)
    assert data["document_name"] == "handbook.pdf"
    assert data["page_number"] == 1
    assert "Target middle passage" in data["content"]
    assert "Chapter 1 start." in data["surrounding_context"]
    assert "Chapter 2 continuation." in data["surrounding_context"]

    # Non-existent chunk
    bad_res = client.get(f"/api/v1/evidence/{uuid.uuid4()}")
    assert bad_res.status_code == 404
