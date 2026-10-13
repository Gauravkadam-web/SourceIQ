# AGENTS.md — SourceIQ Project Rules for Antigravity

**Read this file completely before inspecting, planning, editing, testing, or generating code for SourceIQ.**

These rules are the project-level instructions for AI coding agents. Follow them together with the original PRD, the current Technical Design Document (TDD), the Implementation Plan, and any explicit decisions approved by the project owner.

If these sources conflict, do not silently choose one. Stop, explain the conflict, and ask for a decision. Never treat an assumption or an agent suggestion as an approved product decision.

---

## 1. Project Identity

- **Product:** SourceIQ
- **Tagline:** AI Answers. Verifiable Sources.
- **Product goal:** Build a demonstrable document-intelligence application that answers questions about user-provided PDFs, retrieves relevant evidence, displays verifiable citations, communicates uncertainty, and supports evidence-backed comparison of selected documents.
- **Primary source of truth:** The original SourceIQ / ProofLens AI PRD and explicitly approved user decisions.
- **Development stage:** Documentation and planning must be completed and approved before implementation begins. Do not assume coding is authorized merely because a plan exists.

SourceIQ is an evidence-first document Q&A product. It is not a general-purpose web-search assistant, autonomous agent platform, or a system that can guarantee every generated statement is true.

Never describe the product as “eliminating hallucinations” or guaranteeing factual correctness. Prefer accurate wording such as “grounds answers in retrieved evidence, validates citation references, and abstains when evidence is insufficient.”

---

## 2. Rules of Authority and Decision Status

Use this order of authority:

1. Explicit decisions approved by the project owner.
2. The original PRD.
3. The latest approved TDD and Implementation Plan.
4. Existing implementation and repository conventions, where they do not conflict with the above.
5. Agent recommendations, which remain proposals until approved when they affect scope, architecture, providers, cost, security, or user-visible behavior.

When documenting or discussing a decision, label it accurately as one of:

- **Approved:** explicitly decided by the project owner.
- **PRD requirement:** required by the original PRD.
- **Proposed:** recommended but not yet approved.
- **Open decision:** information is not yet decided.
- **Verified:** confirmed by actual inspection or a test.
- **Unverified:** not yet confirmed.

Do not turn a proposal into an approved decision just because it appears in a generated document.

If the specification is silent about a consequential behavior, ask before implementing it. For a low-risk, reversible detail, choose the smallest reasonable default and disclose the assumption.

---

## 3. Non-Negotiable Project Workflow

### Before implementation

1. Inspect the repository, current branch, working tree, and existing files.
2. Read the original PRD, TDD, Implementation Plan, and relevant project notes.
3. Compare the requested task with the documented MVP scope and approved decisions.
4. Identify affected files, dependencies, risks, and validation steps.
5. State briefly what you intend to do before making changes.
6. If the task requires a new product decision, provider choice, paid service, scope expansion, destructive action, or incompatible contract change, ask for approval first.

### While working

- Make one focused, reviewable change at a time.
- Implement only the requested and approved scope.
- Preserve unrelated work and inspect existing diffs before editing.
- Do not replace a working architecture or refactor unrelated files for stylistic reasons.
- Do not introduce dependencies or infrastructure without a demonstrated need.
- Do not invent APIs, database fields, product behavior, or environment settings.
- Do not claim tests, builds, compatibility checks, or external service behavior were verified unless they were actually checked.

### After working

Report:
1. What changed and why.
2. Every file created, modified, or deleted.
3. Checks actually run and their results.
4. Checks not run and why.
5. Assumptions, remaining decisions, and issues noticed but deliberately left unchanged.

Use plain language suitable for a developer learning the stack.

---

## 4. SourceIQ MVP Boundary

### Features included in the MVP

Keep implementation aligned with the PRD. The MVP includes:

- Workspace and PDF document management.
- Text extraction from supported, text-based PDFs.
- Page-aware provenance throughout extraction, chunking, retrieval, citation, and evidence display.
- Configurable chunking and embeddings.
- PostgreSQL with pgvector for vector storage and semantic retrieval.
- Semantic retrieval scoped to the authorized workspace and, when requested, selected documents.
- Retrieval-augmented Q&A grounded in retrieved evidence.
- Citations that refer to actual stored documents and source pages.
- Evidence inspection that displays the cited source excerpt.
- Explicit uncertainty handling and abstention when evidence is insufficient.
- Standard user-requested comparison of at least two selected documents on a topic, with evidence-backed findings for each document.
- A curated evaluation dataset and repeatable evaluation command.

