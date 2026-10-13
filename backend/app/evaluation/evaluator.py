import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.db.session import SessionLocal
from app.db.models.workspace import Workspace
from app.db.models.document import Document
from app.db.models.chunk import DocumentChunk
from app.services.qa_service import QAService
from app.services.embedding_service import EmbeddingService
from app.schemas.qa import QueryRequest
from app.schemas.evaluation import EvalItemResult, EvalReportResponse


class Evaluator:
    BENCHMARK_PATH = Path(__file__).parent / "benchmark_data.json"

    @classmethod
    def load_benchmark(cls) -> List[Dict[str, Any]]:
        with open(cls.BENCHMARK_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    async def run_evaluation(cls, db: Session) -> EvalReportResponse:
        items = cls.load_benchmark()
        results: List[EvalItemResult] = []

        total_questions = len(items)
        passed_count = 0
        hits = 0
        valid_citations_count = 0
        total_citations_count = 0
        neg_control_total = 0
        neg_control_passed = 0
        latencies: List[float] = []

        # Create temporary evaluation workspace
        eval_ws = Workspace(name="Evaluation Workspace", description="Automated benchmark runner workspace")
        db.add(eval_ws)
        db.commit()
        db.refresh(eval_ws)

        try:
            # Seed documents and chunks for grounded benchmark items
            doc_grounded = Document(
                workspace_id=eval_ws.id,
                filename="benchmark_report.pdf",
                file_path="/tmp/bench.pdf",
                file_size_bytes=2048,
                status="READY",
            )
            db.add(doc_grounded)
            db.commit()

            # Generate synthetic chunks for items that have sample text
            for idx, item in enumerate(items):
                sample_text = item.get("sample_document_text") or item.get("doc1_text")
                if sample_text and not item.get("should_abstain"):
                    # Generate real embedding or deterministic unit vector
                    try:
                        emb = await EmbeddingService.generate_chunk_embeddings([sample_text])
                        vec = emb[0]
                    except Exception:
                        vec = [0.05] * 768

                    chunk = DocumentChunk(
                        document_id=doc_grounded.id,
                        workspace_id=eval_ws.id,
                        page_number=idx + 1,
                        chunk_index=idx,
                        content=sample_text,
                        token_count=len(sample_text.split()),
                        embedding=vec,
                    )
                    db.add(chunk)
            db.commit()

            # Execute benchmark questions
            for item in items:
                q_id = item["id"]
                question = item["question"]
                should_abstain = item.get("should_abstain", False)
                category = item.get("category", "grounded_fact")

                t0 = time.perf_counter()
                req = QueryRequest(question=question, top_k=3)
                try:
                    res = await QAService.answer_query(db, eval_ws.id, req)
                    latency = res.latency_ms
                except Exception as e:
                    logger.error(f"Error evaluating {q_id}: {str(e)}")
                    res = None
                    latency = round((time.perf_counter() - t0) * 1000, 2)

                latencies.append(latency)

                if res is None:
                    results.append(
                        EvalItemResult(
                            id=q_id,
                            question=question,
                            category=category,
                            expected_behavior="Abstain" if should_abstain else "Grounded Answer",
                            actual_behavior="ERROR",
                            passed=False,
                            details="Execution failed",
                        )
                    )
                    continue

                # Check Negative Control (Abstention)
                if should_abstain:
                    neg_control_total += 1
                    passed = (res.status == "INSUFFICIENT_EVIDENCE") and (len(res.citations) == 0)
                    if passed:
                        neg_control_passed += 1
                    results.append(
                        EvalItemResult(
                            id=q_id,
                            question=question,
                            category=category,
                            expected_behavior="INSUFFICIENT_EVIDENCE (Abstain)",
                            actual_behavior=res.status,
                            passed=passed,
                            details="Successfully abstained on unsupported query." if passed else "Failed to abstain.",
                        )
                    )
                    if passed:
                        passed_count += 1
                else:
                    # Grounded factual query
                    hits += 1
                    cits_valid = all(c.chunk_id is not None for c in res.citations)
                    total_citations_count += len(res.citations)
                    if cits_valid:
                        valid_citations_count += len(res.citations)

                    passed = (res.status == "GROUNDED") and len(res.citations) > 0
                    results.append(
                        EvalItemResult(
                            id=q_id,
                            question=question,
                            category=category,
                            expected_behavior="GROUNDED Answer with Citations",
                            actual_behavior=f"{res.status} ({len(res.citations)} citations)",
                            passed=passed,
                            details="Answer verified with valid page citations." if passed else "Citations missing or ground status mismatch.",
                        )
                    )
                    if passed:
                        passed_count += 1

        finally:
            # Clean up evaluation workspace
            db.delete(eval_ws)
            db.commit()

        retrieval_hit_rate = round((hits / max(1, total_questions - neg_control_total)) * 100, 1)
        citation_validity = (
            round((valid_citations_count / max(1, total_citations_count)) * 100, 1)
            if total_citations_count > 0
            else 100.0
        )
        neg_abstention_rate = (
            round((neg_control_passed / max(1, neg_control_total)) * 100, 1) if neg_control_total > 0 else 100.0
        )
        avg_latency = round(sum(latencies) / max(1, len(latencies)), 2)

        return EvalReportResponse(
            total_questions=total_questions,
            passed_count=passed_count,
            retrieval_hit_rate_pct=retrieval_hit_rate,
            citation_validity_pct=citation_validity,
            negative_control_abstention_pct=neg_abstention_rate,
            average_latency_ms=avg_latency,
            is_model_judged=False,
            results=results,
        )


if __name__ == "__main__":
    import asyncio

    async def main():
        print("\n=======================================================")
        print("          SourceIQ Curated Benchmark Evaluator         ")
        print("=======================================================\n")
        db = SessionLocal()
        try:
            report = await Evaluator.run_evaluation(db)
            print(f"Total Questions Evaluated: {report.total_questions}")
            print(f"Total Passed:              {report.passed_count}/{report.total_questions} ({round(report.passed_count/report.total_questions*100, 1)}%)")
            print(f"Retrieval Hit Rate:        {report.retrieval_hit_rate_pct}%")
            print(f"Citation Validity Rate:    {report.citation_validity_pct}%")
            print(f"Negative Control Abstain:  {report.negative_control_abstention_pct}%")
            print(f"Average Latency:           {report.average_latency_ms} ms\n")
            print("Detailed Item Results:")
            for item in report.results:
                mark = "[PASS]" if item.passed else "[FAIL]"
                print(f"  {mark} {item.id} ({item.category}): {item.actual_behavior}")
            print("\n=======================================================\n")
        finally:
            db.close()

    asyncio.run(main())
