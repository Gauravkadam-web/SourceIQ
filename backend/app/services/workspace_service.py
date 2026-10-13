import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.models.workspace import Workspace
from app.db.models.document import Document
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from app.core.errors import EntityNotFoundError


class WorkspaceService:
    @staticmethod
    def create_workspace(db: Session, data: WorkspaceCreate) -> WorkspaceResponse:
        workspace = Workspace(
            name=data.name,
            description=data.description,
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        return WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
            document_count=0,
        )

    @staticmethod
    def list_workspaces(db: Session) -> List[WorkspaceResponse]:
        # Fetch workspaces with document counts
        query = (
            select(
                Workspace,
                func.count(Document.id).label("doc_count")
            )
            .outerjoin(Document, Workspace.id == Document.workspace_id)
            .group_by(Workspace.id)
            .order_by(Workspace.created_at.desc())
        )
        results = db.execute(query).all()

        responses = []
        for ws, doc_count in results:
            responses.append(
                WorkspaceResponse(
                    id=ws.id,
                    name=ws.name,
                    description=ws.description,
                    created_at=ws.created_at,
                    updated_at=ws.updated_at,
                    document_count=doc_count,
                )
            )
        return responses

    @staticmethod
    def get_workspace(db: Session, workspace_id: uuid.UUID) -> WorkspaceResponse:
        workspace = db.get(Workspace, workspace_id)
        if not workspace:
            raise EntityNotFoundError(f"Workspace with ID '{workspace_id}' was not found.")

        doc_count = (
            db.query(func.count(Document.id))
            .filter(Document.workspace_id == workspace_id)
            .scalar()
            or 0
        )
        return WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
            document_count=doc_count,
        )

    @staticmethod
    def delete_workspace(db: Session, workspace_id: uuid.UUID) -> None:
        workspace = db.get(Workspace, workspace_id)
        if not workspace:
            raise EntityNotFoundError(f"Workspace with ID '{workspace_id}' was not found.")
        db.delete(workspace)
        db.commit()
