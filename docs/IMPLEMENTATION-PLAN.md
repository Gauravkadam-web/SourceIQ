# SourceIQ — Implementation Plan

**Document ID:** SIQ-IMP-001  
**Version:** 1.0 — Phased Execution Plan  
**Status:** Baseline Implementation Plan for Review & Approval  
**Product Name:** SourceIQ  
**Official Tagline:** AI Answers. Verifiable Sources.  
**Kickoff PRD Reference:** SourceIQ Kickoff PRD v0.1 (`SIQ-PRD-001`)  
**Product Category:** Evidence-First AI Document Intelligence Platform  

---

## 1. Executive Summary & Implementation Principles

This implementation plan defines the complete, phased engineering roadmap to construct the **SourceIQ** MVP.

### 1.1 Core Execution Rules
1. **Strict Sequence & Prerequisites:** Phases are ordered linearly. No phase begins until the preceding phase satisfies its complete Definition of Done.
2. **Local Development Docker-Free:** All local execution runs bare-metal on Windows (Python 3.12, FastAPI/Uvicorn, Node.js 24/Next.js, native PostgreSQL 18 with pgvector). Docker is strictly reserved for Phase 7 (Production Deployment).
3. **Evidence Grounding First:** Retrieval and citation validation are treated as critical software contracts, not optional prompt suggestions.
4. **No Premature Implementation:** This document establishes the plan; it is **not** authorization to begin coding before formal sign-off.
5. **Clear Separation of Post-MVP Capabilities:** Dedicated "Claim Verification Mode", "Cross-Document Contradiction Finder", and "Evidence-First Decision Brief" are strictly isolated in the Post-MVP Roadmap.

---

## 2. Master Phase Overview

```
+-----------------------------------------------------------------------------------------+
|                                SOURCEIQ IMPLEMENTATION ROADMAP                          |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [Phase 0] Requirements & Architecture Foundation                                       |
|      │                                                                                  |
|      ▼                                                                                  |
|  [Phase 1] Database & Backend Foundation (PostgreSQL, pgvector, Alembic)                |
|      │                                                                                  |
|      ▼                                                                                  |
|  [Phase 2] PDF Ingestion Pipeline (PyMuPDF, Chunking, Embeddings, Storage)              |
|      │                                                                                  |
|      ▼                                                                                  |
|  [Phase 3] Semantic Retrieval & Grounded RAG Pipeline                                    |
|      │                                                                                  |
|      ▼                                                                                  |
|  [Phase 4] Evidence & Citation Reliability (Deterministic Validator, Abstention)        |
|      │                                                                                  |
|      ▼                                                                                  |
|  [Phase 5] Frontend MVP (Next.js, Q&A Workspace, Citation Drawer, Comparison UI)        |
|      │                                                                                  |
|      ▼                                                                                  |
|  [Phase 6] Quality, Security & Release Readiness (Evaluations, Penetration Tests)       |
|      │                                                                                  |
|      ▼                                                                                  |
|  [Phase 7] Production Deployment Plan (Docker Packaging, Cloud Managed Postgres)       |
|      │                                                                                  |
|      ▼                                                                                  |
|  [POST-MVP] Advanced Capabilities (Claim Verification, Contradiction Finder, Briefs)    |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

---

## Phase 0 — Requirements and Foundation

### Objective
Verify complete product scope, establish project repository conventions, validate local runtime environments (Python 3.12, Node 24, PostgreSQL 18 with pgvector), and finalize foundational engineering decisions.

### Scope and Exclusions
- **In Scope:** Runtime environment verification, dependency specification manifests, configuration blueprints (`.env.example`), test runner configuration, coding conventions.
- **Exclusions:** Writing application logic, creating database tables, running live API queries.

### Dependencies
- Approved `docs/TECHNICAL-DESIGN.md` and `docs/IMPLEMENTATION-PLAN.md`.

### Deliverables
- Validated local runtime verification report (PowerShell outputs for Python, Node, psql).
- Project configuration manifests: `backend/pyproject.toml`, `backend/requirements.txt`, `backend/requirements-dev.txt`, `frontend/package.json`.
- Environment template files: `backend/.env.example`, `frontend/.env.example`.
- Global test runner and linting configurations: `pytest.ini`, `.ruff.toml`, `frontend/tsconfig.json`.

### Files or Modules Expected to Be Created
- `backend/.env.example`
- `backend/pyproject.toml`
- `backend/requirements.txt`
- `backend/requirements-dev.txt`
- `backend/pytest.ini`
- `frontend/.env.example`
- `frontend/package.json`
- `frontend/tsconfig.json`

### Ordered Implementation Tasks
1. **Task 0.1:** Verify native Windows PostgreSQL 18 installation and pgvector extension availability via `psql`.
2. **Task 0.2:** Create the root folder structure (`backend/`, `frontend/`, `docs/`, `data/uploads/`).
3. **Task 0.3:** Author `backend/requirements.txt` fixing core runtime dependencies (`fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `psycopg[binary]`, `pgvector`, `alembic`, `pymupdf`, `google-genai` / `openai`, `tenacity`).
4. **Task 0.4:** Author `backend/requirements-dev.txt` fixing development dependencies (`pytest`, `pytest-asyncio`, `httpx`, `ruff`).
5. **Task 0.5:** Author `frontend/package.json` fixing Next.js, React, Lucide icons, and Tailwind/CSS tooling.
6. **Task 0.6:** Author `.env.example` templates for backend and frontend with documentation comments.