### Explicitly post-MVP

Do not implement these as MVP features:

- **Claim Verification Mode.**
- **Cross-Document Contradiction Finder:** automated corpus-wide contradiction discovery. This is distinct from a user explicitly asking to compare selected documents, which is an MVP feature.
- **Evidence-First Decision Brief.**

### Explicitly out of MVP unless approved

- AI agents or multi-agent orchestration.
- LangGraph.
- MCP.
- Graph RAG or Neo4j.
- Replacing PostgreSQL/pgvector with an external vector database.
- OCR for scanned PDFs.
- Web browsing as an evidence source.
- Microservices or Kubernetes.
- Redis, Celery, or another job-queue system without a demonstrated requirement.
- Unrequested analytics, admin features, integrations, or future-roadmap abstractions.

Do not build future features “in advance.” Keep the design maintainable without implementing post-MVP behavior.

---

## 5. Architecture and Stack

The documented architectural direction is a **modular monolith**:

- **Backend:** Python with FastAPI.
- **Frontend:** Next.js.
- **Database:** PostgreSQL with pgvector.
- **ORM / data access:** SQLAlchemy if retained by the approved TDD.
- **Database migrations:** Alembic if retained by the approved TDD.
- **PDF extraction:** PyMuPDF if retained by the approved TDD.
- **AI services:** an LLM provider and embedding provider, to be selected and verified before implementation if not already approved.

These are the current architectural direction, not permission to silently choose every provider, model, hosting platform, or dependency version.

Before implementing, inspect the repository and approved documents. Use their actual versions and commands. Do not invent a directory layout, dependency version, or run command when it can be discovered.

Prefer clear boundaries between:
- API/routes and request/response schemas.
- Application/service logic.
- Persistence and database models.
- PDF extraction and chunking.
- Embedding and LLM provider adapters.
- Retrieval and evidence/citation validation.
- Evaluation utilities.
- Frontend presentation and API communication.

Do not add a layer or abstraction unless it improves a real current requirement.

---

## 6. Local Development and Production

These environment rules are approved project decisions:

- **Local development uses a native local PostgreSQL installation.**
- **Do not use Docker for local development.**
- **Docker is for production deployment only.**
- Production is intended to use Supabase PostgreSQL, subject to verification of the required PostgreSQL/pgvector compatibility and configuration.
- Use database migrations for schema changes.
- Keep all secrets and environment-specific values outside source code.

Do not change these rules unless the project owner explicitly approves a change.

Do not assume the production hosting provider, object-storage provider, or final frontend/backend deployment topology is decided unless the approved documents say so.

### Localhost rule

Do not hardcode `localhost`, a machine-specific hostname, port, drive path, or production URL in application logic. Local development may legitimately use localhost through environment/configuration and documented local examples. Never use an absolute path tied to one developer’s machine.

---

## 7. Configuration and Secrets

Use one clearly defined configuration module per application/runtime. Application code should read settings through that module rather than accessing environment variables throughout the codebase.

- Validate required configuration at startup.
- Fail clearly when required settings are missing or invalid.
- Do not silently fall back to unsafe credentials or production-like defaults.
- Keep `.env` and other real local secret files out of version control.
- Maintain an example environment file with placeholders and comments for every required variable.
- Document new configuration variables in the same change that introduces them.
- Keep development and production configuration requirements distinct.
- Never commit real credentials, API keys, access tokens, passwords, signing secrets, or privileged service keys.
- Never expose database credentials or private AI provider keys in browser code or public frontend environment variables.
- Never log secrets, passwords, authorization headers, or authentication request bodies.
- Do not make paid/external API calls without the task requiring them and the necessary approval/configuration being available.

Use safe placeholders in examples, such as `replace-with-local-secret`; never use a real key or a default password that might be mistaken for a secure value.

---

## 8. Source Provenance Is a Core Product Requirement

Evidence provenance is not optional metadata. Preserve it from the original PDF through the final answer.

