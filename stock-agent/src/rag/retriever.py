"""
RAG Retriever
=============

Phase 7.4 — RAG Integration: Retrieval Pipeline

This orchestrates the end-to-end retrieval flow:
    Query -> Embedding -> FAISS Search -> Postgres Metadata Fetch -> Format

Architecture Placement:
-----------------------
    Analysis Layer  →  RAGRetriever.retrieve()  →  Reasoning (LLM)

Data Flow (Online Query Time):
------------------------------
    symbol (+ optional free-text query)
        ↓
    Query embedding produced inside EmbeddingModel
        ↓
    FAISS similarity search bounded locally via FAISSStore
        ↓
    Raw news strings fetched from PostgreSQL mapping
        ↓
    RetrievalResult built and returned
"""

from __future__ import annotations

from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag.embedder import EmbeddingModel
from src.rag.faiss_store import FAISSStore
from src.config.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class RetrievalResult:
    """
    The value object returned by the RAG layer.

    Attributes
    ----------
    symbol : str
        The ticker for which context was retrieved.
    items : list[str]
        Ordered list of relevant news snippets (most-similar first).
        Each element is a short, human-readable string ready to be
        appended verbatim to the LLM prompt.
    """
    symbol: str
    items: list[str] = field(default_factory=list)

    @property
    def formatted_context(self) -> str:
        """
        Formats the retrieved items into an LLM-friendly block.
        Fallback handling is implemented here if `items` is empty.
        """
        if not self.items:
            return "No significant recent news found."
        
        lines = ["Recent News:\n"]
        for idx, item in enumerate(self.items, 1):
            lines.append(f"{idx}. {item}")
            
        return "\n".join(lines)


class RAGRetriever:
    """
    Public interface orchestrating the RAG retrieval subsystem.

    Responsibilities (SRP):
    -----------------------
        - Embed incoming queries using `EmbeddingModel`.
        - Search FAISS index + fetch metadata using `FAISSStore`.
        - Enforce limits and fallbacks.
        - Return a sanitized ``RetrievalResult`` to the caller.
    """

    def __init__(self, store: FAISSStore, embedder: EmbeddingModel) -> None:
        """
        Dependency injected setup for cleaner testing / inversion of control.
        
        Parameters
        ----------
        store : FAISSStore
            Initialized vector store system.
        embedder : EmbeddingModel
            Initialized lightweight embedding system.
        """
        self.store = store
        self.embedder = embedder

    async def retrieve(
        self,
        symbol: str,
        db_session: AsyncSession,
        query: str = "",
        top_k: int = 5,
    ) -> RetrievalResult:
        """
        Retrieve the Top-K most relevant news snippets for a given symbol.

        Parameters
        ----------
        symbol : str
            The stock ticker being analyzed.
        db_session : AsyncSession
            Active async database session for Postgres metadata fetching.
        query : str, optional
            A natural-language hint. If omitted, the `symbol` is used.
        top_k : int, optional
            Limit to avoid LLM overload. Defaults to 5.

        Returns
        -------
        RetrievalResult
            A structured, LLM-ready dataclass of search hits.
        """
        # Determine strict semantic query
        semantic_query = query.strip() if query.strip() else f"Recent context and news updates for {symbol}"
        logger.debug("RAGRetriever | Generating embedding for query: '%s'", semantic_query)
        
        # 1. Embed Query
        vector = self.embedder.embed_text(semantic_query)
        
        # 2. Search FAISS + DB
        logger.debug("RAGRetriever | Searching vector storage for top %d items", top_k)
        records = await self.store.search(query_vector=vector, top_k=top_k, db_session=db_session)
        
        # 3. Format and clean output text
        retrieved_texts = []
        for r in records:
            # Enforce limits loosely (truncating at 1000 chars per item just to be safe)
            clean_text = r.news_text.strip()
            if len(clean_text) > 1000:
                clean_text = clean_text[:997] + "..."
            retrieved_texts.append(clean_text)

        logger.info("RAGRetriever | Retrieved %d context items for '%s'", len(retrieved_texts), symbol)
        
        return RetrievalResult(
            symbol=symbol,
            items=retrieved_texts
        )
