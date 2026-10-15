# SourceIQ — Project Progress & Milestone Status

**Document ID:** SIQ-PRG-001  
**Last Updated:** 2026-10-15  
**Product Name:** SourceIQ  
**Tagline:** AI Answers. Verifiable Sources.  
**Repository:** `Gauravkadam-web/SourceIQ`  
**Current Milestone:** Phase 7 Completed — Live Cloud Deployment & End-to-End Verification  

---

## 🚀 Live Production Deployment

| Service | Platform | Configuration & Status | Live URL |
| :--- | :--- | :--- | :--- |
| **Backend API** | Render (Free Tier) | Docker container (`python:3.12-slim`), Uvicorn, FastAPI | `https://sourceiq-m08k.onrender.com/api/v1` |
| **Database** | Supabase | PostgreSQL 18 with `pgvector` v0.8.2 extension (16ms latency) | Supabase Managed |
| **Document Storage** | Supabase Storage | Private bucket `sourceiq-documents` (REST API multipart upload) | `sourceiq-documents` bucket |
| **Frontend** | Vercel | Next.js 14 (App Router), Vanilla CSS Design Tokens | Vercel Deployment |
| **AI Models** | Google AI Studio | Gemini 3.1 Flash Lite (LLM) + `gemini-embedding-001` / `text-embedding-004` | Google Cloud Gateway |

---

## 📊 Phase-by-Phase Completion Status

```
[Phase 0] Requirements & Architecture Foundation           ==> 100% COMPLETED
[Phase 1] Database & Backend Foundation (PostgreSQL/pgvector)==> 100% COMPLETED
[Phase 2] PDF Ingestion Pipeline (PyMuPDF, Chunking, Storage)==> 100% COMPLETED
[Phase 3] Semantic Retrieval & Grounded RAG Pipeline        ==> 100% COMPLETED
[Phase 4] Evidence & Citation Reliability (Abstention)       ==> 100% COMPLETED
[Phase 5] Frontend MVP (Next.js, Q&A, Compare, Evidence)    ==> 100% COMPLETED
[Phase 6] Quality, Security & Repeatable Evaluation         ==> 100% COMPLETED
[Phase 7] Production Cloud Deployment & Live Verification    ==> 100% COMPLETED
```

---

## 🧪 Automated Testing & Verification Telemetry

### 1. Backend Test Suite (Pytest)
- **Results:** `42 passed in 4.62s` (100% green).
- **Unit Tests:** Parser provenance, sliding-window chunking, configuration validation, provider factory fallback, citation reference validator, cosine similarity calculation.
- **Integration Tests:** End-to-end ingestion pipeline, multi-document comparison context builder.
- **API Tests:** Workspace CRUD, document upload/validation/isolation, Q&A grounded queries, negative control abstention, evidence inspection drawer, curated evaluation run.

### 2. Frontend Production Build (Next.js 14)
- **Status:** 100% Clean Standalone Production Build (`npm run build`).
- **Routes Compiled (7/7):**
  - `/` — Core Grounded Q&A Workspace
  - `/_not-found` — 404 Error handler
  - `/compare` — Multi-Document Comparison Matrix
  - `/documents` — Document Ingestion & Status Management
  - `/evaluation` — Curated Benchmark Runner & Live Telemetry
- **Assets:** Fully self-contained, unignored `src/lib/api.ts` resolved.

### 3. Live Production Crawling Verification (`https://sourceiq-m08k.onrender.com/api/v1`)
Automated verification script executed on the live Render + Supabase instance:

| # | Step / Feature | Result | Telemetry Details |
| :-: | :--- | :-: | :--- |
| **1** | Health Check (`GET /health`) | **PASSED** | HTTP 200 (290ms) • DB: Healthy (16ms latency) • `pgvector` v0.8.2 enabled |
| **2** | Workspace Listing (`GET /workspaces/`) | **PASSED** | HTTP 200 • Scoped multi-tenant workspace list |
| **3** | Workspace Creation (`POST /workspaces/`) | **PASSED** | HTTP 201 • Persistent UUID generation |
| **4** | PDF Upload (`POST /documents/upload`) | **PASSED** | Multipart upload stored in Supabase Storage Bucket |
| **5** | Ingestion Pipeline (`GET /documents/{id}`) | **PASSED** | Completed in **3 seconds** • 2 pages, 2 chunks embedded in `pgvector` |
| **6** | Grounded Q&A (`POST /qa/query`) | **PASSED** | `status: GROUNDED` • Answer: *"In Project Apollo, the lunar module was named Eagle [CIT-1]."* • Verified Page 1 Citation |
| **7** | Honest Abstention (`POST /qa/query`) | **PASSED** | Negative control query correctly returned `status: INSUFFICIENT_EVIDENCE` |
| **8** | Document 2 Ingestion (`POST /upload`) | **PASSED** | Uploaded `artemis_mission.pdf` • Status: `READY` in 3s |
| **9** | Multi-Doc Comparison (`POST /comparison/query`) | **PASSED** | `status: DIFFERENT_SCOPES` • Findings per document with verified citations |
| **10**| Evaluation Benchmark (`POST /evaluation/run`) | **PASSED** | HTTP 200 (23.5s) • **Hit Rate: 100%**, **Citations: 100%**, **Abstention: 100%** |
| **11**| Workspace & Document Deletion | **PASSED** | Complete purge from Supabase storage and database without orphan records |

---

## 📅 Chronological Session Milestones

1. **Rule Hardening (AGENTS.md):** Implemented strict zero-touch rule for `.env` files; all agent configuration updates directed to `.env.example` only with safe placeholders.
2. **Retrieval Calibration:** Resolved strict threshold issue by recalibrating `SIMILARITY_THRESHOLD` from `0.65` to `0.48` for 500-token chunks with `text-embedding-004`. Verified negative controls still properly abstain.
3. **Supabase Cloud Storage Integration:** Built dual-mode storage service (`STORAGE_BACKEND=supabase`) enabling persistent PDF uploads into Supabase Storage buckets, resolving Render ephemeral disk limitations.
4. **Zero-Shell Auto-Migration:** Embedded Alembic startup migration (`sh -c "alembic upgrade head && uvicorn ..."`) and SQLAlchemy `Base.metadata.create_all` lifespan execution, eliminating the need for manual shell access on Render Free Tier.
5. **Vercel Build Fix:** Removed accidental `lib/` ignore pattern from `.gitignore` that was blocking `frontend/src/lib/api.ts` from being committed to Git.
6. **Live Production Crawling:** Executed full automated crawler against Render production deployment, confirming 11/11 tests passing.
