import time
from typing import Dict, Any, Optional
from src.metrics.models import PipelineMetrics

class MetricsCollector:
    """
    Collects performance metrics for a single stock analysis request or evaluation.
    Not thread-safe, intended to be instantiated per request/loop iteration.
    """
    def __init__(self) -> None:
        self.start_times: Dict[str, float] = {}
        self.durations: Dict[str, float] = {}
        self.counts: Dict[str, int] = {}
        self.metadata: Dict[str, Any] = {}
        self.grounded: bool = False
        self.model_name: Optional[str] = None

    def start_stage(self, stage_name: str) -> None:
        """Starts timing a specific stage (e.g. retrieval)."""
        self.start_times[stage_name] = time.perf_counter()

    def end_stage(self, stage_name: str) -> None:
        """Ends timing a specific stage and stores the duration in ms."""
        start_time = self.start_times.get(stage_name)
        if start_time is not None:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            self.durations[stage_name] = elapsed

    def set_count(self, name: str, val: int) -> None:
        """Sets a quantitative metric (e.g. number of chunks retrieved)."""
        self.counts[name] = val

    def set_grounded(self, grounded: bool) -> None:
        """Stores the grounding check outcome flag."""
        self.grounded = grounded

    def set_model_name(self, name: str) -> None:
        """Stores the name of the active reasoning model."""
        self.model_name = name

    def set_metadata(self, key: str, val: Any) -> None:
        """Stores auxiliary data for future Langfuse or diagnostic reporting."""
        self.metadata[key] = val

    def get_metrics(self) -> PipelineMetrics:
        """Builds and returns a consolidated PipelineMetrics payload."""
        return PipelineMetrics(
            total_duration_ms=self.durations.get("total", 0.0),
            retrieval_duration_ms=self.durations.get("retrieval", 0.0),
            reranker_duration_ms=self.durations.get("reranker", 0.0),
            grounding_duration_ms=self.durations.get("grounding", 0.0),
            prompt_build_duration_ms=self.durations.get("prompt_build", 0.0),
            llm_duration_ms=self.durations.get("llm", 0.0),
            chunks_retrieved=self.counts.get("chunks_retrieved", 0),
            chunks_after_rerank=self.counts.get("chunks_after_rerank", 0),
            grounded=self.grounded,
            model_name=self.model_name,
            additional_data=self.metadata
        )
