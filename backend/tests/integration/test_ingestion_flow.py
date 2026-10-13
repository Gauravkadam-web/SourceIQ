import fitz
import uuid
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.workspace import Workspace
from app.db.models.document import Document
from app.db.models.chunk import DocumentChunk
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService


@pytest.mark.asyncio
async def test_full_document_ingestion_pipeline(db_session: Session, tmp_path):
    # 1. Setup workspace
    ws = Workspace(name="Ingestion Workspace", description="Integration test workspace")
    db_session.add(ws)
    db_session.commit()
    db_session.refresh(ws)

    # 2. Create synthetic 2-page digital PDF
    doc_fitz = fitz.open()
    p1 = doc_fitz.new_page()
    p1.insert_text((50, 72), "SourceIQ provides verifiable evidence-based answers with page citations.", fontsize=11)
    p2 = doc_fitz.new_page()
    p2.insert_text((50, 72), "Cross-document comparison highlights points of agreement and divergence.", fontsize=11)
    
    pdf_bytes = doc_fitz.tobytes()
    doc_fitz.close()

    # 3. Create document record via DocumentService
    doc = DocumentService.create_document_record(
        db=db_session,
        workspace_id=ws.id,
        filename="integration_test.pdf",
        file_bytes=pdf_bytes,
    )
    assert doc.status == "PENDING"
    assert doc.page_count == 0

    # 4. Mock the EmbeddingService to return 768-dimensional vectors
    dummy_vector = [0.01] * 768

    async def mock_embed_chunks(texts):
        return [dummy_vector for _ in texts]

    with patch.object(EmbeddingService, "generate_chunk_embeddings", side_effect=mock_embed_chunks):
        # 5. Execute ingestion worker
        await DocumentService.process_document_ingestion(doc_id=doc.id, db=db_session)

    # 6. Verify Document record in database
    db_session.refresh(doc)
    assert doc.status == "READY"
    assert doc.page_count == 2
    assert doc.chunk_count == 2
    assert doc.error_message is None

    # 7. Verify DocumentChunks in database
    chunks = db_session.execute(
        select(DocumentChunk).filter(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index.asc())
    ).scalars().all()

    assert len(chunks) == 2
    assert chunks[0].page_number == 1
    assert "verifiable evidence-based answers" in chunks[0].content
    assert chunks[1].page_number == 2
    assert "points of agreement and divergence" in chunks[1].content
    assert chunks[0].embedding is not None

    # 8. Clean up document and verify cascade delete
    DocumentService.delete_document(db=db_session, workspace_id=ws.id, doc_id=doc.id)
    deleted_doc = db_session.get(Document, doc.id)
    assert deleted_doc is None

    # Verify chunks cascaded
    remaining_chunks = db_session.execute(
        select(DocumentChunk).filter(DocumentChunk.document_id == doc.id)
    ).scalars().all()
    assert len(remaining_chunks) == 0
