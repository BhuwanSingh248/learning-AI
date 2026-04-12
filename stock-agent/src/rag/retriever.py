"""
RAG Retriever
=============

Defines the public contract for the RAG retrieval layer.

Architecture Placement:
-----------------------
    Analysis Layer  →  RAGRetriever.retrieve()  →  Reasoning (LLM)

Data Flow:
----------

    Offline (Indexing):
        News articles → Embedding model → FAISS index → Persisted on disk

    Online (Query Time):
        symbol (+ optional free-text query)
            ↓
        Query embedding produced
            ↓
        FAISS similarity search  (Top-K = 5 for MVP)
            ↓
        Raw news strings fetched from store
            ↓
        RetrievalResult returned to ReasoningEngine

Inputs:
-------
    symbol : str      — The ticker being analysed (e.g. "AAPL")
    query  : str      — Optional natural-language context clue
                        (e.g. "recent earnings performance")
    top_k  : int      — Number of results to return.  Default: 5 (MVP).

Outputs:
--------
    RetrievalResult   — A lightweight dataclass containing:
                            symbol    : str
                            items     : list[str]   (plain news snippets)

Retrieval Strategy (MVP):
-------------------------
    Pure similarity search via FAISS (cosine / L2).
    Hybrid search (keyword + vector) and time-weighted retrieval are
    deferred to the backlog.

NOTE (Phase 7.1):
-----------------
    This file holds DESIGN STUBS ONLY.
    The class body raises NotImplementedError everywhere so that callers
    fail fast and clearly if this layer is wired up before Phase 7.2.
    Do NOT implement FAISS / embedding logic here yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field


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


class RAGRetriever:
    """
    Public interface for the RAG retrieval subsystem.

    Responsibilities (SRP):
    -----------------------
        - Embed incoming queries (Phase 7.2)
        - Search FAISS index for Top-K similar news (Phase 7.2)
        - Return a ``RetrievalResult`` to the caller

    NOT responsible for:
    --------------------
        - Fetching news from external APIs  → src/data/
        - Cleaning / chunking raw text      → src/processing/
        - Scoring signals                   → src/analysis/
        - Building or sending LLM prompts   → src/llm/

    Design (DIP):
    -------------
        The LLM Reasoning layer depends **only** on ``RetrievalResult``.
        It has no knowledge of FAISS, embeddings, or how context is produced.
        This lets us swap the backend (e.g. ChromaDB, Qdrant) without
        touching the LLM layer.

    Design (OCP):
    -------------
        Retrieval strategy, Top-K value, and similarity metric can be
        changed by sub-classing or injecting different parameters —
        the public ``retrieve()`` signature stays stable.

    Usage (future, Phase 7.2+):
    ----------------------------
        retriever = RAGRetriever(index_path="faiss.index", store_path="news_store.json")
        result    = retriever.retrieve(symbol="AAPL", query="recent earnings", top_k=5)
        # result.items → ["Apple reported ...", "Analysts raised ...", ...]
    """

    def __init__(self, index_path: str, store_path: str) -> None:
        """
        Parameters
        ----------
        index_path : str
            Path to the persisted FAISS index file.
            (Implementation deferred to Phase 7.2)
        store_path : str
            Path to the JSON / SQLite file mapping FAISS IDs → news text.
            (Implementation deferred to Phase 7.2)
        """
        # TODO (Phase 7.2): Load FAISS index from index_path
        # TODO (Phase 7.2): Load news store from store_path
        raise NotImplementedError(
            "RAGRetriever is a Phase 7.1 design stub. "
            "Implementation begins in Phase 7.2."
        )

    def retrieve(
        self,
        symbol: str,
        query: str = "",
        top_k: int = 5,
    ) -> RetrievalResult:
        """
        Retrieve the Top-K most relevant news snippets for a given symbol.

        Parameters
        ----------
        symbol : str
            The stock ticker being analysed.
        query : str, optional
            A natural-language hint to guide retrieval.
            If omitted, the symbol name is used as the implicit query.
        top_k : int, optional
            Maximum number of results to return.  Defaults to 5 (MVP value).

        Returns
        -------
        RetrievalResult
            Frozen dataclass with ``symbol`` and ``items`` (list of strings).

        Raises
        ------
        NotImplementedError
            Always, until Phase 7.2 implementation is complete.
        """
        # TODO (Phase 7.2): Embed `query` (or symbol) using the embedding model
        # TODO (Phase 7.2): Run FAISS.search(embedding, top_k) → IDs + distances
        # TODO (Phase 7.2): Look up IDs in news store → text snippets
        # TODO (Phase 7.2): Return RetrievalResult(symbol=symbol, items=snippets)
        raise NotImplementedError(
            "RAGRetriever.retrieve() is a Phase 7.1 design stub."
        )