### Acceptance Criteria
- Running `python -c "import fitz"` and `psql -c "CREATE EXTENSION IF NOT EXISTS vector;"` succeeds without errors.
- Python and Node package manifests have zero version conflicts.
- Environment templates document all required keys without exposing real credentials.

### Required Tests
- Smoke test: Python virtual environment creation and package installation verification script.
- Smoke test: Node dependency resolution check (`npm install --dry-run`).

### Definition of Done
Environment prerequisites are confirmed operational on Windows without Docker, package specifications are locked, and project skeleton directories are initialized.

### Risks and Dependencies
- **Risk:** Missing native C++ build tools for pgvector on Windows.
- **Mitigation:** Use precompiled binary packages or verify PostgreSQL version-matched installer.

### Decisions Requiring User Approval
- Confirm primary AI Provider (Google Gemini recommended vs. OpenAI).

---

## Phase 1 — Database and Backend Foundation

### Objective
Establish the FastAPI backend application structure, configure asynchronous database connectivity with SQLAlchemy, create the relational and vector schema via Alembic migrations, and configure centralized error handling.

### Scope and Exclusions
- **In Scope:** FastAPI app initialization, CORS middleware, config loading, SQLAlchemy session factory, ORM models, Alembic migration scripts, `/api/v1/health` endpoint, base unit test harness.
- **Exclusions:** PDF parsing, chunking, embedding generation, live LLM calls.

### Dependencies
- Completion of Phase 0.
- Running native PostgreSQL service on `localhost:5432`.

### Deliverables
- Working FastAPI app with CORS and healthcheck router.
- Fully configured SQLAlchemy 2.0 async/sync database session manager.
- Four core ORM models: `Workspace`, `Document`, `DocumentChunk`, `QueryRun`.
- Initial Alembic migration (`0001_initial_schema.py`) creating all tables and HNSW vector index.
- Comprehensive base database integration tests.

### Files or Modules Expected to Be Created
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/versions/0001_initial_schema.py`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/errors.py`
- `backend/app/core/logging.py`
- `backend/app/db/base.py`
- `backend/app/db/session.py`
- `backend/app/db/models/workspace.py`
- `backend/app/db/models/document.py`
- `backend/app/db/models/chunk.py`
- `backend/app/db/models/query_audit.py`
- `backend/app/schemas/workspace.py`
- `backend/app/api/deps.py`
- `backend/app/api/v1/router.py`
- `backend/app/api/v1/endpoints/health.py`
- `backend/app/api/v1/endpoints/workspaces.py`
- `backend/tests/conftest.py`
- `backend/tests/unit/test_config.py`
- `backend/tests/integration/test_db_models.py`
- `backend/tests/api/test_health_api.py`

### Ordered Implementation Tasks
1. **Task 1.1:** Implement `app/core/config.py` using Pydantic `BaseSettings` with type validation and defaults.
2. **Task 1.2:** Implement `app/core/logging.py` providing JSON formatted, sanitized logging.
3. **Task 1.3:** Implement `app/core/errors.py` declaring custom domain exceptions (`EntityNotFoundError`, `StorageLimitExceededError`, `ParsingError`) and global exception handlers.
4. **Task 1.4:** Implement `app/db/session.py` setting up engine and sessionmaker.
5. **Task 1.5:** Implement ORM models in `app/db/models/` using SQLAlchemy DeclarativeBase with pgvector column definitions.
6. **Task 1.6:** Initialize Alembic, configure `alembic/env.py` to target SQLAlchemy metadata, and generate `0001_initial_schema.py`.
7. **Task 1.7:** Execute `alembic upgrade head` and verify table, constraint, and index creation in PostgreSQL.
8. **Task 1.8:** Implement `app/main.py` assembling FastAPI router, CORS middleware, and registering `/health` and `/workspaces` endpoints.
9. **Task 1.9:** Write pytest test suite for config, DB cascading deletes, and healthcheck API.