The pipeline must preserve enough reliable information to trace a displayed citation back to the source, including as applicable:

- Workspace and document identity.
- Original filename and stored document identity.
- Page number, with a consistent convention for zero-based versus one-based numbering.
- Chunk identity and chunk order.
- Extracted text and the source page associated with it.
- Embedding/model identity where needed for compatibility and reproducibility.
- Retrieval/query-run context when needed for evaluation or debugging.

Do not fabricate a page number, source excerpt, document identity, or citation.

If extraction cannot reliably associate text with a page, represent the limitation clearly rather than inventing provenance.

The frontend must display the source page and excerpt associated with the validated citation. Make page numbering understandable to users.

Document deletion and re-ingestion must not leave orphaned chunks, vectors, or citations that appear valid after the source document is gone.

---

## 9. RAG, Citations, and Abstention

Follow the approved retrieval flow and do not bypass evidence validation for convenience.

A typical flow is:

1. Validate the request and verify workspace/document access.
2. Retrieve only eligible chunks from the authorized scope.
3. Build the evidence context from retrieved chunks.
4. Ask the configured LLM to answer using that context.
5. Validate citation references and source excerpts on the server.
6. Return the answer with structured evidence and uncertainty information.
7. Display the answer and evidence transparently in the UI.

The exact request/response contracts must follow the approved API specification.

### Keep these checks distinct

1. **Citation-reference validity:** the cited document, page, and chunk exist and belong to the authorized scope.
2. **Quote validity:** the displayed excerpt corresponds to stored source text.
3. **Claim support:** the evidence actually supports the answer’s claim.

Passing the first or second check does not automatically prove the third.

- Never trust citation identifiers or excerpts generated by the LLM without server-side validation.
- Do not allow a model to invent a source or page.
- Do not describe model-generated conclusions as direct quotations.
- Clearly separate source evidence from interpretation.
- When evidence is absent, weak, conflicting, or outside the retrieved context, communicate the limitation and abstain where appropriate.
- Do not force an answer merely because the API call succeeded.
- Treat similarity thresholds and top-k values as configurable, empirically tuned settings—not universal constants.
- If pgvector’s cosine-distance operator is used, distinguish distance from similarity and document the chosen formula and threshold semantics.

A successful HTTP response is not proof that the answer is correct or supported.

---

## 10. Embeddings and Model Compatibility

Embedding configuration must be explicit and internally consistent.

Before implementation, verify or obtain approval for:
- Embedding provider and exact model.
- Output vector dimension.
- Supported input constraints and limits.
- LLM provider and exact model.
- Relevant rate limits, timeout behavior, and expected cost constraints.

A fixed-dimension pgvector column cannot store incompatible vector dimensions. Do not support arbitrary model switching unless the storage design explicitly supports it.

If an embedding model changes, document the consequences for:
- Stored vectors.
- Schema or index compatibility.
- Re-embedding existing chunks.
- Downtime or staged migration, if applicable.
- Evaluation comparability.

Do not assume a provider/model name, dimension, endpoint, or capability is valid without verification. If a provider decision remains open, preserve it as an open decision and do not hardcode a guessed choice.

---

## 11. Workspace Isolation and Security

Treat workspace isolation as a security boundary, not just a query filter.

- Verify access for every read, list, search, update, delete, and document-processing operation.
- Never trust a workspace ID, user ID, document ID, or ownership field supplied by the client without authorization checks.
- Do not treat a client-provided header such as a user ID or workspace key as authentication unless a real, approved authentication mechanism validates it.
- Make demo identity/context selection explicitly different from production authentication.
- Apply workspace scope to document metadata, chunks, vector retrieval, query history, evidence, and deletion paths as relevant.
- Test that a request from one workspace cannot retrieve or mutate another workspace’s data.
- Return safe responses for inaccessible resources without leaking their contents or existence.
- Validate file type, size, request fields, and other untrusted input at the boundary.
- Use parameterized database operations/ORM expressions; never concatenate untrusted input into SQL.
- Use explicit CORS origins from configuration. Do not use a wildcard as a shortcut for credentialed or production access.
- Return purpose-built response schemas, not raw ORM/database objects.
- Do not expose internal paths, stack traces, raw SQL, provider secrets, or private document data in errors/logs.

