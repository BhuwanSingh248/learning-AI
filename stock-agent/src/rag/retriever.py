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
from src.rag.hybrid_retriever import HybridRetriever
from src.rag.reranker import Reranker
from src.rag.grounding import GroundingService
from src.rag.context_builder import CitationContextBuilder
from src.data.models import CitationContext

class RAGRetriever:
    """
    Public interface orchestrating the advanced RAG retrieval subsystem.
    Coordinates candidate fetching (hybrid), reranking, grounding evaluation, and citation-aware context building.
    """

    def __init__(self, hybrid_retriever: HybridRetriever, reranker: Reranker, grounding_service: GroundingService) -> None:
        """
        Dependency injected setup for cleaner testing / inversion of control.
        """
        self.hybrid_retriever = hybrid_retriever
        self.reranker = reranker
        self.grounding_service = grounding_service

    async def retrieve(
        self,
        symbol: str,
        db_session: AsyncSession,
        query: str = "",
        top_k: int = 5,
    ) -> CitationContext:
        """
        Retrieve the Top-K most relevant news snippets for a given symbol using hybrid search,
        neural reranking, grounding evaluation, and formatting them with gapless sequential citations.

        Parameters
        ----------
        symbol : str
            The stock ticker being analyzed.
        db_session : AsyncSession
            Active async database session.
        query : str, optional
            A natural-language hint. If omitted, the `symbol` is used.
        top_k : int, optional
            Limit for the final number of chunks. Defaults to 5.

        Returns
        -------
        CitationContext
            A structured, LLM-ready context block mapping citations and grounding decisions.
        """
        # Determine strict search query
        search_query = query.strip() if query.strip() else f"Recent context and news updates for {symbol}"
        logger.info(f"RAGRetriever | Starting RAG pipeline for '{symbol}' with query: '{search_query}'")

        # 1. Retrieve raw candidates (fetch a larger pool size so neural reranking has choices)
        candidate_pool_size = top_k * 4
        logger.debug(f"RAGRetriever | Fetching up to {candidate_pool_size} candidates via Hybrid search")
        candidates = await self.hybrid_retriever.search(
            query=search_query,
            symbol=symbol,
            db_session=db_session,
            top_k=candidate_pool_size
        )

        # 2. Score and rerank candidates using Cross-Encoder model
        logger.debug(f"RAGRetriever | Reranking {len(candidates)} candidate chunks")
        ranked_pairs = self.reranker.rerank(
            query=search_query,
            candidates=candidates,
            top_k=top_k
        )

        # 3. Evaluate Grounding Decision
        logger.debug("RAGRetriever | Running grounding evaluation")
        grounding_decision = self.grounding_service.evaluate(
            query=search_query,
            ranked_chunks_with_scores=ranked_pairs
        )

        # 4. Formulate response based on grounding path
        if not grounding_decision.is_grounded:
            logger.warning(f"RAGRetriever | Grounding checks failed for '{symbol}'. Query refused.")
            return CitationContext(
                formatted_text="Insufficient evidence available to answer this question reliably.",
                citations=[],
                grounding=grounding_decision
            )

        ranked_chunks = [chunk for chunk, score in ranked_pairs]

        # 5. Build evidence-backed citation context
        logger.debug("RAGRetriever | Building citation context block")
        citation_context = CitationContextBuilder.build_context(
            chunks=ranked_chunks,
            preview_char_limit=150
        )
        
        # Attach the successful grounding decision to the context
        citation_context.grounding = grounding_decision

        logger.info(f"RAGRetriever | Successfully generated context with {len(citation_context.citations)} citations for '{symbol}'")
        return citation_context


