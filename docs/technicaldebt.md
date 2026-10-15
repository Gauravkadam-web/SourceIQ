# SourceIQ — Technical Debt & Architectural Ledger

**Document ID:** SIQ-DEBT-001  
**Last Updated:** 2026-10-15  
**Product Name:** SourceIQ  
**Architecture:** Modular Monolith (FastAPI + Next.js 14 + Supabase PostgreSQL/pgvector + Supabase Storage)  

---

## 🧭 Overview & Philosophy

This document tracks deliberate trade-offs, known system limitations, and technical debt accumulated during rapid MVP delivery. Each item is documented with its current rationale, impact, severity, and planned remediation roadmap.

---

## 📋 Technical Debt Register

### 1. In-Process Auto-Migration on Container Startup
- **Category:** Infrastructure / Database Lifecycle
- **Severity:** Low (for single-replica Render Free Tier) / Medium (for horizontal scaling)
- **Current Implementation:** The Docker container runs `alembic upgrade head` in its startup `CMD`, and FastAPI `lifespan` runs `Base.metadata.create_all(bind=engine)`.
- **Why It Was Done:** Render Free Tier does not provide interactive Web Shell access. Automatically running migrations on container boot enables zero-touch deployment for the user.
- **Limitation / Debt:** If the backend is scaled horizontally to multiple concurrent container replicas, simultaneous startup migrations could trigger race conditions or DDL lock contentions.
- **Remediation Roadmap:** When upgrading to a multi-instance production plan, move migrations to a dedicated CI/CD GitHub Actions pre-deploy step or Render "Release Command".

---

### 2. Ephemeral Disk Fallback with Supabase Storage
- **Category:** Storage / File Persistence
- **Severity:** Low
- **Current Implementation:** Documents are uploaded to Supabase Storage bucket `sourceiq-documents` via REST API multipart upload. For PyMuPDF extraction, files are cached locally in `/data/uploads`. If a container restarts and a document is requested, `ensure_local_copy` downloads it on-demand from Supabase.
- **Why It Was Done:** Render free containers have ephemeral filesystems that reset on restart or spin-down.
- **Limitation / Debt:** Large PDFs (e.g. 10MB) must be downloaded over HTTP before parsing. Deletion requires two separate network calls (local file + Supabase bucket).
- **Remediation Roadmap:** Stream PDF bytes directly to `fitz.open(stream=bytes, filetype="pdf")` without writing to local disk during on-demand extraction, eliminating disk I/O completely.

---

### 3. Fixed Vector Dimensions & Model Coupling
- **Category:** Retrieval & Embeddings
- **Severity:** Medium
- **Current Implementation:** Stored in a fixed-dimension pgvector column `Vector(768)` corresponding to Google Gemini `text-embedding-004` / `gemini-embedding-001`.
- **Why It Was Done:** PostgreSQL pgvector requires fixed column dimensions at table creation (`sa.Column('embedding', Vector(768))`).
- **Limitation / Debt:** Switching to OpenAI (`text-embedding-3-small`, 1536 dims) or local Ollama (e.g. 1024 dims) requires a schema migration and complete re-embedding of existing document chunks.
- **Remediation Roadmap:** For post-MVP multi-model support, introduce a multi-column embedding table (e.g. `embedding_768`, `embedding_1536`) or model-namespaced embedding rows with a `model_id` foreign key.

---

### 4. Cosine Similarity Calibration vs. Hybrid Search
- **Category:** Retrieval Precision
- **Severity:** Low / Medium
- **Current Implementation:** Single semantic vector similarity with threshold `0.48`.
- **Why It Was Done:** Calibrated to handle both short keyword queries (which often have lower raw cosine similarity ~0.50–0.55 against 500-token chunks) while strictly abstaining on negative controls (< 0.40).
- **Limitation / Debt:** Pure vector search can sometimes struggle with exact keyword lookups (e.g. exact model numbers, acronyms, or specific codes) where dense embeddings produce lower similarity than lexical matches.
- **Remediation Roadmap:** Implement Hybrid Search combining PostgreSQL Full-Text Search (tsvector / BM25) and pgvector semantic distance with Reciprocal Rank Fusion (RRF), as outlined in the Post-MVP architectural roadmap.

---

### 5. Client-Side Workspace Scoping vs. Authentication
- **Category:** Security / Multi-Tenancy
- **Severity:** Low (Approved for MVP) / High (for Multi-User Production)
- **Current Implementation:** Workspaces are isolated via UUID foreign keys on every query, retrieval, chunk, and document. Frontend stores selected workspace ID in browser local storage.
- **Why It Was Done:** PRD explicitly scoped the MVP to workspace-level isolation without requiring complex user authentication or OAuth flows.
- **Limitation / Debt:** Any client knowing a workspace UUID could theoretically access documents in that workspace if no network-level firewall is applied.
- **Remediation Roadmap:** Implement Supabase Auth / NextAuth.js with JWT token validation in FastAPI dependency `get_current_user` in Phase 8 (Post-MVP).

---

### 6. CORS Configuration Tightening
- **Category:** Network Security
- **Severity:** Low
- **Current Implementation:** `CORS_ORIGINS` currently permits `localhost:3000`, `127.0.0.1:3000`, and `https://sourceiq-m08k.onrender.com`.
- **Why It Was Done:** Allows seamless local development testing alongside the live Render deployment.
- **Limitation / Debt:** When Vercel frontend is finalized with a custom production domain, the domain list must be explicitly updated.
- **Remediation Roadmap:** Once Vercel deployment URL is locked, add the exact Vercel URL to `CORS_ORIGINS` in Render environment settings.

---

### 7. Scanned PDF Graceful Rejection (No OCR in MVP)
- **Category:** PDF Extraction
- **Severity:** Low (Explicit PRD Constraint)
- **Current Implementation:** PyMuPDF extracts digital text streams. Scanned or image-only PDFs with < 50 characters extract as empty text and are rejected with `ParsingError: Document contains no extractable digital text (scanned PDF)`.
- **Why It Was Done:** OCR (Tesseract / Cloud Vision) was explicitly placed out of MVP scope in `AGENTS.md` and the PRD to maintain fast, low-cost ingestion.
- **Remediation Roadmap:** Add optional OCR worker (Tesseract or Gemini 1.5 Flash multimodal vision) for scanned PDFs in Post-MVP Phase 9.
