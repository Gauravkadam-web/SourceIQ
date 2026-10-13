import time
import uuid
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.errors import EntityNotFoundError, BadRequestError
from app.core.logging import logger
from app.db.models.workspace import Workspace
from app.db.models.document import Document
from app.db.models.query_audit import QueryRun
from app.providers.factory import get_llm_provider
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService, RetrievedChunk
from app.services.qa_service import LLMCitation
from app.schemas.qa import CitationDetail
from app.schemas.comparison import ComparisonRequest, ComparisonResponse, DocumentFinding


class LLMDocFinding(BaseModel):
    document_id: str = Field(description="Document UUID")
    has_sufficient_evidence: bool = Field(description="Whether the document contains evidence for the topic")
    summary: str = Field(description="Finding summary with citation tags like [DOC1-CIT-1]")
    citations: List[LLMCitation] = Field(default_factory=list)


class LLMComparisonOutput(BaseModel):
    synthesis: str = Field(description="Synthesis comparing the findings across documents")
    relationship: str = Field(description="AGREEMENT, DIFFERENCE, CONTRADICTION, DIFFERENT_SCOPES, or INSUFFICIENT_EVIDENCE")
    scope_notes: Optional[str] = Field(default=None, description="Notes on incompatible definitions, timeframes, or methodologies")
    findings: List[LLMDocFinding] = Field(default_factory=list)


