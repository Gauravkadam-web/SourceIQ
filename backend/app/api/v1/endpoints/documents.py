import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.config import settings
from app.core.errors import BadRequestError, StorageLimitExceededError, ParsingError
from app.schemas.document import DocumentUploadResponse, DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.post(
    "/{workspace_id}/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    workspace_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    """
    Upload a digital PDF to a workspace.
    Validates MIME type, extension, magic bytes, and size, then dispatches background ingestion.
    """
    filename = file.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise BadRequestError("Only PDF files (.pdf) are supported.")

    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise StorageLimitExceededError(
            f"File size ({len(file_bytes)} bytes) exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE_BYTES} bytes."
        )

    if not file_bytes.startswith(b"%PDF-"):
        raise ParsingError("Invalid PDF format. File header does not start with '%PDF-'.")

    # Persist record in PENDING state
    doc = DocumentService.create_document_record(
        db=db,
        workspace_id=workspace_id,
        filename=filename,
        file_bytes=file_bytes,
    )

    # Dispatch parsing and embedding asynchronously
    background_tasks.add_task(DocumentService.process_document_ingestion, doc.id)

    return DocumentUploadResponse.model_validate(doc)


@router.get(
    "/{workspace_id}/documents",
    response_model=List[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
def list_documents(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> List[DocumentResponse]:
    """List all documents belonging to a workspace."""
    return DocumentService.list_documents(db, workspace_id)


@router.get(
    "/{workspace_id}/documents/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
def get_document(
    workspace_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """Get the current processing status and metadata for a specific document."""
    return DocumentService.get_document(db, workspace_id, document_id)


@router.delete(
    "/{workspace_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    workspace_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    """Delete a document, its physical storage file, and all associated vector embeddings."""
    DocumentService.delete_document(db, workspace_id, document_id)