### Acceptance Criteria
- `alembic upgrade head` creates all tables and HNSW vector index cleanly.
- `GET /api/v1/health` returns `200 OK` with database connection latency and status.
- Workspace CRUD API allows creating, listing, and deleting workspaces.
- Deleting a workspace cascades and removes all associated child records.

### Required Tests
- `pytest tests/unit/test_config.py` (verifies environment variable parsing and validation).
- `pytest tests/integration/test_db_models.py` (verifies table constraints, foreign keys, cascades).
- `pytest tests/api/test_health_api.py` (verifies HTTP 200 response on healthcheck).

### Definition of Done
Database migrations execute cleanly against native PostgreSQL, ORM models enforce relational constraints, FastAPI starts without warnings, and base tests pass with 100% green status.

### Risks and Dependencies
- **Risk:** Database connection timeouts or credentials mismatch.
- **Mitigation:** Clear error logging in `app/db/session.py` with immediate diagnostic messaging.

### Decisions Requiring User Approval
- None (follows standard SQLAlchemy/Alembic architecture approved in Design Document).

---

## Phase 2 — PDF Ingestion

### Objective
Implement the complete PDF ingestion pipeline: upload validation, secure filesystem storage, page-aware text extraction via PyMuPDF, recursive token chunking with provenance retention, dense vector embedding generation, and atomic persistence.

### Scope and Exclusions
- **In Scope:** PDF file validation (magic bytes, size), storage adapter, PyMuPDF parsing, empty/scanned PDF detection, chunking logic, embedding provider integration, batch persistence, document status tracking (`PENDING` $\to$ `PARSING` $\to$ `EMBEDDING` $\to$ `READY` / `FAILED`).
- **Exclusions:** OCR for scanned documents (detected and cleanly rejected), semantic retrieval queries.

### Dependencies
- Completion of Phase 1.
- Active AI Provider API Key (`GEMINI_API_KEY` or `OPENAI_API_KEY`).

### Deliverables
- `StorageService` for local filesystem management.
- `ParserService` for page-isolated text extraction via PyMuPDF.
- `ChunkingService` with configurable token size, overlap, and metadata preservation.
- `EmbeddingService` wrapping the external embedding model gateway.
- `DocumentService` orchestrating the ingestion pipeline.
- Document upload and status endpoints (`/workspaces/{id}/documents/upload`, `GET /documents/{id}`).
- Comprehensive unit and integration test suite for PDF ingestion.

### Files or Modules Expected to Be Created
- `backend/app/services/storage_service.py`
- `backend/app/services/parser_service.py`
- `backend/app/services/chunking_service.py`
- `backend/app/services/embedding_service.py`
- `backend/app/services/document_service.py`
- `backend/app/providers/base.py`
- `backend/app/providers/gemini_provider.py`
- `backend/app/providers/openai_provider.py`
- `backend/app/schemas/document.py`
- `backend/app/schemas/chunk.py`
- `backend/app/api/v1/endpoints/documents.py`
- `backend/tests/unit/test_parser.py`
- `backend/tests/unit/test_chunking.py`
- `backend/tests/integration/test_embedding_service.py`
- `backend/tests/integration/test_ingestion_flow.py`

### Ordered Implementation Tasks
1. **Task 2.1:** Implement `StorageService` providing secure file write, read, and delete operations on `data/uploads/<workspace_id>/<doc_id>.pdf`.
2. **Task 2.2:** Implement `ParserService` using `fitz` (PyMuPDF) to extract per-page text and detect scanned/empty PDFs.
3. **Task 2.3:** Implement `ChunkingService` to split page texts into 500-token chunks with 50-token overlap, tagging each chunk with `doc_id`, `page_number`, and `chunk_index`.
4. **Task 2.4:** Implement `EmbeddingProviderInterface` in `app/providers/base.py` and concrete `GeminiProvider` / `OpenAIProvider`.
5. **Task 2.5:** Implement `EmbeddingService` handling chunk batching (16 chunks/batch) and exponential backoff retry.
6. **Task 2.6:** Implement `DocumentService` coordinating upload validation, DB record creation, background ingestion execution, and status transitions.
7. **Task 2.7:** Implement document API endpoints in `app/api/v1/endpoints/documents.py` supporting multipart file uploads, status polling, and document deletion.
8. **Task 2.8:** Write unit tests for parser and chunker, plus end-to-end integration test with sample digital and scanned test PDFs.

