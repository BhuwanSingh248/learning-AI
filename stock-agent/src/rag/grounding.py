from typing import List, Tuple
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
        min_score_threshold: float = 0.0,
        min_chunks: int = 1,
        min_average_threshold: float = -1.0
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

        # Extract score arrays for numerical rule evaluations
        scores = [score for chunk, score in ranked_chunks_with_scores]
        best_score = scores[0]
        average_score = sum(scores) / candidate_count

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
        # Rule 3: Validate Average Quality Gating
        # -------------------------------------------------------------
        if average_score < self.min_average_threshold:
            reason = f"Grounding failed: Average evidence score below threshold. (Average: {average_score:.4f}, Required >= {self.min_average_threshold})"
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
            f"Candidates: {candidate_count} | Best Score: {best_score:.4f} | Avg Score: {average_score:.4f}"
        )
        return GroundingDecision(
            is_grounded=True,
            reason=reason,
            confidence_score=average_score
        )

