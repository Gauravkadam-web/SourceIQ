from fastapi import APIRouter
from app.api.v1.endpoints import health, workspaces, documents

api_router = APIRouter()

# Health router
api_router.include_router(health.router, tags=["Health"])

# Workspaces router
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])

# Documents router (under /workspaces)
api_router.include_router(documents.router, prefix="/workspaces", tags=["Documents"])