### Acceptance Criteria
- Uploading a valid digital PDF creates a document record and transitions status to `READY` with correct `page_count` and `chunk_count`.
- All generated `DocumentChunk` records have valid vector embeddings and correct page numbers.
- Uploading a file $>10$ MB or non-PDF returns `400 Bad Request` or `413 Payload Too Large`.
- Uploading a scanned PDF transitions status to `FAILED` with error message: *"Scanned or image-only PDFs are not supported in the MVP."*
- Deleting a document removes its physical PDF file and all corresponding vector chunks from the database.

### Required Tests
- `pytest tests/unit/test_parser.py` (tests text extraction, page numbering, empty page handling).
- `pytest tests/unit/test_chunking.py` (tests chunk token boundaries, overlap continuity, index ordering).
- `pytest tests/integration/test_ingestion_flow.py` (runs complete upload $\to$ parse $\to$ embed $\to$ DB cycle).

### Definition of Done
PDF documents are parsed with 100% page-provenance fidelity, chunked into vectors in PostgreSQL, and document status is accurately trackable via REST APIs.

### Risks and Dependencies
- **Risk:** Ingestion blocking the API event loop for large PDFs.
- **Mitigation:** Execute extraction and embedding inside FastAPI `BackgroundTasks` with threadpool isolation.

### Decisions Requiring User Approval
- Confirm maximum page limit cap per document (e.g., 30 pages recommended for MVP).

---

## Phase 3 — Retrieval and RAG

### Objective
Implement question vectorization, permission-filtered vector similarity search in PostgreSQL, context assembly, and evidence-grounded answer synthesis using the external LLM.

### Scope and Exclusions
- **In Scope:** Query embedding, cosine distance vector search (`<=>`), SQL metadata pre-filtering by workspace and document list, prompt assembly with `<document_evidence>` XML tags, structured LLM generation, basic grounded answering.
- **Exclusions:** Multi-turn conversational memory (MVP is single-turn focused Q&A per query), automated contradiction mining.

### Dependencies
- Completion of Phase 2.
- Ingested test documents with generated embeddings in the database.

### Deliverables
- `RetrievalService` executing SQL-level filtered vector search.
- `QAService` assembling grounded context prompts and invoking LLM.
- Grounded query API endpoint: `POST /api/v1/workspaces/{id}/qa/query`.
- Retrieval recall and RAG grounding integration test suite.

### Files or Modules Expected to Be Created
- `backend/app/services/retrieval_service.py`
- `backend/app/services/qa_service.py`
- `backend/app/schemas/qa.py`
- `backend/app/api/v1/endpoints/qa.py`
- `backend/tests/unit/test_retrieval_service.py`
- `backend/tests/integration/test_rag_pipeline.py`
- `backend/tests/api/test_qa_api.py`

### Ordered Implementation Tasks
1. **Task 3.1:** Implement `RetrievalService` executing cosine distance vector queries filtered by `workspace_id` and optional `document_ids`.
2. **Task 3.2:** Add similarity score thresholding (`SIMILARITY_THRESHOLD = 0.65`) to filter out semantically irrelevant noise.
3. **Task 3.3:** Design the structured system prompt and user prompt templates wrapping retrieved passages in `<document_evidence>` tags with assigned keys (`CIT-1`, `CIT-2`, etc.).
4. **Task 3.4:** Implement `QAService` orchestrating query embedding, candidate retrieval, prompt formatting, and LLM structured invocation.
5. **Task 3.5:** Implement the Q&A endpoint in `app/api/v1/endpoints/qa.py` accepting `QueryRequest` and returning `GroundedAnswerResponse`.
6. **Task 3.6:** Write unit and integration tests verifying retrieval filtering and answer grounding.

### Acceptance Criteria
- Querying retrieves only chunks belonging to the target workspace.
- Chunks below the similarity threshold are excluded from prompt context.
- The LLM receives clean, XML-isolated passages and produces answers referencing citation keys.
- Query runs are audited in the `query_runs` table with recorded latency.

