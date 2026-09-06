from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from src.config.database import AsyncSessionLocal
from src.config.settings import settings
from src.rag.bm25_retriever import BM25Retriever
from src.rag.embedder import EmbeddingModel
from src.rag.faiss_store import FAISSStore
from src.rag.grounding import GroundingService
from src.rag.hybrid_retriever import HybridRetriever
from src.rag.models import RagNewsMetadata
from src.rag.reranker import Reranker

from evaluation.metrics import calibrate_grounding_thresholds, retrieval_metrics


EVALUATION_DIR = Path(__file__).resolve().parent
GOLDEN_SET_PATH = EVALUATION_DIR / "golden_set.v1.jsonl"
DEFAULT_OUTPUT_DIR = EVALUATION_DIR / "results"


def load_golden_set(path: Path = GOLDEN_SET_PATH) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError("golden set is empty")
    versions = {row.get("schema_version") for row in rows}
    if versions != {"1.0"}:
        raise ValueError(f"unsupported golden-set versions: {sorted(versions)}")
    required = {"case_id", "symbol", "query", "expected_grounded", "relevant_evidence_ids", "relevance_keywords"}
    for row in rows:
        missing = required - row.keys()
        if missing:
            raise ValueError(f"{row.get('case_id', '<unknown>')} missing fields: {sorted(missing)}")
    return rows


def _keyword_match(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    if not keywords:
        return False
    matches = sum(keyword.lower() in lowered for keyword in keywords)
    return matches >= max(1, (len(keywords) + 1) // 2)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _aggregate_retrieval(rows: list[dict], strategy: str, k: int) -> dict:
    metrics = [retrieval_metrics(row[strategy], row["relevant_ids"], k=k) for row in rows]
    return {
        "precision": _mean([metric.precision for metric in metrics]),
        "recall": _mean([metric.recall for metric in metrics]),
        "mrr": _mean([metric.mrr for metric in metrics]),
        "ndcg": _mean([metric.ndcg for metric in metrics]),
    }


async def evaluate(golden_set: list[dict]) -> dict:
    embedder = EmbeddingModel()
    faiss_store = FAISSStore()
    bm25_retriever = BM25Retriever()
    hybrid = HybridRetriever(faiss_store=faiss_store, bm25_retriever=bm25_retriever, embedder=embedder)
    reranker = Reranker()

    run_rows: list[dict] = []
    calibration_samples: list[dict] = []

    async with AsyncSessionLocal() as session:
        for case in golden_set:
            result = await session.execute(
                select(RagNewsMetadata).where(RagNewsMetadata.symbol == case["symbol"])
            )
            corpus = list(result.scalars().all())

            # qrels are derived from the annotated query terms against the authoritative
            # corpus snapshot. The stable evidence IDs in the golden set remain the
            # human-facing annotation contract; chunk IDs are runtime corpus identities.
            relevant_ids = [
                chunk.chunk_id
                for chunk in corpus
                if _keyword_match(chunk.chunk_text or "", case["relevance_keywords"])
            ] if case["expected_grounded"] else []

            faiss_results, bm25_results, hybrid_results = await hybrid.search_detailed(
                query=case["query"],
                symbol=case["symbol"],
                db_session=session,
                top_k=20,
            )
            reranked = reranker.rerank(case["query"], hybrid_results, top_k=5)

            best_score = float(reranked[0][1]) if reranked else 0.0
            top_scores = [float(score) for _, score in reranked[:3]]
            top_3_average = _mean(top_scores)

            row = {
                "case_id": case["case_id"],
                "symbol": case["symbol"],
                "query": case["query"],
                "expected_grounded": bool(case["expected_grounded"]),
                "annotated_evidence_ids": case["relevant_evidence_ids"],
                "relevant_ids": relevant_ids,
                "bm25": [chunk.chunk_id for chunk in bm25_results],
                "faiss": [chunk.chunk_id for chunk in faiss_results],
                "hybrid": [chunk.chunk_id for chunk in hybrid_results],
                "reranked": [chunk.chunk_id for chunk, _ in reranked],
                "best_score": best_score,
                "top_3_average": top_3_average,
                "candidate_count": len(reranked),
            }
            run_rows.append(row)
            calibration_samples.append({
                "expected_grounded": case["expected_grounded"],
                "best_score": best_score,
                "top_3_average": top_3_average,
                "candidate_count": len(reranked),
            })

    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "golden_set": {
            "path": str(GOLDEN_SET_PATH.relative_to(EVALUATION_DIR.parent)),
            "version": "1.0",
            "case_count": len(golden_set),
            "sha256": hashlib.sha256(GOLDEN_SET_PATH.read_bytes()).hexdigest(),
        },
        "configuration": {
            "grounding_min_score": settings.GROUNDING_MIN_SCORE,
            "grounding_min_average_score": settings.GROUNDING_MIN_AVERAGE_SCORE,
            "grounding_min_chunks": settings.GROUNDING_MIN_CHUNKS,
            "reranker_model": reranker.model_name,
        },
        "retrieval": {
            strategy: {f"@{k}": _aggregate_retrieval(run_rows, strategy, k) for k in (1, 3, 5)}
            for strategy in ("bm25", "faiss", "hybrid", "reranked")
        },
        "grounding_calibration": calibrate_grounding_thresholds(calibration_samples),
        "cases": run_rows,
    }
    return report


def write_reports(report: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "rag_evaluation.v1.json"
    md_path = output_dir / "rag_evaluation.v1.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# RAG Evaluation Report v1",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Golden cases: **{report['golden_set']['case_count']}**",
        "",
        "## Retrieval",
        "",
        "| Strategy | K | Precision | Recall | MRR | nDCG |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for strategy, values in report["retrieval"].items():
        for k, metrics in values.items():
            lines.append(
                f"| {strategy} | {k[1:]} | {metrics['precision']:.3f} | {metrics['recall']:.3f} | "
                f"{metrics['mrr']:.3f} | {metrics['ndcg']:.3f} |"
            )

    calibration = report["grounding_calibration"]
    lines.extend([
        "",
        "## Grounding calibration",
        "",
        f"- Recommended `min_score`: **{calibration['min_score']:.4f}**",
        f"- Recommended `min_average`: **{calibration['min_average']:.4f}**",
        f"- Recommended `min_chunks`: **{calibration['min_chunks']}**",
        f"- Precision: **{calibration['precision']:.3f}**",
        f"- Recall: **{calibration['recall']:.3f}**",
        f"- F1: **{calibration['f1']:.3f}**",
        f"- Precision target met: **{calibration['precision_target_met']}**",
        "",
        "## Reproducibility",
        "",
        "The JSON report records the golden-set hash, model name, grounding configuration, per-query retrieval runs and calibration samples so a future run can be compared without relying on a hand-edited Markdown report.",
    ])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_only() -> None:
    rows = load_golden_set()
    print(f"Validated {len(rows)} golden cases (schema v1.0).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reproducible RAG evaluation suite.")
    parser.add_argument("--validate-only", action="store_true", help="Validate the golden set without requiring a database.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    golden_set = load_golden_set()
    if args.validate_only:
        print(f"Validated {len(golden_set)} golden cases (schema v1.0).")
        return

    report = asyncio.run(evaluate(golden_set))
    write_reports(report, args.output_dir)
    print(json.dumps(report["grounding_calibration"], indent=2))
    print(f"Reports written to {args.output_dir}")


if __name__ == "__main__":
    main()
