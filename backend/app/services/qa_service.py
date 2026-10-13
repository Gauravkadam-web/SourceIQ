import re
import time
import uuid
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.core.errors import EntityNotFoundError, ProviderError
from app.core.logging import logger
from app.db.models.workspace import Workspace
from app.db.models.document import Document
from app.db.models.chunk import DocumentChunk
from app.db.models.query_audit import QueryRun, CitationLog
from app.providers.factory import get_llm_provider
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService, RetrievedChunk
from app.schemas.qa import QueryRequest, QueryResponse, CitationDetail, EvidenceInspectionResponse


class LLMCitation(BaseModel):
    citation_key: str = Field(description="The citation key, e.g. CIT-1")
    claim: str = Field(description="The specific claim made in the answer")
    quoted_snippet: str = Field(description="Exact snippet quoted from the evidence chunk")


class LLMAnswerOutput(BaseModel):
    answer: str = Field(description="Comprehensive answer citing facts with [CIT-X] tags")
    status: str = Field(default="GROUNDED", description="GROUNDED or INSUFFICIENT_EVIDENCE")
    citations: List[LLMCitation] = Field(default_factory=list)


class QAService:
    @classmethod
    async def answer_query(
        cls,
        db: Session,
        workspace_id: uuid.UUID,
        request: QueryRequest,
    ) -> QueryResponse:
        start_time = time.perf_counter()

        # 1. Workspace validation
        workspace = db.get(Workspace, workspace_id)
        if not workspace:
            raise EntityNotFoundError(f"Workspace with ID '{workspace_id}' was not found.")

        # 2. Scope validation (if document_ids specified)
        if request.document_ids:
            for doc_id in request.document_ids:
                doc = db.get(Document, doc_id)
                if not doc or doc.workspace_id != workspace_id:
                    raise EntityNotFoundError(f"Document '{doc_id}' not found in workspace.")

        # 3. Query embedding
        query_vector = await EmbeddingService.generate_query_embedding(request.question)

        # 4. Semantic retrieval
        retrieved_chunks = RetrievalService.retrieve_relevant_chunks(
            db=db,
            workspace_id=workspace_id,
            query_vector=query_vector,
            document_ids=request.document_ids,
            top_k=request.top_k or 5,
        )

        # 5. Abstention if insufficient evidence
        if not retrieved_chunks:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            abstain_answer = "I could not find sufficient evidence in the uploaded documents to answer your question."
            
            query_run = QueryRun(
                workspace_id=workspace_id,
                question=request.question,
                answer=abstain_answer,
                status="INSUFFICIENT_EVIDENCE",
                latency_ms=latency_ms,
            )
            db.add(query_run)
            db.commit()
            db.refresh(query_run)

            return QueryResponse(
                query_id=query_run.id,
                question=request.question,
                answer=abstain_answer,
                status="INSUFFICIENT_EVIDENCE",
                latency_ms=latency_ms,
                citations=[],
            )

        # 6. Evidence context assembly
        evidence_xml, chunk_map = cls._build_evidence_context(retrieved_chunks)

        system_instruction = (
            "You are SourceIQ, a high-precision document intelligence assistant.\n"
            "Your task is to answer the user's question STRICTLY based on the provided evidence excerpts.\n"
            "Rules you must obey without exception:\n"
            "1. Only state facts directly supported by the text in <document_evidence>.\n"
            "2. For every factual claim, you MUST append citation tags like [CIT-1], [CIT-2] matching the chunk IDs.\n"
            "3. If the evidence does not contain enough information to answer completely, explicitly state what is missing and set status to 'INSUFFICIENT_EVIDENCE'.\n"
            "4. Never fabricate citations, page numbers, or claims not found in the evidence.\n"
            "5. Provide exact quoted snippets for each cited claim in the structured output."
        )

        user_prompt = f"<document_evidence>\n{evidence_xml}\n</document_evidence>\n\nUser Question: {request.question}"

        # 7. LLM Generation
        provider = get_llm_provider()
        llm_raw = await provider.generate_grounded_answer(
            system_instruction=system_instruction,
            user_prompt=user_prompt,
            response_schema=LLMAnswerOutput,
        )

        try:
            llm_result = LLMAnswerOutput.model_validate(llm_raw)
        except Exception:
            # Fallback if raw dict has 'answer'
            answer_text = llm_raw.get("answer", "")
            llm_result = LLMAnswerOutput(
                answer=answer_text,
                status="GROUNDED" if "[CIT-" in answer_text else "INSUFFICIENT_EVIDENCE",
                citations=[],
            )

        # 8. Server-Side Citation Validation
        validated_citations, is_all_valid = cls._validate_citations(llm_result.citations, chunk_map)

        final_status = llm_result.status
        if not is_all_valid:
            final_status = "CITATION_FAILED"
        elif not validated_citations and "[CIT-" in llm_result.answer:
            final_status = "CITATION_FAILED"
        elif not validated_citations and final_status == "GROUNDED":
            final_status = "INSUFFICIENT_EVIDENCE"

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 9. Record QueryRun and CitationLogs
        query_run = QueryRun(
            workspace_id=workspace_id,
            question=request.question,
            answer=llm_result.answer,
            status=final_status,
            latency_ms=latency_ms,
        )
        db.add(query_run)
        db.flush()

        db_citation_logs = []
        for cit in validated_citations:
            db_citation_logs.append(
                CitationLog(
                    query_run_id=query_run.id,
                    chunk_id=cit.chunk_id,
                    claim_snippet=cit.claim or cit.quoted_snippet,
                    similarity_score=cit.similarity_score,
                    is_valid=True,
                )
            )
        if db_citation_logs:
            db.add_all(db_citation_logs)

        db.commit()
        db.refresh(query_run)

        return QueryResponse(
            query_id=query_run.id,
            question=request.question,
            answer=llm_result.answer,
            status=final_status,
            latency_ms=latency_ms,
            citations=validated_citations,
        )

    @staticmethod
    def _build_evidence_context(chunks: List[RetrievedChunk]) -> Tuple[str, Dict[str, RetrievedChunk]]:
        xml_parts = []
        chunk_map: Dict[str, RetrievedChunk] = {}
        for idx, chunk in enumerate(chunks, start=1):
            key = f"CIT-{idx}"
            chunk_map[key] = chunk
            xml_parts.append(
                f'<chunk id="{key}" document="{chunk.document_name}" page="{chunk.page_number}">\n'
                f"{chunk.content}\n"
                f"</chunk>"
            )
        return "\n".join(xml_parts), chunk_map

    @staticmethod
    def _validate_citations(
        raw_citations: List[LLMCitation],
        chunk_map: Dict[str, RetrievedChunk],
    ) -> Tuple[List[CitationDetail], bool]:
        validated: List[CitationDetail] = []
        all_valid = True

        for raw_cit in raw_citations:
            clean_key = raw_cit.citation_key.strip().strip("[]")
            if clean_key not in chunk_map:
                # Key hallucinated or fabricated by LLM
                all_valid = False
                continue

            chunk = chunk_map[clean_key]
            # Quote verification: check if quoted snippet appears in chunk content
            quoted = raw_cit.quoted_snippet.strip()
            if quoted and quoted.lower() in chunk.content.lower():
                actual_quote = quoted
            else:
                # Fallback to chunk passage prefix if snippet was slightly paraphrased
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

    @classmethod
    def get_evidence(cls, db: Session, chunk_id: uuid.UUID) -> EvidenceInspectionResponse:
        """Retrieves targeted chunk text along with surrounding context from the document."""
        chunk = db.get(DocumentChunk, chunk_id)
        if not chunk:
            raise EntityNotFoundError(f"Evidence chunk with ID '{chunk_id}' was not found.")

        doc = db.get(Document, chunk.document_id)
        doc_name = doc.filename if doc else "document.pdf"

        # Fetch adjacent chunks in the same document
        prev_chunk = (
            db.execute(
                select(DocumentChunk)
                .filter(
                    DocumentChunk.document_id == chunk.document_id,
                    DocumentChunk.chunk_index == chunk.chunk_index - 1,
                )
            )
            .scalars()
            .first()
        )

        next_chunk = (
            db.execute(
                select(DocumentChunk)
                .filter(
                    DocumentChunk.document_id == chunk.document_id,
                    DocumentChunk.chunk_index == chunk.chunk_index + 1,
                )
            )
            .scalars()
            .first()
        )

        surrounding_parts = []
        if prev_chunk:
            surrounding_parts.append(f"...{prev_chunk.content[-200:]}")
        surrounding_parts.append(f"[{chunk.content}]")
        if next_chunk:
            surrounding_parts.append(f"{next_chunk.content[:200]}...")

        surrounding_context = "\n\n".join(surrounding_parts)

        return EvidenceInspectionResponse(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            document_name=doc_name,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            surrounding_context=surrounding_context,
        )