### Required Tests
- `pytest tests/unit/test_retrieval_service.py` (verifies SQL query generation, parameter binding, and scoring).
- `pytest tests/integration/test_rag_pipeline.py` (verifies end-to-end question $\to$ retrieval $\to$ LLM response flow).
- `pytest tests/api/test_qa_api.py` (verifies API request/response contracts and error handling).

### Definition of Done
User questions reliably retrieve top-$k$ relevant passages and generate structured answers with inline citation keys, strictly partitioned by workspace.

### Risks and Dependencies
- **Risk:** LLM provider latency spikes or timeouts.
- **Mitigation:** Enforce 15-second client timeouts and clear fallback error messaging.

### Decisions Requiring User Approval
- Confirm default `top_k` chunk retrieval count (5 recommended).

---

## Phase 4 — Evidence and Citation Reliability

### Objective
Implement deterministic server-side citation validation, transparent abstention on unanswerable questions, cross-document topic comparison (FR-07), and evidence inspection endpoints.

### Scope and Exclusions
- **In Scope:** Server-side citation mapping and verification, phantom citation stripping, substring/fuzzy passage match validation, explicit abstention logic, multi-document comparison query pipeline (FR-07), evidence context inspection endpoint (`GET /evidence/{chunk_id}`).
- **Exclusions:** Autonomous claim verification classifier, cross-document contradiction finder (post-MVP).

### Dependencies
- Completion of Phase 3.

### Deliverables
- `CitationValidator` service ensuring 100% verifiable citations.
- Abstention policy handler returning explicit `INSUFFICIENT_EVIDENCE` states.
- `ComparisonService` synthesizing side-by-side perspectives across 2+ documents.
- Evidence inspection endpoint: `GET /api/v1/evidence/{chunk_id}`.
- Citation reliability, abstention, and cross-document comparison test suites.

### Files or Modules Expected to Be Created
- `backend/app/services/citation_validator.py`
- `backend/app/services/comparison_service.py`
- `backend/app/schemas/comparison.py`
- `backend/app/api/v1/endpoints/evidence.py`
- `backend/app/api/v1/endpoints/comparison.py`
- `backend/tests/unit/test_citation_validator.py`
- `backend/tests/unit/test_abstention.py`
- `backend/tests/integration/test_comparison_flow.py`

### Ordered Implementation Tasks
1. **Task 4.1:** Implement `CitationValidator`:
   - Map LLM citation keys (`CIT-1`) back to actual database chunk records.
   - Detect and discard phantom citation keys not provided in the prompt.
   - Verify that quoted snippets exist within the cited chunk text.
   - Attach verified document filenames, page numbers, and chunk IDs.
2. **Task 4.2:** Implement the Abstention Policy:
   - When candidate chunks are empty or below similarity threshold, return `status: "INSUFFICIENT_EVIDENCE"`.
   - When the LLM indicates information is missing, abstain cleanly rather than fabricating an answer.
3. **Task 4.3:** Implement `ComparisonService` (FR-07):
   - Accept a topic and 2+ document IDs.
   - Retrieve top chunks for each document independently.
   - Prompt the LLM to present structured per-document findings with citations.
4. **Task 4.4:** Implement `GET /api/v1/evidence/{chunk_id}` returning verbatim chunk content and adjacent page context for user inspection.
5. **Task 4.5:** Implement `POST /api/v1/workspaces/{id}/comparison/query` endpoint.
6. **Task 4.6:** Write comprehensive test suites for citation validation, abstention, and multi-document comparison.

### Acceptance Criteria
- 100% of citations in the API response map to real, retrieved chunks with verified page numbers.
- Hallucinated or non-existent citation keys are stripped with an audit warning.
- Negative-control test questions (answers not in documents) produce explicit abstention answers.
- Comparison API returns structured per-document findings without inventing consensus.

### Required Tests
- `pytest tests/unit/test_citation_validator.py` (verifies phantom key rejection and snippet matching).
- `pytest tests/unit/test_abstention.py` (verifies abstention triggering on low similarity).
- `pytest tests/integration/test_comparison_flow.py` (verifies multi-document comparison synthesis).

### Definition of Done
Every claim in a generated answer is verified against database evidence, ungrounded claims are rejected or flagged, and users can inspect exact source text passages.

### Risks and Dependencies
- **Risk:** Minor whitespace or punctuation differences between LLM quote and raw text.
- **Mitigation:** Use normalized whitespace token matching with an 80% overlap threshold.

