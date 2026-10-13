import uuid
import pytest
from sqlalchemy.orm import Session
from app.db.models.workspace import Workspace
from app.db.models.document import Document
from app.db.models.chunk import DocumentChunk
from app.services.retrieval_service import RetrievalService


def test_retrieval_service_filters_by_workspace_and_status(db_session: Session):
    # Setup two workspaces
    ws1 = Workspace(name="Workspace 1")
    ws2 = Workspace(name="Workspace 2")
    db_session.add_all([ws1, ws2])
    db_session.commit()

    # Documents
    doc1_ready = Document(
        workspace_id=ws1.id,
        filename="report1.pdf",
        file_path="/tmp/r1.pdf",
        file_size_bytes=1024,
        status="READY",
    )
    doc1_pending = Document(
        workspace_id=ws1.id,
        filename="report_pending.pdf",
        file_path="/tmp/rp.pdf",
        file_size_bytes=1024,
        status="PENDING",
    )
    doc2_ready = Document(
        workspace_id=ws2.id,
        filename="secret2.pdf",
        file_path="/tmp/s2.pdf",
        file_size_bytes=1024,
        status="READY",
    )
    db_session.add_all([doc1_ready, doc1_pending, doc2_ready])
    db_session.commit()

    # Chunks with distinct embeddings
    # Target query vector will be [1.0, 0.0, ...]
    v_exact = [1.0] + [0.0] * 767
    v_diff = [0.0] * 767 + [1.0]

    # Eligible chunk in ws1
    chunk_eligible = DocumentChunk(
        document_id=doc1_ready.id,
        workspace_id=ws1.id,
        page_number=1,
        chunk_index=0,
        content="Eligible content in Workspace 1.",
        token_count=10,
        embedding=v_exact,
    )
    # Chunk in ws1 but document is PENDING (not ready)
    chunk_pending_doc = DocumentChunk(
        document_id=doc1_pending.id,
        workspace_id=ws1.id,
        page_number=1,
        chunk_index=0,
        content="Content from pending document.",
        token_count=10,
        embedding=v_exact,
    )
    # Chunk in ws2 (isolated workspace)
    chunk_ws2 = DocumentChunk(
        document_id=doc2_ready.id,
        workspace_id=ws2.id,
        page_number=1,
        chunk_index=0,
        content="Secret content in Workspace 2.",
        token_count=10,
        embedding=v_exact,
    )
    db_session.add_all([chunk_eligible, chunk_pending_doc, chunk_ws2])
    db_session.commit()

    query_vector = [1.0] + [0.0] * 767

    # Retrieve for ws1
    results = RetrievalService.retrieve_relevant_chunks(
        db=db_session,
        workspace_id=ws1.id,
        query_vector=query_vector,
        similarity_threshold=0.5,
    )

    # Must only find the READY chunk belonging to ws1
    assert len(results) == 1
    assert results[0].chunk_id == chunk_eligible.id
    assert results[0].document_name == "report1.pdf"
    assert results[0].similarity_score >= 0.99


def test_retrieval_service_document_id_scoping(db_session: Session):
    ws = Workspace(name="Scope Workspace")
    db_session.add(ws)
    db_session.commit()

    doc_a = Document(workspace_id=ws.id, filename="doc_a.pdf", file_path="/tmp/a.pdf", file_size_bytes=1024, status="READY")
    doc_b = Document(workspace_id=ws.id, filename="doc_b.pdf", file_path="/tmp/b.pdf", file_size_bytes=1024, status="READY")
    db_session.add_all([doc_a, doc_b])
    db_session.commit()

    v = [1.0] + [0.0] * 767
    chunk_a = DocumentChunk(
        document_id=doc_a.id,
        workspace_id=ws.id,
        page_number=2,
        chunk_index=0,
        content="Document A passage",
        token_count=5,
        embedding=v,
    )
    chunk_b = DocumentChunk(
        document_id=doc_b.id,
        workspace_id=ws.id,
        page_number=5,
        chunk_index=0,
        content="Document B passage",
        token_count=5,
        embedding=v,
    )
    db_session.add_all([chunk_a, chunk_b])
    db_session.commit()

    # Query scoped strictly to doc_b
    results = RetrievalService.retrieve_relevant_chunks(
        db=db_session,
        workspace_id=ws.id,
        query_vector=v,
        document_ids=[doc_b.id],
        similarity_threshold=0.5,
    )

    assert len(results) == 1
    assert results[0].document_id == doc_b.id
    assert results[0].document_name == "doc_b.pdf"
    assert results[0].page_number == 5