If authentication requirements remain unresolved, document the options and ask before claiming production-ready account security.

---

## 12. PDF Ingestion and File Handling

MVP ingestion is for supported, text-based PDFs unless the PRD is explicitly changed.

Handle, without crashing:
- Invalid or corrupted PDFs.
- Unsupported file types.
- Empty or near-empty extracted text.
- Scanned PDFs that require OCR.
- Files exceeding the configured size limit.
- Extraction failures and provider failures.
- Duplicate or repeated ingestion requests.
- Partial ingestion and interrupted processing.

Do not add OCR to the MVP without explicit approval.

- Keep file-size and ingestion limits in configuration.
- Validate uploaded content server-side; do not trust only a filename or browser-provided content type.
- Use safe storage names and paths; do not construct filesystem paths directly from untrusted filenames.
- Avoid retaining unnecessary temporary files.
- Ensure failed ingestion has a clear status and can be retried safely where supported.
- Avoid duplicate chunks/vectors when retrying the same ingestion operation.
- Keep long-running ingestion behavior appropriate for the MVP. Do not add a distributed queue unless current needs justify it.
- Define deletion behavior for source files, extracted text, chunks, vectors, and associated query/evidence records according to the approved data-retention decision.

---

## 13. Database and Migrations

- Every schema change must be represented by a migration.
- Do not rely on automatic schema creation/update as the production migration strategy.
- Never edit a migration that has already been applied in a shared or deployed environment; add a new migration instead.
- Use foreign keys, unique constraints, not-null constraints, and check constraints where they represent real data invariants.
- Use transactions when one operation changes multiple related records.
- Use timezone-aware timestamps and document the timestamp convention.
- Choose indexes based on actual queries and the pgvector retrieval design.
- Make workspace relationships and cascade/deletion behavior explicit.
- Avoid storing duplicate representations of data unless there is a clear reason.
- Do not manually modify the database to make the application appear to work.
- Do not run destructive migrations, reset databases, delete user data, or drop tables without explicit approval.
- Do not claim a migration was tested unless it was actually run against an appropriate database.

For vector indexes and query behavior, follow the approved PostgreSQL/pgvector compatibility plan. Verify actual database and extension versions before relying on version-specific features.

---

## 14. API Contracts and Error Handling

Define and review endpoint request/response schemas before implementing the endpoint.

- Follow the approved route naming, versioning, and API contracts.
- Do not invent fields or change response shapes without checking consumers and obtaining approval when the change is breaking.
- Use validated request and response models.
- Use consistent error response structures and meaningful HTTP status codes.
- Do not return raw framework errors or stack traces to users.
- Do not swallow exceptions or report success after a failed operation.
- Keep internal diagnostic details in safe server logs and return a clear, non-sensitive message to the client.
- Handle provider timeouts, rate limits, and temporary failures deliberately.
- Avoid unbounded retries and duplicate billable requests.
- Record relevant latency, status, and usage metrics when available, without logging private content or secrets.
- Do not add endpoints that are not required by the approved MVP.

The frontend and backend must use the same contract. If the contract is ambiguous, stop and clarify rather than guessing.

---

## 15. Frontend and User Experience

Inspect the existing design system and components before creating new ones.

- Keep presentation separate from API calls and data-fetching logic.
- Route all backend requests through a shared API client where the existing architecture supports it.
- Keep the backend base URL in configuration.
- Reuse existing components and design tokens.
- Do not invent a new visual theme or replace the existing design without approval.
- Avoid hardcoded API URLs, environment-specific values, duplicated status lists, and repeated UI logic.
- Do not place secrets in frontend configuration.
- Handle loading, empty, error, and successful states for each relevant view.
- Empty states should explain the next useful action.
- Display citations and evidence clearly; users must be able to inspect the referenced document/page/excerpt.
- Distinguish an answer, a direct source excerpt, and an interpretation.
- Communicate unsupported questions, missing evidence, extraction failures, and comparison limitations honestly.
- Handle long filenames, empty workspaces, missing pages, large excerpts, and partial results without breaking the layout.
- Make interactive elements accessible, keyboard-usable, and clear about their current state.
- Do not add decorative UI that misrepresents evidence quality or model certainty.

