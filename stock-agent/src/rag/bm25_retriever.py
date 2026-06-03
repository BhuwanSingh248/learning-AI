from typing import List, Tuple
from rank_bm25 import BM25Okapi

from src.config.logger import setup_logger
from src.rag.models import RagNewsMetadata

logger = setup_logger(__name__)


class BM25Retriever:
    """
    Keyword-based retriever using BM25.

    Responsibilities:
    - Index chunk text
    - Execute keyword search
    - Return ranked chunk candidates

    Non-responsibilities:
    - FAISS search
    - Embeddings
    - Symbol filtering
    - Reranking
    - LLM interaction
    """

    def __init__(self) -> None:
        self.index: BM25Okapi | None = None
        self.records: List[RagNewsMetadata] = []

    def _tokenize(self, text: str) -> List[str]:
        """
        Normalize text for indexing and querying.
        """
        return [
            word.strip(".,!?\"'()[]{}").lower()
            for word in text.split()
            if word.strip()
        ]

    def add_chunks(self, chunks: List[RagNewsMetadata]) -> None:
        """
        Build a BM25 index from chunk records.

        NOTE:
        Current implementation rebuilds the entire index.
        Acceptable for MVP.
        """
        if not chunks:
            logger.warning(
                "BM25Retriever: No chunks provided for indexing."
            )
            return

        self.records = chunks

        tokenized_docs = [
            self._tokenize(chunk.chunk_text)
            for chunk in chunks
        ]

        self.index = BM25Okapi(tokenized_docs)

        logger.info(
            "BM25Retriever: Indexed %s chunks.",
            len(chunks)
        )

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[RagNewsMetadata, float]]:
        """
        Perform keyword search and return top-k ranked chunks.

        Returns:
            List[
                (
                    RagNewsMetadata,
                    score
                )
            ]
        """
        if not self.index:
            logger.warning(
                "BM25Retriever: No index available."
            )
            return []

        query_tokens = self._tokenize(query)

        scores = self.index.get_scores(query_tokens)

        results = [
            (record, float(score))
            for record, score in zip(self.records, scores)
        ]

        results.sort(
            key=lambda item: item[1],
            reverse=True
        )

        return results[:top_k]