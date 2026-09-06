import json
from pathlib import Path

import pytest

from evaluation.metrics import (
    calibrate_grounding_thresholds,
    classification_metrics,
    retrieval_metrics,
)


GOLDEN_SET = Path(__file__).parents[2] / "evaluation" / "golden_set.v1.jsonl"


def test_golden_set_is_versioned_and_has_required_fields():
    rows = [json.loads(line) for line in GOLDEN_SET.read_text(encoding="utf-8").splitlines()]
    assert len(rows) >= 10
    assert {row["schema_version"] for row in rows} == {"1.0"}
    assert len({row["case_id"] for row in rows}) == len(rows)
    for row in rows:
        assert row["symbol"]
        assert row["query"]
        assert isinstance(row["relevant_evidence_ids"], list)
        assert "expected_recommendation" in row["expected_answer_properties"]


def test_retrieval_metrics_perfect_ranked_results():
    metrics = retrieval_metrics(["e1", "e2", "e3"], ["e1", "e2"])
    assert metrics.precision == pytest.approx(2 / 3)
    assert metrics.recall == pytest.approx(1.0)
    assert metrics.mrr == pytest.approx(1.0)
    assert metrics.ndcg == pytest.approx(1.0)


def test_classification_metrics():
    metrics = classification_metrics([True, True, False, False], [True, False, False, True])
    assert metrics.accuracy == pytest.approx(0.5)
    assert metrics.precision == pytest.approx(0.5)
    assert metrics.recall == pytest.approx(0.5)
    assert metrics.f1 == pytest.approx(0.5)


def test_grounding_calibration_finds_measured_thresholds():
    samples = [
        {"expected_grounded": True, "best_score": -2.0, "top_3_average": -4.0, "candidate_count": 2},
        {"expected_grounded": True, "best_score": -3.0, "top_3_average": -5.0, "candidate_count": 2},
        {"expected_grounded": False, "best_score": -8.0, "top_3_average": -10.0, "candidate_count": 2},
        {"expected_grounded": False, "best_score": -10.0, "top_3_average": -12.0, "candidate_count": 1},
    ]
    result = calibrate_grounding_thresholds(samples, min_precision=1.0)
    assert result["precision_target_met"] is True
    assert result["f1"] == pytest.approx(1.0)
    assert result["min_score"] >= -8.0
    assert result["min_average"] >= -10.0