### Decisions Requiring User Approval
- Confirm fuzzy matching overlap threshold (80% recommended).

---

## Phase 5 — Frontend MVP

### Objective
Build the Next.js 14+ TypeScript user interface providing an evidence-first experience: workspace management, PDF upload dropzone with live processing status, grounded Q&A interface with interactive citation badges, evidence inspector drawer, and cross-document comparison view.

### Scope and Exclusions
- **In Scope:** Workspace switcher, drag-and-drop PDF uploader, status polling, Q&A search with document scope filter, answer card with clickable citation badges, slide-over evidence inspector drawer, cross-document comparison matrix, responsive accessible styling.
- **Exclusions:** User registration/login forms (uses workspace switcher for college demo), PDF canvas rendering (shows extracted text passages with page labels).

### Dependencies
- Completion of Phase 4 (all backend endpoints operational and validated).

### Deliverables
- Next.js application with App Router and TypeScript.
- Workspace manager view (`/workspaces`).
- Primary workspace dashboard (`/workspaces/[id]`): Document Library + Q&A.
- Evidence drawer component displaying verified source text excerpts.
- Cross-document comparison view (`/workspaces/[id]/compare`).
- Comprehensive frontend component tests.

### Files or Modules Expected to Be Created
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/app/workspaces/page.tsx`
- `frontend/src/app/workspaces/[workspaceId]/page.tsx`
- `frontend/src/app/workspaces/[workspaceId]/compare/page.tsx`
- `frontend/src/components/common/Button.tsx`
- `frontend/src/components/common/Badge.tsx`
- `frontend/src/components/common/Modal.tsx`
- `frontend/src/components/documents/DocumentUploadDropzone.tsx`
- `frontend/src/components/documents/DocumentList.tsx`
- `frontend/src/components/documents/DocumentStatusBadge.tsx`
- `frontend/src/components/qa/QueryInput.tsx`
- `frontend/src/components/qa/DocumentScopePicker.tsx`
- `frontend/src/components/qa/AnswerCard.tsx`
- `frontend/src/components/qa/AbstentionAlert.tsx`
- `frontend/src/components/citations/CitationChip.tsx`
- `frontend/src/components/citations/EvidenceDrawer.tsx`
- `frontend/src/components/comparison/ComparisonMatrix.tsx`
- `frontend/src/lib/api-client.ts`
- `frontend/src/types/` (all shared schema definitions)
- `frontend/tests/components/` (component tests)

### Ordered Implementation Tasks
1. **Task 5.1:** Initialize Next.js project structure, Tailwind/CSS design tokens, and root layout with SourceIQ branding.
2. **Task 5.2:** Implement `api-client.ts` with typed error handling and configurable base URL.
3. **Task 5.3:** Build Workspace views (`/workspaces` and `/workspaces/[id]`).
4. **Task 5.4:** Implement `DocumentUploadDropzone` and `DocumentList` with live polling for status (`PROCESSING` $\to$ `READY`).
5. **Task 5.5:** Build Q&A components: `QueryInput`, `DocumentScopePicker`, `AnswerCard`, and `AbstentionAlert`.
6. **Task 5.6:** Implement `CitationChip` and slide-over `EvidenceDrawer` to display verbatim chunk text upon clicking a citation.
7. **Task 5.7:** Build Cross-Document Comparison view (`/workspaces/[id]/compare`) displaying side-by-side document findings.
8. **Task 5.8:** Add comprehensive loading skeletons, empty states, and toast notifications.
9. **Task 5.9:** Write frontend unit and component tests.

### Acceptance Criteria
- User can create a workspace, upload a PDF, and observe status transitions cleanly.
- Asking a question displays the answer with interactive citation chips (`[report.pdf, p. 4]`).
- Clicking a citation chip opens the Evidence Drawer showing the exact verified source excerpt.
- Asking an unanswerable question renders the `AbstentionAlert` explaining insufficient evidence.
- Multi-document comparison displays findings side-by-side with individual citations.

### Required Tests
- Component test: `CitationChip` renders correct page label and triggers drawer on click.
- Component test: `AbstentionAlert` renders when answer status is `INSUFFICIENT_EVIDENCE`.
- End-to-end user flow: Upload PDF $\to$ wait for READY $\to$ submit query $\to$ inspect citation.

### Definition of Done
The full-stack application runs smoothly on Windows, UI displays verified evidence with zero layout jank, and all interactive features are fully functional.

### Risks and Dependencies
- **Risk:** Polling hammering backend on large uploads.
- **Mitigation:** Use progressive polling (1s, 2s, 3s, max 5s) and stop polling immediately upon terminal state (`READY` or `FAILED`).

### Decisions Requiring User Approval
- Final color palette approval (Deep Navy / Slate / Emerald for verified citations).

---

## Phase 6 — Quality, Security, and Release Readiness

### Objective
Execute comprehensive quality assurance across software correctness, security posture, and AI grounding quality; build the automated evaluation benchmark suite; and finalize project documentation.

### Scope and Exclusions
- **In Scope:** Full automated test suite execution (unit, integration, API), prompt injection penetration tests, document deletion audit, curated 20-case AI benchmark suite, performance profiling, setup documentation verification.
- **Exclusions:** Live cloud security scanning (reserved for production hosting).

### Dependencies
- Completion of Phase 5.

### Deliverables
- Curated evaluation dataset (`backend/app/evaluation/dataset.json`) with 20 documented test cases (positive & negative controls).
- Automated CLI evaluator (`python -m app.evaluation.evaluator`) outputting hit rate, citation validity, and abstention metrics.
- Complete automated test suite passing with $>85\%$ code coverage.
- Security audit report covering prompt injection, file upload safety, and parameterized queries.
- Clean, step-by-step developer setup guide in `README.md`.

### Files or Modules Expected to Be Created
- `backend/app/evaluation/dataset.json`
- `backend/app/evaluation/evaluator.py`
- `backend/tests/eval/test_curated_benchmark.py`
- `backend/tests/security/test_prompt_injection.py`
- `backend/tests/security/test_upload_safety.py`
- `README.md`

### Ordered Implementation Tasks
1. **Task 6.1:** Curate 20 benchmark test cases across sample domain PDFs:
   - 12 standard factual retrieval queries with known target pages.
   - 4 cross-document comparison queries.
   - 4 negative-control queries (facts absent from documents to test abstention).
2. **Task 6.2:** Implement `evaluator.py` CLI script executing the 20 benchmark queries and printing an evaluation summary table.
3. **Task 6.3:** Write security penetration tests for prompt injection (`<document_evidence>` escape attempts) and path traversal uploads.
4. **Task 6.4:** Verify document cascade deletion cleans up all physical files, database rows, and vector embeddings.
5. **Task 6.5:** Profile memory usage on Windows to verify process stays well within 4 GB RAM budget (< 350 MB RAM for FastAPI + PostgreSQL).
6. **Task 6.6:** Author root `README.md` with complete, reproducible local setup and demo instructions.

### Acceptance Criteria
- 100% of automated unit, integration, and API tests pass.
- Curated evaluation benchmark reports:
  - Retrieval Hit Rate $\ge 90\%$.
  - Citation Validity Rate = $100\%$.
  - Negative Control Abstention Rate = $100\%$.
- Security tests confirm prompt injections inside PDFs cannot override system instructions.
- A new developer can clone the repo and run the application following `README.md` without missing steps.

### Required Tests
- `pytest tests/` (full test suite execution).
- `python -m app.evaluation.evaluator` (benchmark execution).
- `pytest tests/security/` (security tests).

### Definition of Done
Test suite passes with 100% green status, AI benchmark validates grounding and abstention, security defenses are verified, and documentation is complete.

### Risks and Dependencies
- **Risk:** External AI provider output variance during automated evaluation.
- **Mitigation:** Use temperature 0.0 for evaluation runs to maximize determinism.

### Decisions Requiring User Approval
- Review and approve final benchmark metric thresholds.

---

## Phase 7 — Production Deployment

### Objective
Package the application for production deployment using Docker containers, configure deployment to managed cloud PostgreSQL (e.g., Supabase PostgreSQL with pgvector), configure cloud persistent storage, and implement operational health checks.

### Scope and Exclusions
- **In Scope:** Production multi-stage Dockerfiles (`backend/Dockerfile`, `frontend/Dockerfile`), production environment configuration templates, Supabase / cloud PostgreSQL setup guide, automated migration entrypoints, health check endpoints.
- **Exclusions:** Local Docker usage (local remains bare-metal Windows), premature Kubernetes or microservice clustering.

### Dependencies
- Completion of Phase 6.

### Deliverables
- Production `backend/Dockerfile` and `frontend/Dockerfile`.
- Production `docker-compose.prod.yml` (for single-server cloud host deployment).
- Database migration execution script for production container startup.
- Production environment documentation and secrets checklist.

### Files or Modules Expected to Be Created
- `backend/Dockerfile`
- `backend/entrypoint.sh`
- `frontend/Dockerfile`
- `docker-compose.prod.yml`
- `docs/PRODUCTION-DEPLOYMENT.md`

### Ordered Implementation Tasks
1. **Task 7.1:** Author multi-stage, rootless `backend/Dockerfile` optimizing image size (< 180 MB).
2. **Task 7.2:** Author multi-stage `frontend/Dockerfile` utilizing Next.js standalone output.
3. **Task 7.3:** Author `docker-compose.prod.yml` defining production backend, frontend, and reverse proxy networking.
4. **Task 7.4:** Write database migration runner in `backend/entrypoint.sh` executing `alembic upgrade head` before starting Uvicorn.
5. **Task 7.5:** Author `docs/PRODUCTION-DEPLOYMENT.md` detailing cloud setup with Supabase PostgreSQL, environment secrets, and monitoring.

### Acceptance Criteria
- Production Docker images build without warnings.
- Backend container successfully executes migrations on startup and serves traffic.
- Health check endpoints (`/health`) return 200 OK under containerized runtime.
- Zero secrets or API keys are baked into Docker image layers.

### Required Tests
- Production container build and startup smoke test in staging/CI environment.
- Healthcheck curl test against containerized service.

### Definition of Done
Production container assets are validated, database migrations run reliably on container startup, and deployment documentation is verified.

### Risks and Dependencies
- **Risk:** Cloud database latency or pgvector extension version mismatches.
- **Mitigation:** Document required pgvector extension versions in deployment guide.

### Decisions Requiring User Approval
- Confirm target cloud hosting provider (e.g., Render / Railway / Supabase / AWS).

---

## Post-MVP — Advanced Capabilities

The following features are **explicitly excluded from the MVP** and are scheduled for post-MVP releases:

### 1. Claim Verification Mode
- **Description:** A dedicated interface where users input a specific factual hypothesis. The system decomposes the claim, retrieves supporting and contradicting passages across the corpus, and assigns a calibrated verdict: `SUPPORTED`, `CONTRADICTED`, or `UNVERIFIABLE`, with supporting citations for each verdict.
- **Prerequisites:** Completion of MVP, fine-tuned verification prompts, extensive benchmark dataset of fact-checking claims.

### 2. Cross-Document Contradiction Finder
- **Description:** An automated, asynchronous analysis engine that scans an entire multi-document workspace to detect conflicting claims (e.g., differing dates, conflicting financial metrics, opposing policy clauses) without requiring user-prompted comparison questions.
- **Prerequisites:** MVP comparison service, background worker queue (Celery/Redis), cluster-based entity resolution.

### 3. Evidence-First Decision Brief
- **Description:** An executive reporting tool that synthesizes document collections into structured decision briefs containing key findings, opposing evidence, confidence ratings, missing information gaps, and recommended actions.
- **Prerequisites:** Multi-section long-form synthesis pipeline, PDF report export capabilities.

---

## 3. Project Schedule & Phase Dependency Matrix

| Phase | Milestone Name | Prerequisites | Est. Effort | Critical Deliverable |
| :---: | :--- | :--- | :---: | :--- |
| **0** | Requirements & Foundation | Approved PRD & Technical Design | 1 Day | Verified Windows runtime, package manifests |
| **1** | Database & Backend Foundation | Phase 0 | 2 Days | Native PostgreSQL schema, Alembic migrations, `/health` |
| **2** | PDF Ingestion Pipeline | Phase 1 | 3 Days | PyMuPDF extraction, token chunking, pgvector persistence |
| **3** | Retrieval & Grounded RAG | Phase 2 | 2 Days | Filtered vector search, XML context assembly, Q&A API |
| **4** | Evidence & Citation Reliability | Phase 3 | 2 Days | Deterministic citation validator, abstention policy, FR-07 |
| **5** | Frontend MVP | Phase 4 | 4 Days | Next.js workspace UI, Q&A, Evidence Drawer, Compare UI |
| **6** | Quality, Security & Readiness | Phase 5 | 2 Days | 20-case evaluation benchmark, security tests, README |
| **7** | Production Deployment | Phase 6 | 1 Day | Production Dockerfiles, Supabase setup guide |
| **Post**| Advanced Capabilities | Phase 7 | Future | Claim Verification, Contradiction Finder, Decision Briefs |
