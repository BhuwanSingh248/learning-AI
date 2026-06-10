from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.rag.models import RagNewsMetadata
from src.rag.faiss_store import FAISSStore
from src.rag.bm25_retriever import BM25Retriever
from src.rag.embedder import EmbeddingModel
from src.config.logger import setup_logger

logger = setup_logger(__name__)

class HybridRetriever:
    """
    Orchestrates search requests across semantic (FAISS) and keyword-based (BM25) retrievers.
    Coordinates fetching candidates, indexing them into BM25 dynamically, querying both,
    and deduplicating the results.
    """

    def __init__(self, faiss_store: FAISSStore, bm25_retriever: BM25Retriever, embedder: EmbeddingModel) -> None:
        """
        Constructor utilizing dependency injection (DIP).
        """
        self.faiss_store = faiss_store
        self.bm25_retriever = bm25_retriever
        self.embedder = embedder

    async def search(self, query: str, symbol: str, db_session: AsyncSession, top_k: int = 5) -> List[RagNewsMetadata]:
        """
        Executes parallel retrieval across FAISS and BM25, merging and deduplicating on chunk_id.
        """
        logger.info(f"HybridRetriever | Triggering search for '{symbol}' with query: '{query}'")

        # -------------------------------------------------------------
        # Phase 1: Fetch candidate chunks for BM25 from Postgres
        # -------------------------------------------------------------
        logger.debug(f"HybridRetriever | Fetching candidates from database for '{symbol}'")
        stmt = select(RagNewsMetadata).where(RagNewsMetadata.symbol == symbol)
        db_result = await db_session.execute(stmt)
        all_chunks = list(db_result.scalars().all())

        if not all_chunks:
            logger.warning(f"HybridRetriever | No news chunks found in database for '{symbol}'. Fallback retrieval triggered.")
            # If no historical metadata exists, return empty list immediately
            return []

        # -------------------------------------------------------------
        # Phase 2: Load and index candidates into BM25
        # -------------------------------------------------------------
        logger.debug(f"HybridRetriever | Loading {len(all_chunks)} chunks into BM25 index")
        self.bm25_retriever.add_chunks(all_chunks)

        # -------------------------------------------------------------
        # Phase 3: Execute BM25 search (synchronous)
        # -------------------------------------------------------------
        logger.debug("HybridRetriever | Executing BM25 keyword search")
        bm25_hits = self.bm25_retriever.search(query=query, top_k=top_k)
        bm25_results = [record for record, score in bm25_hits]

        # -------------------------------------------------------------
        # Phase 4: Execute FAISS vector search (asynchronous)
        # -------------------------------------------------------------
        logger.debug("HybridRetriever | Generating query embedding for FAISS")
        vectorized_query = self.embedder.embed_text(query)
        
        logger.debug("HybridRetriever | Executing FAISS semantic search")
        vector_results = await self.faiss_store.search(
            query_vector=vectorized_query,
            top_k=top_k,
            db_session=db_session
        )

        # -------------------------------------------------------------
        # Phase 5: Merge and deduplicate results on chunk_id (Step 3.3)
        # -------------------------------------------------------------
        seen_chunk_ids = set()
        merged_results = []

        # Logic: Combine vector hits first (retaining semantic relevance), then append keyword hits
        for record in vector_results + bm25_results:
            if record.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(record.chunk_id)
                merged_results.append(record)

        logger.info(f"HybridRetriever | Retained {len(merged_results)} unique chunks after deduplication (limit={top_k})")
        return merged_results[:top_k]