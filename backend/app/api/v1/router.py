from fastapi import APIRouter
from app.api.v1.endpoints import health, workspaces, documents, qa, comparison, evidence, evaluation

api_router = APIRouter()

# Health router
api_router.include_router(health.router, tags=["Health"])

# Workspaces router
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])

# Documents router (under /workspaces)
api_router.include_router(documents.router, prefix="/workspaces", tags=["Documents"])

# Grounded Q&A router (under /workspaces)
api_router.include_router(qa.router, prefix="/workspaces", tags=["Q&A"])

# Multi-Document Comparison router (under /workspaces)
api_router.include_router(comparison.router, prefix="/workspaces", tags=["Comparison"])

# Evidence inspection router
api_router.include_router(evidence.router, prefix="/evidence", tags=["Evidence"])

# Benchmark Evaluation router
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["Evaluation"])



