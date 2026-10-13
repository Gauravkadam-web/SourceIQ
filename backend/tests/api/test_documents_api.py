import io
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models.workspace import Workspace
from app.db.models.document import Document
from app.core.config import settings


@pytest.fixture
def test_workspace(db_session: Session) -> Workspace:
    ws = Workspace(name="Test Doc Workspace", description="Workspace for document testing")
    db_session.add(ws)
    db_session.commit()
    db_session.refresh(ws)
    return ws


def test_upload_valid_pdf_success(client: TestClient, test_workspace: Workspace):
    fake_pdf_content = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>%%EOF"
    files = {"file": ("test_report.pdf", io.BytesIO(fake_pdf_content), "application/pdf")}

    response = client.post(f"/api/v1/workspaces/{test_workspace.id}/documents/upload", files=files)

    assert response.status_code == 202
    data = response.json()
    assert data["filename"] == "test_report.pdf"
    assert data["workspace_id"] == str(test_workspace.id)
    assert data["status"] == "PENDING"
    assert "id" in data


def test_upload_rejects_non_pdf_extension(client: TestClient, test_workspace: Workspace):
    files = {"file": ("malicious.exe", io.BytesIO(b"executable"), "application/octet-stream")}

    response = client.post(f"/api/v1/workspaces/{test_workspace.id}/documents/upload", files=files)

    assert response.status_code == 400
    assert "Only PDF files" in response.json()["detail"]


def test_upload_rejects_invalid_magic_bytes(client: TestClient, test_workspace: Workspace):
    files = {"file": ("fake.pdf", io.BytesIO(b"Plain text masquerading as pdf"), "application/pdf")}

    response = client.post(f"/api/v1/workspaces/{test_workspace.id}/documents/upload", files=files)

    assert response.status_code == 422
    assert "Invalid PDF format" in response.json()["detail"]


def test_upload_rejects_file_exceeding_size_limit(client: TestClient, test_workspace: Workspace, monkeypatch):
    # Set limit to 100 bytes for test
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_BYTES", 100)
    fake_large_pdf = b"%PDF-1.4\n" + b"A" * 200
    files = {"file": ("large.pdf", io.BytesIO(fake_large_pdf), "application/pdf")}

    response = client.post(f"/api/v1/workspaces/{test_workspace.id}/documents/upload", files=files)

    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()


def test_upload_to_nonexistent_workspace(client: TestClient):
    random_id = uuid.uuid4()
    fake_pdf = b"%PDF-1.4\nvalid pdf content"
    files = {"file": ("doc.pdf", io.BytesIO(fake_pdf), "application/pdf")}

    response = client.post(f"/api/v1/workspaces/{random_id}/documents/upload", files=files)

    assert response.status_code == 404


def test_list_and_get_document(client: TestClient, test_workspace: Workspace, db_session: Session):
    doc = Document(
        id=uuid.uuid4(),
        workspace_id=test_workspace.id,
        filename="existing.pdf",
        file_path="/tmp/fake.pdf",
        file_size_bytes=1024,
        status="READY",
        page_count=2,
        chunk_count=5,
    )
    db_session.add(doc)
    db_session.commit()

    # List documents
    list_res = client.get(f"/api/v1/workspaces/{test_workspace.id}/documents")
    assert list_res.status_code == 200
    docs = list_res.json()
    assert len(docs) == 1
    assert docs[0]["id"] == str(doc.id)

    # Get single document
    get_res = client.get(f"/api/v1/workspaces/{test_workspace.id}/documents/{doc.id}")
    assert get_res.status_code == 200
    assert get_res.json()["filename"] == "existing.pdf"
    assert get_res.json()["status"] == "READY"


def test_workspace_isolation_blocks_cross_workspace_document_access(
    client: TestClient, db_session: Session
):
    ws1 = Workspace(name="Workspace 1")
    ws2 = Workspace(name="Workspace 2")
    db_session.add_all([ws1, ws2])
    db_session.commit()

    doc = Document(
        id=uuid.uuid4(),
        workspace_id=ws1.id,
        filename="secret.pdf",
        file_path="/tmp/secret.pdf",
        file_size_bytes=500,
        status="READY",
    )
    db_session.add(doc)
    db_session.commit()

    # Attempting to access ws1's document via ws2 endpoint must return 404
    get_res = client.get(f"/api/v1/workspaces/{ws2.id}/documents/{doc.id}")
    assert get_res.status_code == 404

    delete_res = client.delete(f"/api/v1/workspaces/{ws2.id}/documents/{doc.id}")
    assert delete_res.status_code == 404


def test_delete_document_success(client: TestClient, test_workspace: Workspace, db_session: Session):
    doc = Document(
        id=uuid.uuid4(),
        workspace_id=test_workspace.id,
        filename="to_delete.pdf",
        file_path="/tmp/to_delete.pdf",
        file_size_bytes=256,
        status="READY",
    )
    db_session.add(doc)
    db_session.commit()

    del_res = client.delete(f"/api/v1/workspaces/{test_workspace.id}/documents/{doc.id}")
    assert del_res.status_code == 204

    # Verify deleted
    get_res = client.get(f"/api/v1/workspaces/{test_workspace.id}/documents/{doc.id}")
    assert get_res.status_code == 404
