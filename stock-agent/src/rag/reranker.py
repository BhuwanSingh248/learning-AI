from typing import List, Tuple
from sentence_transformers import CrossEncoder

from src.rag.models import RagNewsMetadata
from src.config.logger import setup_logger

logger = setup_logger(__name__)

class Reranker:
    """
    Reranks candidate news chunks using a local Cross-Encoder model.
    Implements a precise, token-level comparison between the query and each chunk.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        """
        Loads the Cross-Encoder model lazily to avoid application startup bottlenecks.
        """
        self.model_name = model_name
        self._model: CrossEncoder | None = None
        logger.debug("Reranker | Configured with model '%s' (lazy load)", model_name)

    def _load_model(self) -> CrossEncoder:
        """
        Internal helper to load the CrossEncoder model when needed.
        """
        if self._model is None:
            logger.info("Reranker | Loading model '%s' …", self.model_name)
            # Instantiates the HuggingFace CrossEncoder model locally
            self._model = CrossEncoder(self.model_name)
            logger.info("Reranker | Model successfully loaded.")
        return self._model

    def rerank(
        self,
        query: str,
        candidates: List[RagNewsMetadata],
        top_k: int = 5
    ) -> List[Tuple[RagNewsMetadata, float]]:
        """
        Scores all candidate chunks against the user query, sorts them by relevance,
        and returns the top_k.

        Args:
            query: The search query string.
            candidates: A list of retrieved RagNewsMetadata objects.
            top_k: Number of highest-ranked results to return.

        Returns:
            List[Tuple[RagNewsMetadata, score]]: Sorted list of chunks with relevance scores.
        """
        if not candidates:
            logger.warning("Reranker | No candidates provided for reranking.")
            return []

        # Load the neural model lazily
        model = self._load_model()

        # 1. Format inputs as pairs of (query, document_text)
        # We access 'chunk_text' from the database metadata model
        pairs = [(query, chunk.chunk_text) for chunk in candidates]
        logger.debug("Reranker | Evaluating relevance for %d candidates", len(candidates))

        # 2. Predict relevance scores (returns a list of floats)
        scores = model.predict(pairs)

        # 3. Pair each record with its score
        ranked_results = [(candidate, float(score)) for candidate, score in zip(candidates, scores)]
        # 4. Sort results descending based on relevance score
        ranked_results.sort(key=lambda item: item[1], reverse=True)

        logger.info("Reranker | Completed reranking. Best score: %.4f | Worst score: %.4f", ranked_results[0][1], ranked_results[-1][1])

        # 5. Return top_k highest scores
        return ranked_results[:top_k]
