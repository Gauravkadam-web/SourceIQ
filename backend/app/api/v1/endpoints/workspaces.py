import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from app.services.workspace_service import WorkspaceService

router = APIRouter()


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    data: WorkspaceCreate,
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    """Create a new workspace."""
    return WorkspaceService.create_workspace(db, data)


@router.get("/", response_model=List[WorkspaceResponse], status_code=status.HTTP_200_OK)
def list_workspaces(
    db: Session = Depends(get_db),
) -> List[WorkspaceResponse]:
    """List all available workspaces."""
    return WorkspaceService.list_workspaces(db)


@router.get("/{workspace_id}", response_model=WorkspaceResponse, status_code=status.HTTP_200_OK)
def get_workspace(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    """Get details for a specific workspace."""
    return WorkspaceService.get_workspace(db, workspace_id)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    """Delete a workspace and cascade delete all its documents and vectors."""
    WorkspaceService.delete_workspace(db, workspace_id)