Do not enforce a generic “no inline styles” rule blindly if the existing approved design system uses a different approach; follow the repository’s established styling conventions and documented design tokens.

---

## 16. Multi-Document Comparison

The MVP comparison feature is initiated by the user for selected documents and a specific topic.

- Include findings per selected document.
- Ground each material finding in evidence and citations.
- Distinguish agreement, difference, and contradiction only when the cited evidence supports the distinction.
- Flag incompatible definitions, time periods, scopes, or assumptions when they affect the comparison.
- Do not manufacture a disagreement simply because wording differs.
- Do not claim documents contradict each other if they address different contexts or populations.
- Clearly state when a selected document contains insufficient evidence for the requested topic.
- Do not silently search the entire workspace when the user selected a narrower document scope.
- Do not turn this feature into automated workspace-wide contradiction discovery; that remains post-MVP.

---

## 17. Evaluation and Quality

Evaluation is an MVP responsibility, not optional polish.

Maintain a small, version-controlled benchmark with representative questions and expected evidence/behavior. Keep private secrets and sensitive source material out of the repository.

Where appropriate, evaluate:
- Retrieval hit rate/recall against expected evidence.
- Citation-reference validity.
- Quote/source matching.
- Evidence support for answer claims.
- Correct abstention on unsupported questions.
- Comparison behavior on agreement, differences, incompatible scopes, and insufficient evidence.
- Error handling for invalid, empty, and failed documents.
- Workspace isolation.

Rules:
- Clearly distinguish deterministic checks from model-judged evaluations.
- Label LLM-judged metrics as model-based and acknowledge their limitations.
- Do not present a model judge as ground truth.
- Do not claim an accuracy percentage or performance target is achieved until measured.
- Treat initial targets as goals to validate, not guarantees.
- Keep evaluation repeatable with documented commands and reproducible configuration.
- Do not change a benchmark expectation merely to make a failing implementation pass. Investigate whether the implementation or expectation is wrong and explain the result.
- Do not report tests or evaluation commands as run if they were not run.

---

## 18. Configuration Values and Hardcoding

Values that vary by environment, affect behavior, or are reused should be centralized in configuration/constants rather than scattered through application code.

Examples include:
- API base URL, host, and port.
- Database connection details.
- Provider names and model identifiers.
- Secrets and API keys.
- Upload and extraction limits.
- Chunk size and overlap.
- Embedding batch size.
- Retrieval top-k and threshold.
- Timeouts, retry limits, and concurrency.
- Allowed frontend origins.
- Feature flags, if approved and actually needed.

Do not centralize every harmless literal just for the sake of abstraction. Use judgment, follow existing conventions, and keep changes proportionate.

Never commit real `.env` files. Ensure example values are clearly placeholders. Do not add a new configuration switch without a real requirement.

---

## 19. Testing and Verification

Write or update tests alongside the behavior they cover.

Prioritize:
- Unit tests for chunking, provenance, retrieval logic, and citation validation.
- API tests for validation, status/error responses, and document lifecycle.
- Integration tests for database queries, pgvector behavior, and migrations where the environment permits.
- Evaluation tests for supported and unsupported questions.
- Security tests proving workspace isolation.
- Frontend tests for loading, empty, error, evidence, and citation display states where a test framework exists.

Use the test and lint tools already configured in the repository. Do not install another framework without justification.

- Never modify tests merely to make broken code appear to pass.
- Distinguish a failed test from an unavailable dependency/service.
- Do not claim full coverage unless measured.
- Report exact commands run and summarize actual outcomes.
- If tests cannot be run because a database, provider key, or external service is unavailable, state that limitation clearly.

---

## 20. Git, Files, and Destructive Actions

- Inspect the current working tree before editing.
- Preserve the user's uncommitted changes.
- Do not reset, clean, stash, checkout over, or discard user changes without explicit permission.
- Do not commit, push, create a release, or deploy unless explicitly requested.
- Do not delete documents, data, migrations, or project files without approval.
- Do not modify unrelated files or perform broad formatting/refactoring as a side effect.
- Do not write machine-specific absolute paths into committed code or docs.
- Do not leave placeholder implementations or TODOs while claiming the feature is complete.
- If the task is too broad for one reviewable change, propose smaller steps.

---

## 21. Deployment Readiness

