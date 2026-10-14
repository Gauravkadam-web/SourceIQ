# SourceIQ — AI Answers. Verifiable Sources.

[![Backend Tests](https://img.shields.io/badge/pytest-42%2F42%20passing-10b981?style=flat-square&logo=python)](file:///d:/SourceIQ/backend)
[![Next.js Build](https://img.shields.io/badge/next.js-14.2%20passing-06b6d4?style=flat-square&logo=next.js)](file:///d:/SourceIQ/frontend)
[![PostgreSQL](https://img.shields.io/badge/postgresql-18%20%2B%20pgvector%20v0.8.6-336791?style=flat-square&logo=postgresql)](file:///d:/SourceIQ/backend)
[![Architecture](https://img.shields.io/badge/architecture-modular%20monolith-6366f1?style=flat-square)](file:///d:/SourceIQ)
[![License](https://img.shields.io/badge/license-MIT-slate?style=flat-square)](LICENSE)

> **SourceIQ** is an evidence-first document intelligence platform that answers questions about user-uploaded PDFs, retrieves relevant evidence with strict page-level provenance, validates citation references on the server, communicates uncertainty through honest abstention, and supports evidence-backed comparison across selected documents.

---

## 🏛️ System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        SourceIQ Web Application                        │
│                     Next.js 14 (App Router) + Vanilla CSS              │
│       [ / ] Q&A  |  [ /compare ] Matrix  |  [ /documents ] Ingest      │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTP / JSON REST APIs
┌──────────────────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend (Modular Monolith)                  │
├────────────────────────────────────────────────────────────────────────┤
│ • Workspaces Router      • Document Ingestion Router                   │
│ • Grounded Q&A Router    • Multi-Doc Comparison Router                 │
│ • Evidence Router        • Curated Evaluation Router                   │
├────────────────────────────────────────────────────────────────────────┤
│                          Application Services                          │
│ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────┐ │
│ │   DocumentService    │ │   RetrievalService   │ │    QAService     │ │
│ │ (PyMuPDF Extraction) │ │  (pgvector Cosine)   │ │(Citation Valida) │ │
│ └──────────────────────┘ └──────────────────────┘ └──────────────────┘ │
│ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────┐ │
│ │  ComparisonService   │ │  EvaluationService   │ │ Provider Gateway │ │
│ │ (Multi-Doc Analysis) │ │ (Benchmark Runner)   │ │ (Gemini, OpenAI) │ │
│ └──────────────────────┘ └──────────────────────┘ └──────────────────┘ │
├────────────────────────────────────────────────────────────────────────┤
│                             Data Layer                                 │
│          SQLAlchemy ORM + Alembic Versioned Migrations                 │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Native Connection (psycopg3)
┌──────────────────────────────────▼─────────────────────────────────────┐
│                  Native PostgreSQL 18 with pgvector                    │
│   • workspaces        • documents         • document_chunks (768d)     │
│   • query_runs        • citation_logs     • HNSW Cosine Index          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Core Product Capabilities

- 📄 **Page-Aware PDF Ingestion**: Extracts text using PyMuPDF while strictly preserving zero-indexed and 1-based source page provenance throughout chunking, vectorization, and retrieval.
- 🧩 **Sliding Window Chunking**: Token-aware sliding chunker (500 tokens target, 50 overlap) with clean sentence boundary awareness.
- 🎯 **Semantic Retrieval with pgvector**: Scoped strictly to the active workspace with cosine distance indexing (`<=>`), preventing cross-tenant leakage.
- 🛡️ **Server-Side Citation Validation**: Every LLM-generated citation badge (e.g. `[CIT-1]`, `[DOC1-CIT-1]`) is cross-checked against stored database chunks and verified verbatim before returning to the user.
- 🚫 **Honest Abstention (`INSUFFICIENT_EVIDENCE`)**: When evidence is missing or below the similarity threshold (0.65), SourceIQ communicates uncertainty honestly rather than hallucinating answers.
- ⚖️ **Multi-Document Comparison (FR-07)**: Compares specific topics across 2+ selected documents, generating structured per-document findings and classifying relationships into `AGREEMENT`, `DIFFERENCE`, `CONTRADICTION`, `DIFFERENT_SCOPES`, or `INSUFFICIENT_EVIDENCE`.
- 🔍 **Interactive Evidence Drawer**: Click on any citation badge in the UI to slide open the exact source document passage, page number, and surrounding context.
- 📊 **Curated Evaluation Benchmark (FR-08)**: Repeatable automated benchmark suite validating retrieval hit rate, citation validity, and negative control abstention rate.

---

## 🛠️ Technology Stack

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend** | Python 3.12, FastAPI, Uvicorn | High-performance asynchronous REST API with Pydantic validation |
| **Database** | PostgreSQL 18, `pgvector` v0.8.6 | Native vector search directly in transactional database (No external vector DB) |
| **ORM & Migrations**| SQLAlchemy 2.0, Alembic | Type-safe models with versioned schema migrations |
| **PDF Extraction** | PyMuPDF (fitz) | Fast, deterministic text and page provenance extraction |
| **AI Provider** | Google Gemini (`gemini-3.1-flash-lite`, `gemini-embedding-001`) | Pluggable provider architecture with automatic model fallback |
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript | Modern server/client architecture with fast page rendering |
| **Styling** | Vanilla CSS Design Tokens | Ultra-modern dark slate & cyan neon palette with glassmorphism |

---

## 🚀 Quick Start (Local Native Windows)

> **Important**: As specified in `AGENTS.md`, **local development strictly uses a native local PostgreSQL installation**. Docker is used for production deployment only.

### 1. Prerequisites
- **Python**: 3.12+ installed
- **Node.js**: 20+ installed
- **PostgreSQL**: 18+ with `pgvector` installed and running on `localhost:5432`

### 2. Configure Environment Files

SourceIQ strictly enforces 3 independent environment configuration scopes:
1. `/.env.example` $\to$ copy to `/.env` (Global repository settings)
2. `/backend/.env.example` $\to$ copy to `/backend/.env` (Backend credentials & Gemini API key)
3. `/frontend/.env.example` $\to$ copy to `/frontend/.env.local` (Next.js public API URL)

```bash
# In backend directory:
copy backend\.env.example backend\.env
# Open backend\.env and configure your GEMINI_API_KEY and DATABASE_URL
```

### 3. Setup & Run Backend

```powershell
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Backend API will be available at: **http://127.0.0.1:8000**  
Interactive Swagger Docs: **http://127.0.0.1:8000/docs**

### 4. Setup & Run Frontend

```powershell
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Frontend Web UI will be available at: **http://localhost:3000**

---

## ⚡ One-Click Local Launcher

For convenience on Windows, launch both services concurrently with a single command:

```powershell
# Using Batch file:
.\run_dev.bat

# OR using PowerShell:
.\run_dev.ps1
```

---

## 🧪 Testing & Verification

### Run Automated Backend Test Suite (42 Tests)
```powershell
cd backend
venv\Scripts\python -m pytest tests/ -v
```

### Run Live End-to-End API Test with Real Gemini API
```powershell
cd backend
venv\Scripts\python scripts/live_api_test.py
```
This script automatically validates all 9 live pipeline steps:
1. Healthcheck (`GET /api/v1/health`)
2. Workspace creation (`POST /api/v1/workspaces/`)
3. Workspace listing (`GET /api/v1/workspaces/`)
4. PDF upload (`POST /api/v1/workspaces/{id}/documents/upload`)
5. Ingestion pipeline (PyMuPDF $\to$ Chunking $\to$ Gemini 768-dim Vector Embeddings)
6. Grounded Q&A with verified citation tags (`POST /api/v1/workspaces/{id}/qa/query`)
7. Honest Abstention negative control (`status: INSUFFICIENT_EVIDENCE`)
8. Evidence chunk inspection (`GET /api/v1/evidence/{chunk_id}`)
9. Cascade deletion cleanup (`DELETE /api/v1/workspaces/{id}`)

### Run Frontend Production Build Validation
```powershell
cd frontend
npm run build
```

---

## 🐳 Production Deployment (Docker Compose)

Docker is configured **strictly for production environments**:

```bash
# Launch production stack (Backend + Frontend + PostgreSQL with pgvector)
docker compose -f docker-compose.prod.yml up --build -d
```

---

## 📚 API Reference Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Comprehensive database, pgvector, and latency health check |
| `GET` | `/api/v1/workspaces/` | List all workspaces |
| `POST` | `/api/v1/workspaces/` | Create a new isolated workspace |
| `GET` | `/api/v1/workspaces/{id}` | Get workspace details and document count |
| `DELETE` | `/api/v1/workspaces/{id}` | Cascade delete workspace and all associated documents/vectors |
| `POST` | `/api/v1/workspaces/{id}/documents/upload` | Upload PDF file for asynchronous ingestion |
| `GET` | `/api/v1/workspaces/{id}/documents` | List all documents in workspace with ingestion status |
| `GET` | `/api/v1/workspaces/{id}/documents/{doc_id}` | Poll document ingestion status and chunk count |
| `DELETE` | `/api/v1/workspaces/{id}/documents/{doc_id}` | Delete document and cascade delete vector embeddings |
| `POST` | `/api/v1/workspaces/{id}/qa/query` | Grounded question answering with citation validation & abstention |
| `POST` | `/api/v1/workspaces/{id}/comparison/query` | Evidence-backed multi-document comparison (FR-07) |
| `GET` | `/api/v1/evidence/{chunk_id}` | Inspect verbatim passage text, page number, and surrounding context |
| `POST` | `/api/v1/evaluation/run` | Execute curated benchmark test suite (FR-08) |

---

## 🔒 Security & Data Isolation Rules

- **Workspace Boundaries**: Every document, chunk, vector retrieval, and citation lookup is strictly scoped to the authorized workspace ID.
- **Zero Secrets Leakage**: `.env` files are gitignored and never committed or logged. Example blueprints are maintained via `.env.example`.
- **Parameterization**: All database operations use SQLAlchemy parameterized queries, preventing SQL injection.
- **Provenance Integrity**: Model outputs are parsed and checked against stored document chunks before rendering citations to prevent hallucinated references.

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
