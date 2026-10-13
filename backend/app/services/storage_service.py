import os
import uuid
import shutil
from pathlib import Path
from app.core.config import settings
from app.core.errors import StorageLimitExceededError, ParsingError
from app.core.logging import logger


class StorageService:
    @staticmethod
    def get_upload_dir(workspace_id: uuid.UUID) -> Path:
        base_dir = Path(settings.STORAGE_LOCAL_DIR).resolve()
        workspace_dir = base_dir / str(workspace_id)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        return workspace_dir

    @staticmethod
    def get_file_path(workspace_id: uuid.UUID, doc_id: uuid.UUID) -> Path:
        return StorageService.get_upload_dir(workspace_id) / f"{doc_id}.pdf"

    @classmethod
    def save_file(cls, workspace_id: uuid.UUID, doc_id: uuid.UUID, file_bytes: bytes) -> str:
        # 1. Size validation
        if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise StorageLimitExceededError(
                f"File size ({len(file_bytes)} bytes) exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_BYTES} bytes."
            )

        # 2. Magic bytes validation (%PDF- header)
        if not file_bytes.startswith(b"%PDF-"):
            raise ParsingError("Invalid file format. File does not start with valid '%PDF-' header bytes.")

        # 3. Secure disk persistence
        file_path = cls.get_file_path(workspace_id, doc_id)
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        logger.info(f"Persisted PDF file to {file_path}")
        return str(file_path)

    @classmethod
    def delete_file(cls, workspace_id: uuid.UUID, doc_id: uuid.UUID) -> None:
        file_path = cls.get_file_path(workspace_id, doc_id)
        if file_path.exists():
            try:
                os.remove(file_path)
                logger.info(f"Deleted physical document file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete document file {file_path}: {str(e)}")

    @classmethod
    def delete_workspace_dir(cls, workspace_id: uuid.UUID) -> None:
        workspace_dir = cls.get_upload_dir(workspace_id)
        if workspace_dir.exists():
            try:
                shutil.rmtree(workspace_dir)
                logger.info(f"Deleted workspace upload directory: {workspace_dir}")
            except Exception as e:
                logger.warning(f"Failed to delete workspace dir {workspace_dir}: {str(e)}")
