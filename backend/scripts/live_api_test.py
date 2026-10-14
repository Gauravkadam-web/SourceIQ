import asyncio
import io
import os
import sys
import time
import uuid
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import fitz  # PyMuPDF
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.db.models.workspace import Workspace
from app.db.models.document import Document
from app.services.document_service import DocumentService


def print_banner(text: str):
    print("\n" + "=" * 65)
    print(f"  {text}")
    print("=" * 65)


def create_sample_pdf() -> bytes:
    """Generates an in-memory 2-page digital PDF with verifiable facts."""
    doc = fitz.open()
    
    # Page 1
    p1 = doc.new_page()
    p1.insert_text(
        (50, 72),
        "SourceIQ Financial Report — Fiscal Year 2024\n\n"
        "Enterprise cloud revenue reached $48.5 million in 2024, representing 28% year-over-year growth.\n"
        "The expansion was primarily driven by enterprise subscription contracts and hybrid cloud migrations.\n"
        "Customer retention rate for cloud tiers held strong at 94.2%.",
        fontsize=11,
    )
    
    # Page 2
    p2 = doc.new_page()
    p2.insert_text(
        (50, 72),
        "Operational Performance & Profitability\n\n"
        "Operating margins expanded to 21.4% driven by logistics automation and data center optimizations.\n"
        "Research and development expenditures were $12.3 million, focused on evidence-backed document AI.\n"
        "Total full-time headcount reached 185 employees globally as of December 31, 2024.",
        fontsize=11,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def main():
    print_banner("SourceIQ — Live API End-to-End Verification")
    client = TestClient(app)

    # 1. Healthcheck Endpoint
    print("\n[Step 1] Testing GET /api/v1/health ...")
    res = client.get("/api/v1/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    print(f"  --> Status:   {health_data.get('status')}")
    print(f"  --> Database: {health_data.get('database')}")
    print(f"  --> pgvector: {health_data.get('pgvector')}")
    print(f"  --> Latency:  {health_data.get('latency_ms')} ms")

    # 2. Create Workspace
    print("\n[Step 2] Testing POST /api/v1/workspaces/ ...")
    ws_res = client.post(
        "/api/v1/workspaces/",
        json={"name": "Live Verification Workspace", "description": "Automated end-to-end API test"},
    )
    assert ws_res.status_code == 201, f"Failed to create workspace: {ws_res.text}"
    workspace = ws_res.json()
    ws_id = workspace["id"]
    print(f"  --> Workspace Created: ID={ws_id}, Name='{workspace['name']}'")

    # 3. List Workspaces
    print("\n[Step 3] Testing GET /api/v1/workspaces/ ...")
    list_res = client.get("/api/v1/workspaces/")
    assert list_res.status_code == 200
    print(f"  --> Total Workspaces: {len(list_res.json())}")

    # 4. Upload PDF Document
    print("\n[Step 4] Testing POST /api/v1/workspaces/{id}/documents/upload ...")
    pdf_bytes = create_sample_pdf()
    files = {"file": ("sourceiq_fy2024_report.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    upload_res = client.post(f"/api/v1/workspaces/{ws_id}/documents/upload", files=files)
    assert upload_res.status_code == 202, f"Upload failed: {upload_res.text}"
    doc_info = upload_res.json()
    doc_id = doc_info["id"]
    print(f"  --> Document Upload Accepted: ID={doc_id}")
    print(f"  --> Filename: {doc_info['filename']}")
    print(f"  --> Initial Status: {doc_info['status']}")

    # 5. Process Ingestion & Poll Status
    print("\n[Step 5] Ingesting Document (PyMuPDF Extraction -> Chunking -> Gemini Vector Embeddings) ...")
    
    # In TestClient, BackgroundTasks may have completed synchronously or require direct processing
    status_res = client.get(f"/api/v1/workspaces/{ws_id}/documents/{doc_id}")
    doc_status = status_res.json()
    if doc_status["status"] not in ("READY", "FAILED"):
        db = SessionLocal()
        try:
            asyncio.run(DocumentService.process_document_ingestion(uuid.UUID(doc_id), db=db))
        finally:
            db.close()
        status_res = client.get(f"/api/v1/workspaces/{ws_id}/documents/{doc_id}")
        doc_status = status_res.json()

    print(f"  --> Status:      {doc_status['status']}")
    print(f"  --> Page Count:  {doc_status['page_count']}")
    print(f"  --> Chunk Count: {doc_status['chunk_count']}")
    assert doc_status["status"] == "READY", f"Document ingestion failed: {doc_status.get('error_message')}"

    # 6. Grounded Q&A Query (Real Evidence-backed generation)
    print("\n[Step 6] Testing POST /api/v1/workspaces/{id}/qa/query (Grounded Question) ...")
    q1 = "What was the enterprise cloud revenue and growth rate reported in 2024?"
    print(f"  Question: '{q1}'")
    qa_res = client.post(
        f"/api/v1/workspaces/{ws_id}/qa/query",
        json={"question": q1, "top_k": 3},
    )
    assert qa_res.status_code == 200, f"QA query failed: {qa_res.text}"
    qa_data = qa_res.json()
    print(f"  --> Status:     {qa_data['status']}")
    print(f"  --> Latency:    {qa_data['latency_ms']} ms")
    print(f"  --> Answer:     {qa_data['answer']}")
    print(f"  --> Citations:  {len(qa_data['citations'])} verified citation(s)")
    for cit in qa_data["citations"]:
        print(f"      * [{cit['citation_key']}] Page {cit['page_number']} ({cit['document_name']}): \"{cit['quoted_snippet'][:80]}...\"")
    
    chunk_id_for_inspection = qa_data["citations"][0]["chunk_id"] if qa_data["citations"] else None

    # 7. Negative Control Query (Honest Abstention)
    print("\n[Step 7] Testing POST /api/v1/workspaces/{id}/qa/query (Negative Control / Abstention) ...")
    q2 = "What was the company's average rocket launch velocity on Mars in 2024?"
    print(f"  Question: '{q2}'")
    abstain_res = client.post(
        f"/api/v1/workspaces/{ws_id}/qa/query",
        json={"question": q2, "top_k": 3},
    )
    assert abstain_res.status_code == 200
    abstain_data = abstain_res.json()
    print(f"  --> Status:    {abstain_data['status']}")
    print(f"  --> Answer:    {abstain_data['answer']}")
    print(f"  --> Citations: {len(abstain_data['citations'])} (Expected 0 - Honest Abstention)")
    assert abstain_data["status"] == "INSUFFICIENT_EVIDENCE", "System should have abstained on ungrounded query!"

    # 8. Evidence Chunk Inspection
    if chunk_id_for_inspection:
        print("\n[Step 8] Testing GET /api/v1/evidence/{chunk_id} (Evidence Inspection) ...")
        ev_res = client.get(f"/api/v1/evidence/{chunk_id_for_inspection}")
        assert ev_res.status_code == 200
        ev_data = ev_res.json()
        print(f"  --> Chunk ID:      {ev_data['chunk_id']}")
        print(f"  --> Document:      {ev_data['document_name']} (Page {ev_data['page_number']})")
        print(f"  --> Chunk Content: \"{ev_data['content'][:100]}...\"")

    # 9. Cleanup Test Workspace
    print("\n[Step 9] Testing DELETE /api/v1/workspaces/{id} (Cascade Cleanup) ...")
    del_res = client.delete(f"/api/v1/workspaces/{ws_id}")
    assert del_res.status_code == 204
    print(f"  --> Workspace {ws_id} and all cascaded vectors deleted cleanly.")

    print_banner("ALL LIVE API CHECKS PASSED SUCCESSFULLY (100% GREEN)")


if __name__ == "__main__":
    main()
