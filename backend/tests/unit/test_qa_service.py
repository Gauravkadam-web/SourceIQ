import uuid
from app.services.retrieval_service import RetrievedChunk
from app.services.qa_service import QAService, LLMCitation


def test_build_evidence_context_formats_xml_tags():
    c1 = RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        document_name="annual_report.pdf",
        page_number=3,
        chunk_index=0,
        content="Revenue rose 25% year over year.",
        similarity_score=0.92,
        distance=0.08,
    )
    c2 = RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        document_name="annual_report.pdf",
        page_number=4,
        chunk_index=1,
        content="Operating costs decreased by 5%.",
        similarity_score=0.88,
        distance=0.12,
    )

    xml, chunk_map = QAService._build_evidence_context([c1, c2])

    assert 'id="CIT-1"' in xml
    assert 'document="annual_report.pdf"' in xml
    assert 'page="3"' in xml
    assert "Revenue rose 25%" in xml
    assert 'id="CIT-2"' in xml
    assert "CIT-1" in chunk_map
    assert "CIT-2" in chunk_map


def test_validate_citations_verifies_real_and_rejects_hallucinations():
    c1_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    c1 = RetrievedChunk(
        chunk_id=c1_id,
        document_id=doc_id,
        document_name="report.pdf",
        page_number=7,
        chunk_index=2,
        content="Enterprise customers grew by 140 new accounts.",
        similarity_score=0.89,
        distance=0.11,
    )
    chunk_map = {"CIT-1": c1}

    raw_citations = [
        LLMCitation(
            citation_key="CIT-1",
            claim="Enterprise accounts grew",
            quoted_snippet="Enterprise customers grew by 140 new accounts.",
        ),
        LLMCitation(
            citation_key="CIT-99",  # Hallucinated key
            claim="Bogus claim",
            quoted_snippet="Non-existent quote",
        ),
    ]

    validated, all_valid = QAService._validate_citations(raw_citations, chunk_map)

    assert not all_valid  # Because CIT-99 was rejected
    assert len(validated) == 1
    assert validated[0].citation_key == "CIT-1"
    assert validated[0].chunk_id == c1_id
    assert validated[0].page_number == 7
    assert validated[0].quoted_snippet == "Enterprise customers grew by 140 new accounts."
