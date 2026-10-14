import os
import uuid
import shutil
from pathlib import Path
import httpx
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

        # 3. Always save local copy for fast parsing & processing
        file_path = cls.get_file_path(workspace_id, doc_id)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"Persisted PDF file to local storage: {file_path}")

        # 4. Optional Supabase Storage Bucket Upload (for cloud persistence)
        if settings.STORAGE_BACKEND == "supabase" and settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                object_path = f"{workspace_id}/{doc_id}.pdf"
                upload_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}/{object_path}"
                headers = {
                    "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                    "Content-Type": "application/pdf",
                    "x-upsert": "true",
                }
                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(upload_url, headers=headers, content=file_bytes)
                    if resp.status_code in (200, 201):
                        logger.info(f"Successfully uploaded PDF to Supabase Storage: {object_path}")
                    else:
                        logger.warning(f"Supabase Storage upload returned {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"Failed to upload PDF to Supabase Storage: {str(e)}")

        return str(file_path)

    @classmethod
    def ensure_local_copy(cls, workspace_id: uuid.UUID, doc_id: uuid.UUID, file_path_str: str) -> str:
        """Ensures the PDF file exists locally on disk, downloading from Supabase Storage if missing."""
        file_path = Path(file_path_str)
        if file_path.exists():
            return str(file_path)

        # If missing on disk (e.g. ephemeral Render restart), pull from Supabase Storage
        if settings.STORAGE_BACKEND == "supabase" and settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                object_path = f"{workspace_id}/{doc_id}.pdf"
                download_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/authenticated/{settings.SUPABASE_STORAGE_BUCKET}/{object_path}"
                headers = {"Authorization": f"Bearer {settings.SUPABASE_KEY}"}
                with httpx.Client(timeout=20.0) as client:
                    resp = client.get(download_url, headers=headers)
                    if resp.status_code == 200:
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(file_path, "wb") as f:
                            f.write(resp.content)
                        logger.info(f"Restored local copy from Supabase Storage: {object_path}")
                        return str(file_path)
                    else:
                        logger.warning(f"Failed to download from Supabase Storage ({resp.status_code})")
            except Exception as e:
                logger.error(f"Error restoring file from Supabase Storage: {str(e)}")

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

        # Delete from Supabase Storage if enabled
        if settings.STORAGE_BACKEND == "supabase" and settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                object_path = f"{workspace_id}/{doc_id}.pdf"
                delete_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}"
                headers = {"Authorization": f"Bearer {settings.SUPABASE_KEY}", "Content-Type": "application/json"}
                with httpx.Client(timeout=10.0) as client:
                    client.request("DELETE", delete_url, headers=headers, json={"prefixes": [object_path]})
                logger.info(f"Deleted object from Supabase Storage: {object_path}")
            except Exception as e:
                logger.warning(f"Failed to delete from Supabase Storage: {str(e)}")

    @classmethod
    def delete_workspace_dir(cls, workspace_id: uuid.UUID) -> None:
        workspace_dir = cls.get_upload_dir(workspace_id)
        if workspace_dir.exists():
            try:
                shutil.rmtree(workspace_dir)
                logger.info(f"Deleted workspace upload directory: {workspace_dir}")
            except Exception as e:
                logger.warning(f"Failed to delete workspace dir {workspace_dir}: {str(e)}")
