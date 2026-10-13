import uuid
from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.core.logging import logger
from app.db.models.chunk import DocumentChunk
from app.db.models.document import Document


@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    page_number: int
    chunk_index: int
    content: str
    similarity_score: float
    distance: float


class RetrievalService:
    @classmethod
    def retrieve_relevant_chunks(
        cls,
        db: Session,
        workspace_id: uuid.UUID,
        query_vector: List[float],
        document_ids: Optional[List[uuid.UUID]] = None,
        top_k: int = 5,
        similarity_threshold: Optional[float] = None,
    ) -> List[RetrievedChunk]:
        """
        Executes pgvector cosine similarity search (<=> operator) strictly isolated to the authorized workspace.
        Only chunks from READY documents are eligible.
        """
        if similarity_threshold is None:
            similarity_threshold = settings.SIMILARITY_THRESHOLD

        cosine_dist = DocumentChunk.embedding.cosine_distance(query_vector)

        stmt = (
            select(
                DocumentChunk,
                Document.filename.label("document_name"),
                cosine_dist.label("distance"),
            )
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(
                DocumentChunk.workspace_id == workspace_id,
                Document.status == "READY",
            )
        )

        # Optional document-level filtering
        if document_ids:
            stmt = stmt.filter(DocumentChunk.document_id.in_(document_ids))

        # Order by distance ascending (closest vectors first) and take top_k candidates
        stmt = stmt.order_by(cosine_dist.asc()).limit(top_k)

        results = db.execute(stmt).all()

        retrieved: List[RetrievedChunk] = []
        for row in results:
            chunk: DocumentChunk = row[0]
            doc_name: str = row[1]
            dist: float = float(row[2])
            # Cosine distance ranges from 0 (identical) to 2 (opposite); cosine similarity = 1 - distance
            similarity = round(max(0.0, 1.0 - dist), 4)

            # Filter out chunks falling below similarity threshold
            if similarity >= similarity_threshold:
                retrieved.append(
                    RetrievedChunk(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        document_name=doc_name,
                        page_number=chunk.page_number,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        similarity_score=similarity,
                        distance=round(dist, 4),
                    )
                )

        logger.info(
            f"Retrieved {len(retrieved)} chunks for workspace {workspace_id} "
            f"(candidates evaluated: {len(results)}, threshold: {similarity_threshold})"
        )
        return retrieved
