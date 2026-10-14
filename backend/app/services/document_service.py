import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.core.config import settings
from app.core.logging import logger
from app.core.errors import EntityNotFoundError, ParsingError, StorageLimitExceededError
from app.db.models.document import Document
from app.db.models.chunk import DocumentChunk
from app.db.models.workspace import Workspace
from app.services.storage_service import StorageService
from app.services.parser_service import ParserService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.schemas.document import DocumentUploadResponse, DocumentResponse


class DocumentService:
    @classmethod
    def create_document_record(
        cls,
        db: Session,
        workspace_id: uuid.UUID,
        filename: str,
        file_bytes: bytes,
    ) -> Document:
        # Check workspace exists
        workspace = db.get(Workspace, workspace_id)
        if not workspace:
            raise EntityNotFoundError(f"Workspace with ID '{workspace_id}' was not found.")

        # Check workspace document limit
        current_docs_count = (
            db.execute(select(func.count(Document.id)).filter(Document.workspace_id == workspace_id)).scalar() or 0
        )
        if current_docs_count >= settings.MAX_DOCUMENTS_PER_WORKSPACE:
            raise StorageLimitExceededError(
                f"Workspace document limit of {settings.MAX_DOCUMENTS_PER_WORKSPACE} reached."
            )

        doc_id = uuid.uuid4()

        # Save file to disk
        file_path = StorageService.save_file(workspace_id, doc_id, file_bytes)

        # Create Document record in PENDING state
        doc = Document(
            id=doc_id,
            workspace_id=workspace_id,
            filename=filename,
            file_path=file_path,
            file_size_bytes=len(file_bytes),
            status="PENDING",
            page_count=0,
            chunk_count=0,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @classmethod
    async def process_document_ingestion(cls, doc_id: uuid.UUID, db: Optional[Session] = None) -> None:
        """Background worker task for parsing, chunking, and embedding."""
        from app.db.session import SessionLocal

        db_created = False
        if db is None:
            db = SessionLocal()
            db_created = True

        try:
            doc = db.get(Document, doc_id)
            if not doc:
                logger.error(f"Cannot process document: {doc_id} not found in database.")
                return

            doc_id_val = doc.id
            workspace_id_val = doc.workspace_id
            filename_val = doc.filename
            file_path_val = doc.file_path

            try:
                # 1. State: PARSING
                doc.status = "PARSING"
                db.commit()

                local_path = StorageService.ensure_local_copy(workspace_id_val, doc_id_val, file_path_val)
                pages = ParserService.extract_pages(local_path)
                doc.page_count = len(pages)
                db.commit()

                # 2. Chunking
                chunks_data = ChunkingService.chunk_pages(pages)
                if not chunks_data:
                    raise ParsingError("No text chunks could be generated from document.")

                # 3. State: EMBEDDING
                doc.status = "EMBEDDING"
                db.commit()

                chunk_texts = [c.content for c in chunks_data]
                embeddings = await EmbeddingService.generate_chunk_embeddings(chunk_texts)

                # 4. Clean any existing chunks for idempotency / safe retry
                db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id_val).delete()

                # 5. Bulk insert DocumentChunks
                db_chunks = []
                for chunk_data, embedding in zip(chunks_data, embeddings):
                    db_chunks.append(
                        DocumentChunk(
                            document_id=doc_id_val,
                            workspace_id=workspace_id_val,
                            page_number=chunk_data.page_number,
                            chunk_index=chunk_data.chunk_index,
                            content=chunk_data.content,
                            token_count=chunk_data.token_count,
                            embedding=embedding,
                        )
                    )

                db.add_all(db_chunks)
                doc.status = "READY"
                doc.chunk_count = len(db_chunks)
                doc.error_message = None
                db.commit()
                logger.info(f"Document {doc_id_val} ({filename_val}) successfully ingested with {len(db_chunks)} chunks.")

            except Exception as e:
                logger.error(f"Ingestion failed for document {doc_id_val}: {str(e)}", exc_info=True)
                db.rollback()
                failed_doc = db.get(Document, doc_id_val)
                if failed_doc:
                    failed_doc.status = "FAILED"
                    failed_doc.error_message = str(e)
                    db.commit()
        finally:
            if db_created and db:
                db.close()

    @classmethod
    def list_documents(cls, db: Session, workspace_id: uuid.UUID) -> List[DocumentResponse]:
        workspace = db.get(Workspace, workspace_id)
        if not workspace:
            raise EntityNotFoundError(f"Workspace with ID '{workspace_id}' was not found.")

        query = select(Document).filter(Document.workspace_id == workspace_id).order_by(Document.created_at.desc())
        docs = db.execute(query).scalars().all()
        return [DocumentResponse.model_validate(d) for d in docs]

    @classmethod
    def get_document(cls, db: Session, workspace_id: uuid.UUID, doc_id: uuid.UUID) -> DocumentResponse:
        doc = db.get(Document, doc_id)
        if not doc or doc.workspace_id != workspace_id:
            raise EntityNotFoundError(f"Document with ID '{doc_id}' was not found in this workspace.")
        return DocumentResponse.model_validate(doc)

    @classmethod
    def delete_document(cls, db: Session, workspace_id: uuid.UUID, doc_id: uuid.UUID) -> None:
        doc = db.get(Document, doc_id)
        if not doc or doc.workspace_id != workspace_id:
            raise EntityNotFoundError(f"Document with ID '{doc_id}' was not found in this workspace.")

        # Delete physical file
        StorageService.delete_file(workspace_id, doc_id)

        # Database cascade deletes document_chunks and embeddings
        db.delete(doc)
        db.commit()
        logger.info(f"Document {doc_id} and associated vector chunks deleted.")