class ComparisonService:
    @classmethod
    async def compare_documents(
        cls,
        db: Session,
        workspace_id: uuid.UUID,
        request: ComparisonRequest,
    ) -> ComparisonResponse:
        start_time = time.perf_counter()

        # 1. Validate workspace
        workspace = db.get(Workspace, workspace_id)
        if not workspace:
            raise EntityNotFoundError(f"Workspace with ID '{workspace_id}' was not found.")

        # 2. Validate at least two unique documents
        unique_doc_ids = list(dict.fromkeys(request.document_ids))
        if len(unique_doc_ids) < 2:
            raise BadRequestError("Comparison requires at least two distinct documents.")

        # 3. Validate documents belong to workspace and are READY
        docs: List[Document] = []
        for doc_id in unique_doc_ids:
            doc = db.get(Document, doc_id)
            if not doc or doc.workspace_id != workspace_id:
                raise EntityNotFoundError(f"Document '{doc_id}' not found in workspace.")
            if doc.status != "READY":
                raise BadRequestError(f"Document '{doc.filename}' is not ready for querying (status: {doc.status}).")
            docs.append(doc)

        # 4. Generate topic embedding
        query_vector = await EmbeddingService.generate_query_embedding(request.topic)

        # 5. Retrieve chunks per document
        doc_chunks_map: Dict[uuid.UUID, List[RetrievedChunk]] = {}
        total_retrieved = 0

        for doc in docs:
            chunks = RetrievalService.retrieve_relevant_chunks(
                db=db,
                workspace_id=workspace_id,
                query_vector=query_vector,
                document_ids=[doc.id],
                top_k=request.top_k_per_document or 3,
            )
            doc_chunks_map[doc.id] = chunks
            total_retrieved += len(chunks)

        comparison_id = uuid.uuid4()

        # 6. Check if zero evidence found across all documents
        if total_retrieved == 0:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            findings = [
                DocumentFinding(
                    document_id=doc.id,
                    document_name=doc.filename,
                    has_sufficient_evidence=False,
                    summary="No relevant evidence found in this document for the requested topic.",
                    citations=[],
                )
                for doc in docs
            ]
            
            # Record audit run
            query_run = QueryRun(
                id=comparison_id,
                workspace_id=workspace_id,
                question=f"[COMPARE] {request.topic}",
                answer="Insufficient evidence across all selected documents.",
                status="INSUFFICIENT_EVIDENCE",
                latency_ms=latency_ms,
            )
            db.add(query_run)
            db.commit()

            return ComparisonResponse(
                comparison_id=comparison_id,
                workspace_id=workspace_id,
                topic=request.topic,
                status="INSUFFICIENT_EVIDENCE",
                relationship="INSUFFICIENT_EVIDENCE",
                synthesis="None of the selected documents contain sufficient evidence to evaluate this topic.",
                scope_notes=None,
                document_findings=findings,
                latency_ms=latency_ms,
            )

        # 7. Build XML context and global chunk map
        evidence_xml, chunk_map = cls._build_comparison_context(docs, doc_chunks_map)

        system_instruction = (
            "You are SourceIQ's Cross-Document Comparison Engine.\n"
            "Analyze the user's topic across the provided documents strictly from the text in <multi_document_comparison>.\n"
            "Rules you must strictly follow:\n"
            "1. Produce findings for EACH document individually. Ground every claim using citation tags like [DOC1-CIT-1].\n"
            "2. If a document has no evidence for the topic, set has_sufficient_evidence=false and state that clearly.\n"
            "3. Synthesize the comparison and assign a relationship category:\n"
            "   - 'AGREEMENT': Documents agree on key factual points on the same scope.\n"
            "   - 'DIFFERENCE': Documents present different perspectives or details without conflicting facts.\n"
            "   - 'CONTRADICTION': Documents make directly opposing factual claims on the exact same metric/scope.\n"
            "   - 'DIFFERENT_SCOPES': Documents address different years, locations, or definitions (explain in scope_notes).\n"
            "   - 'INSUFFICIENT_EVIDENCE': Evidence is too sparse to evaluate.\n"
            "4. Never manufacture contradictions simply due to differing wording or different contexts.\n"
            "5. Provide exact quoted snippets for each citation."
        )

        user_prompt = (
            f"<multi_document_comparison>\n{evidence_xml}\n</multi_document_comparison>\n\n"
            f"Comparison Topic: {request.topic}"
        )

        # 8. Call LLM provider
        provider = get_llm_provider()
        llm_raw = await provider.generate_grounded_answer(
            system_instruction=system_instruction,
            user_prompt=user_prompt,
            response_schema=LLMComparisonOutput,
        )

        try:
            llm_result = LLMComparisonOutput.model_validate(llm_raw)
        except Exception:
            # Fallback
            synthesis_text = llm_raw.get("synthesis", "Comparison evaluation completed.")
            llm_result = LLMComparisonOutput(
                synthesis=synthesis_text,
                relationship="DIFFERENCE",
                scope_notes=None,
                findings=[],
            )

        # 9. Server-side validation of findings and citations
        validated_findings: List[DocumentFinding] = []
        raw_findings_map = {f.document_id: f for f in llm_result.findings}

        for idx, doc in enumerate(docs, start=1):
            doc_id_str = str(doc.id)
            doc_chunks = doc_chunks_map.get(doc.id, [])
            raw_f = raw_findings_map.get(doc_id_str)

            if not doc_chunks:
                # No chunks retrieved for this document
                validated_findings.append(
                    DocumentFinding(
                        document_id=doc.id,
                        document_name=doc.filename,
                        has_sufficient_evidence=False,
                        summary="This document does not contain relevant evidence for the requested topic.",
                        citations=[],
                    )
                )
            elif raw_f:
                # Validate citations for this document
                val_cits, _ = cls._validate_doc_citations(raw_f.citations, chunk_map, doc.id)
                validated_findings.append(
                    DocumentFinding(
                        document_id=doc.id,
                        document_name=doc.filename,
                        has_sufficient_evidence=raw_f.has_sufficient_evidence and (len(val_cits) > 0 or len(doc_chunks) > 0),
                        summary=raw_f.summary,
                        citations=val_cits,
                    )
                )
            else:
                # LLM didn't return finding for doc; construct standard summary from retrieved chunks
                sample_chunk = doc_chunks[0]
                cit = CitationDetail(
                    citation_key=f"DOC{idx}-CIT-1",
                    chunk_id=sample_chunk.chunk_id,
                    document_id=doc.id,
                    document_name=doc.filename,
                    page_number=sample_chunk.page_number,
                    similarity_score=sample_chunk.similarity_score,
                    quoted_snippet=sample_chunk.content[:150],
                    claim=f"Relevant passage from {doc.filename}",
                )
                validated_findings.append(
                    DocumentFinding(
                        document_id=doc.id,
                        document_name=doc.filename,
                        has_sufficient_evidence=True,
                        summary=f"Evidence retrieved from page {sample_chunk.page_number}.",
                        citations=[cit],
                    )
                )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 10. Audit logging
        query_run = QueryRun(
            id=comparison_id,
            workspace_id=workspace_id,
            question=f"[COMPARE] {request.topic}",
            answer=llm_result.synthesis,
            status="COMPLETED",
            latency_ms=latency_ms,
        )
        db.add(query_run)
        db.commit()

        return ComparisonResponse(
            comparison_id=comparison_id,
            workspace_id=workspace_id,
            topic=request.topic,
            status="COMPLETED",
            relationship=llm_result.relationship,
            synthesis=llm_result.synthesis,
            scope_notes=llm_result.scope_notes,
            document_findings=validated_findings,
            latency_ms=latency_ms,
        )

    @staticmethod
    def _build_comparison_context(
        docs: List[Document],
        doc_chunks_map: Dict[uuid.UUID, List[RetrievedChunk]],
    ) -> Tuple[str, Dict[str, RetrievedChunk]]:
        xml_parts = []
        chunk_map: Dict[str, RetrievedChunk] = {}

        for doc_idx, doc in enumerate(docs, start=1):
            chunks = doc_chunks_map.get(doc.id, [])
            xml_parts.append(f'<document id="{doc.id}" index="{doc_idx}" name="{doc.filename}">')
            if not chunks:
                xml_parts.append("  <no_evidence>No relevant passages found in this document.</no_evidence>")
            else:
                for chunk_idx, chunk in enumerate(chunks, start=1):
                    key = f"DOC{doc_idx}-CIT-{chunk_idx}"
                    chunk_map[key] = chunk
                    xml_parts.append(
                        f'  <chunk id="{key}" page="{chunk.page_number}">\n'
                        f"    {chunk.content}\n"
                        f"  </chunk>"
                    )
            xml_parts.append("</document>")

        return "\n".join(xml_parts), chunk_map

    @staticmethod
    def _validate_doc_citations(
        raw_citations: List[LLMCitation],
        chunk_map: Dict[str, RetrievedChunk],
        expected_doc_id: uuid.UUID,
    ) -> Tuple[List[CitationDetail], bool]:
        validated: List[CitationDetail] = []
        all_valid = True

        for raw_cit in raw_citations:
            clean_key = raw_cit.citation_key.strip().strip("[]")
            if clean_key not in chunk_map:
                all_valid = False
                continue

            chunk = chunk_map[clean_key]
            # Ensure citation actually belongs to this document
            if chunk.document_id != expected_doc_id:
                all_valid = False
                continue

            quoted = raw_cit.quoted_snippet.strip()
            if quoted and quoted.lower() in chunk.content.lower():
                actual_quote = quoted
            else:
                actual_quote = chunk.content[:150] + "..." if len(chunk.content) > 150 else chunk.content

            validated.append(
                CitationDetail(
                    citation_key=clean_key,
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    document_name=chunk.document_name,
                    page_number=chunk.page_number,
                    similarity_score=chunk.similarity_score,
                    quoted_snippet=actual_quote,
                    claim=raw_cit.claim,
                )
            )

        return validated, all_valid
