from __future__ import annotations

from dataclasses import dataclass
from math import log2
from typing import Iterable, Sequence


@dataclass(frozen=True)
class RetrievalMetrics:
    precision: float
    recall: float
    mrr: float
    ndcg: float


@dataclass(frozen=True)
class ClassificationMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float


def _normalise(values: Iterable[str]) -> list[str]:
    return [str(value) for value in values]


def retrieval_metrics(
    retrieved_ids: Sequence[str],
    relevant_ids: Iterable[str],
    k: int | None = None,
) -> RetrievalMetrics:
    """Compute precision, recall, reciprocal rank and nDCG for one query."""
    retrieved = _normalise(retrieved_ids[:k] if k is not None else retrieved_ids)
    relevant = set(_normalise(relevant_ids))

    if not relevant:
        return RetrievalMetrics(
            precision=1.0 if not retrieved else 0.0,
            recall=1.0 if not retrieved else 0.0,
            mrr=1.0 if not retrieved else 0.0,
            ndcg=1.0 if not retrieved else 0.0,
        )

    hits = [item in relevant for item in retrieved]
    hit_count = sum(hits)
    precision = hit_count / len(retrieved) if retrieved else 0.0
    recall = hit_count / len(relevant)

    reciprocal_rank = 0.0
    for rank, hit in enumerate(hits, start=1):
        if hit:
            reciprocal_rank = 1.0 / rank
            break

    dcg = sum((1.0 / log2(rank + 1)) for rank, hit in enumerate(hits, start=1) if hit)
    ideal_hits = min(len(relevant), len(retrieved))
    idcg = sum(1.0 / log2(rank + 1) for rank in range(1, ideal_hits + 1))
    ndcg = dcg / idcg if idcg else 0.0

    return RetrievalMetrics(precision, recall, reciprocal_rank, ndcg)


def classification_metrics(
    expected: Sequence[bool],
    predicted: Sequence[bool],
) -> ClassificationMetrics:
    """Compute binary classification metrics for grounding decisions."""
    if len(expected) != len(predicted):
        raise ValueError("expected and predicted must have the same length")
    if not expected:
        return ClassificationMetrics(0.0, 0.0, 0.0, 0.0)

    tp = sum(e and p for e, p in zip(expected, predicted))
    tn = sum((not e) and (not p) for e, p in zip(expected, predicted))
    fp = sum((not e) and p for e, p in zip(expected, predicted))
    fn = sum(e and (not p) for e, p in zip(expected, predicted))

    accuracy = (tp + tn) / len(expected)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return ClassificationMetrics(accuracy, precision, recall, f1)


def calibrate_grounding_thresholds(
    samples: Sequence[dict],
    score_candidates: Sequence[float] | None = None,
    average_candidates: Sequence[float] | None = None,
    min_precision: float = 0.95,
) -> dict:
    """Grid-search grounding thresholds and return the best measured pair.

    Each sample must contain ``expected_grounded``, ``best_score``,
    ``top_3_average`` and ``candidate_count``. Higher scores are considered
    more relevant, matching GroundingService's existing semantics.
    """
    if not samples:
        raise ValueError("at least one calibration sample is required")

    scores = score_candidates or sorted({float(s["best_score"]) for s in samples})
    averages = average_candidates or sorted({float(s["top_3_average"]) for s in samples})
    chunk_counts = sorted({int(s["candidate_count"]) for s in samples})

    best: dict | None = None
    for min_score in scores:
        for min_average in averages:
            for min_chunks in chunk_counts:
                predicted = [
                    float(sample["best_score"]) >= min_score
                    and float(sample["top_3_average"]) >= min_average
                    and int(sample["candidate_count"]) >= min_chunks
                    for sample in samples
                ]
                expected = [bool(sample["expected_grounded"]) for sample in samples]
                metrics = classification_metrics(expected, predicted)
                candidate = {
                    "min_score": float(min_score),
                    "min_average": float(min_average),
                    "min_chunks": int(min_chunks),
                    "accuracy": metrics.accuracy,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "f1": metrics.f1,
                }
                if metrics.precision < min_precision:
                    continue
                # Prefer F1, then recall, then the least permissive threshold pair.
                key = (metrics.f1, metrics.recall, min_score, min_average, min_chunks)
                if best is None or key > best["_sort_key"]:
                    candidate["_sort_key"] = key
                    best = candidate

    if best is None:
        # No candidate met the requested precision. Return the best F1 result
        # without pretending the requested precision target was achieved.
        fallback = None
        for min_score in scores:
            for min_average in averages:
                for min_chunks in chunk_counts:
                    predicted = [
                        float(sample["best_score"]) >= min_score
                        and float(sample["top_3_average"]) >= min_average
                        and int(sample["candidate_count"]) >= min_chunks
                        for sample in samples
                    ]
                    expected = [bool(sample["expected_grounded"]) for sample in samples]
                    metrics = classification_metrics(expected, predicted)
                    key = (metrics.f1, metrics.precision, metrics.recall)
                    if fallback is None or key > fallback["_sort_key"]:
                        fallback = {
                            "min_score": float(min_score),
                            "min_average": float(min_average),
                            "min_chunks": int(min_chunks),
                            "accuracy": metrics.accuracy,
                            "precision": metrics.precision,
                            "recall": metrics.recall,
                            "f1": metrics.f1,
                            "_sort_key": key,
                        }
        best = fallback

    assert best is not None
    best.pop("_sort_key", None)
    best["precision_target_met"] = best["precision"] >= min_precision
    best["sample_count"] = len(samples)
    return best
