from typing import List, Tuple
from src.config.settings import settings
from src.data.models import GroundingDecision
from src.rag.models import RagNewsMetadata
from src.config.logger import setup_logger

logger = setup_logger(__name__)


class GroundingService:
    """
    Owns evaluation criteria for determining if retrieved context is high-quality.
    Performs deterministic rule validation over Cross-Encoder scores.
    """

    def __init__(
        self,
        min_score_threshold: float = settings.GROUNDING_MIN_SCORE,
        min_chunks: int = settings.GROUNDING_MIN_CHUNKS,
        min_average_threshold: float = settings.GROUNDING_MIN_AVERAGE_SCORE
    ) -> None:

        """
        Args:
            min_score_threshold: Minimum Cross-Encoder score needed for the top candidate.
            min_chunks: Minimum number of candidate chunks required to support the query.
            min_average_threshold: Minimum average Cross-Encoder score of retrieved chunks.
        """
        self.min_score_threshold = min_score_threshold
        self.min_chunks = min_chunks
        self.min_average_threshold = min_average_threshold

        logger.info(
            "GroundingService | Initialized with thresholds: "
            "min_score=%.4f, min_avg=%.4f, min_chunks=%d",
            self.min_score_threshold,
            self.min_average_threshold,
            self.min_chunks
        )

    def evaluate(
        self,
        query: str,
        ranked_chunks_with_scores: List[Tuple[RagNewsMetadata, float]]
    ) -> GroundingDecision:
        """
        Applies deterministic rules to decide if we should proceed to the prompt building layer.

        Args:
            query: The user query being analyzed.
            ranked_chunks_with_scores: List of (chunk, reranker_score) sorted descending.

        Returns:
            GroundingDecision: Dictates if the system has enough grounding evidence.
        """
        candidate_count = len(ranked_chunks_with_scores)

        # Extract score arrays for diagnostics (even if count is 0)
        scores = [score for chunk, score in ranked_chunks_with_scores]
        best_score = scores[0] if scores else 0.0
        
        # 6.4.3: Calculate average of top-3 scores to avoid distortion by low relevance tail chunks
        top_scores = scores[:3]
        average_score = (sum(top_scores) / len(top_scores)) if len(top_scores) > 0 else 0.0

        # -----------------------------------------------------------------
        # Diagnostic log: Always emit full context before any rule fires
        # -----------------------------------------------------------------
        logger.info(
            "GroundingService | DIAGNOSTICS | Query: '%s' | "
            "Candidates: %d | Best: %.4f | Top3 Avg: %.4f | "
            "Thresholds -> min_score: %.4f, min_top3_avg: %.4f, min_chunks: %d",
            query, candidate_count, best_score, average_score,
            self.min_score_threshold, self.min_average_threshold, self.min_chunks
        )

        # -------------------------------------------------------------
        # Rule 1: Validate Chunk count density
        # -------------------------------------------------------------
        if candidate_count < self.min_chunks:
            reason = f"Grounding failed: Insufficient retrieved evidence. (Found {candidate_count} chunks, required >= {self.min_chunks})"
            logger.warning(f"GroundingService | Query: '{query}' | Decision: REFUSE | Reason: {reason}")
            return GroundingDecision(
                is_grounded=False,
                reason=reason,
                confidence_score=0.0
            )

        # -------------------------------------------------------------
        # Rule 2: Validate Peak Relevance Check (Best Score)
        # -------------------------------------------------------------
        if best_score < self.min_score_threshold:
            reason = f"Grounding failed: Top reranker score below threshold. (Best: {best_score:.4f}, Required >= {self.min_score_threshold})"
            logger.warning(f"GroundingService | Query: '{query}' | Decision: REFUSE | Reason: {reason}")
            return GroundingDecision(
                is_grounded=False,
                reason=reason,
                confidence_score=best_score
            )

        # -------------------------------------------------------------
        # Rule 3: Validate Average Quality Gating (Top-3 Average)
        # -------------------------------------------------------------
        if average_score < self.min_average_threshold:
            reason = f"Grounding failed: Top-3 average evidence score below threshold. (Top-3 Avg: {average_score:.4f}, Required >= {self.min_average_threshold})"
            logger.warning(f"GroundingService | Query: '{query}' | Decision: REFUSE | Reason: {reason}")
            return GroundingDecision(
                is_grounded=False,
                reason=reason,
                confidence_score=average_score
            )

        # -------------------------------------------------------------
        # Success: Grounding validated successfully
        # -------------------------------------------------------------
        reason = "Evidence passed all grounding checks."
        logger.info(
            f"GroundingService | Query: '{query}' | Decision: ALLOW | "
            f"Candidates: {candidate_count} | Best Score: {best_score:.4f} | Top-3 Avg Score: {average_score:.4f}"
        )
        return GroundingDecision(
            is_grounded=True,
            reason=reason,
            confidence_score=average_score
        )
