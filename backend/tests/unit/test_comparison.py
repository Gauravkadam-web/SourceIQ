import uuid
from app.db.models.document import Document
from app.services.retrieval_service import RetrievedChunk
from app.services.comparison_service import ComparisonService
from app.services.qa_service import LLMCitation


def test_build_comparison_context_with_mixed_evidence():
    doc1_id = uuid.uuid4()
    doc2_id = uuid.uuid4()

    doc1 = Document(id=doc1_id, filename="company_a.pdf", file_path="/tmp/a.pdf", file_size_bytes=100, status="READY")
    doc2 = Document(id=doc2_id, filename="company_b.pdf", file_path="/tmp/b.pdf", file_size_bytes=100, status="READY")

    c1 = RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=doc1_id,
        document_name="company_a.pdf",
        page_number=2,
        chunk_index=0,
        content="Company A reported revenue of $50M.",
        similarity_score=0.91,
        distance=0.09,
    )

    doc_chunks_map = {
        doc1_id: [c1],
        doc2_id: [],  # Doc 2 has no evidence
    }

    xml, chunk_map = ComparisonService._build_comparison_context([doc1, doc2], doc_chunks_map)

    assert 'name="company_a.pdf"' in xml
    assert 'id="DOC1-CIT-1"' in xml
    assert "Company A reported revenue of $50M." in xml
    assert 'name="company_b.pdf"' in xml
    assert "<no_evidence>" in xml
    assert "DOC1-CIT-1" in chunk_map


def test_validate_doc_citations_enforces_document_ownership():
    doc1_id = uuid.uuid4()
    doc2_id = uuid.uuid4()
    c1_id = uuid.uuid4()

    c1 = RetrievedChunk(
        chunk_id=c1_id,
        document_id=doc1_id,
        document_name="company_a.pdf",
        page_number=1,
        chunk_index=0,
        content="Passage from doc 1",
        similarity_score=0.88,
        distance=0.12,
    )

    chunk_map = {"DOC1-CIT-1": c1}

    # Citation claiming to belong to doc 2, but chunk is actually from doc 1
    raw_citations = [
        LLMCitation(citation_key="DOC1-CIT-1", claim="Claim", quoted_snippet="Passage from doc 1")
    ]

    # Validating for doc 1 should succeed
    val_doc1, valid_doc1 = ComparisonService._validate_doc_citations(raw_citations, chunk_map, doc1_id)
    assert valid_doc1
    assert len(val_doc1) == 1

    # Validating for doc 2 should reject it (mismatched document owner)
    val_doc2, valid_doc2 = ComparisonService._validate_doc_citations(raw_citations, chunk_map, doc2_id)
    assert not valid_doc2
    assert len(val_doc2) == 0