Do not equate “works on my machine” with production readiness.

Before changing deployment-related code, consider:
- Platform-provided port and host binding.
- Environment-driven allowed origins.
- Managed database TLS/encryption requirements.
- Database migration execution and rollback/recovery plan.
- Temporary versus persistent file storage.
- Provider timeouts, quotas, and secrets.
- Startup configuration validation.
- Logging without sensitive content.
- Health/readiness behavior if required by the chosen deployment platform.
- Whether the selected PostgreSQL/pgvector features are supported in production.

Docker is production-only for this project. Do not require a local Docker workflow.

Do not deploy or create external resources as part of an ordinary code task without explicit authorization.

---

## 22. Open Decisions Must Stay Open

The following areas must remain open until the PRD or project owner resolves them. Check the latest project documents before assuming any has been decided:

- LLM provider and exact model.
- Embedding provider, exact model, and vector dimension.
- Authentication approach for the college/demo use case and whether persistent user accounts are required.
- Final upload-size and ingestion limits.
- Whether scanned PDFs are rejected with a clear explanation in the MVP.
- Production hosting topology.
- File/object storage strategy.
- Provider budget, rate limits, and usage constraints.
- Any other item explicitly marked unresolved in the current PRD/TDD.

For each consequential open decision, state the question, why it matters, a concise recommendation, and whether it blocks the next step. Do not silently select a paid service or make a product decision.

---

## 23. Response Format for Antigravity

Before changes, give one concise sentence describing the intended task.

After changes, report:

1. **Summary:** What changed and why.
2. **Files changed:** Each created/modified/deleted file and its purpose.
3. **Validation:** Commands/checks actually run and their results.
4. **Not validated:** Anything not run and why.
5. **Assumptions/open decisions:** Explicitly list any remaining.
6. **Out of scope:** Relevant issues noticed but deliberately not changed.

Keep explanations direct, clear, and beginner-friendly. Do not claim something works unless it was verified.

---

## 24. Final Checklist

Before calling any task complete, verify:

### Scope
- [ ] The change matches the request and approved PRD.
- [ ] No post-MVP feature was added.
- [ ] No unrelated refactor or formatting was included.
- [ ] Existing user changes were preserved.

### Security and data
- [ ] Workspace access is verified on every relevant operation.
- [ ] Client-supplied IDs/headers are not mistaken for authentication.
- [ ] Inputs and uploaded files are validated.
- [ ] No secret is committed, logged, or exposed to the browser.
- [ ] Source provenance and citation references remain accurate.
- [ ] Document deletion/retry behavior does not leave misleading orphan data.

### Configuration and database
- [ ] Environment-specific values are configuration-driven.
- [ ] Example configuration uses safe placeholders.
- [ ] Schema changes have migrations.
- [ ] Vector dimensions and retrieval metric semantics are consistent.
- [ ] No destructive database action occurred without approval.
- [ ] Local development remains native PostgreSQL; Docker remains production-only.

### Product behavior
- [ ] Insufficient evidence leads to an honest limitation/abstention.
- [ ] Source evidence is distinguishable from interpretation.
- [ ] Standard selected-document comparison remains in MVP.
- [ ] Automated contradiction discovery remains post-MVP.
- [ ] UI handles loading, empty, error, and content states where relevant.

### Verification and report
- [ ] Relevant tests/evaluation were run where possible.
- [ ] Unrun checks are explicitly disclosed.
- [ ] No unmeasured accuracy/performance claim is presented as fact.
- [ ] Files changed and reasons are reported clearly.

---

## 25. When Unsure or Blocked

Stop and ask when:
- The PRD, TDD, and Implementation Plan conflict.
- A behavior or API contract is unspecified and consequential.
- A provider/model or paid service needs to be selected.
- A change expands MVP scope.
- Workspace security or data deletion behavior is ambiguous.
- A migration may be destructive or incompatible.
- The task would overwrite or discard user work.
- The same approach has failed repeatedly.

Do not hide uncertainty behind a confident guess. Report the actual blocker and the smallest decision needed to proceed.

**Final rule: SourceIQ must remain evidence-first, scope-controlled, secure by design, honest about uncertainty, and verifiable through tests. Documentation or implementation that violates those principles is not complete.**
