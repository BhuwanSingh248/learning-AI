"""Compatibility entry point for the reproducible RAG calibration suite."""

import asyncio
from pathlib import Path

from evaluation.evaluate_rag import GOLDEN_SET_PATH, evaluate, load_golden_set, write_reports


async def run_calibration(output_dir: Path | None = None) -> None:
    """Run the versioned golden-set benchmark and persist its calibration report."""
    golden_set = load_golden_set(GOLDEN_SET_PATH)
    report = await evaluate(golden_set)
    write_reports(report, output_dir or Path(__file__).resolve().parent / "evaluation" / "results")
    calibration = report["grounding_calibration"]
    print(
        "Recommended grounding thresholds: "
        f"min_score={calibration['min_score']:.4f}, "
        f"min_average={calibration['min_average']:.4f}, "
        f"min_chunks={calibration['min_chunks']}"
    )


if __name__ == "__main__":
    asyncio.run(run_calibration())
