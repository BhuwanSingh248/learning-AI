"""
FAISS Vector Store Module
=========================

Phase 7.3 — RAG Integration: FAISS Index - Storage & Retrieval

This module acts as the ONLY bridging layer between embeddings and vector storage.

Responsibilities (SRP):
-----------------------
    ✅ Initialize and maintain the FAISS index (FlatL2 mapping into IndexIDMap)
    ✅ Store generated vector embeddings
    ✅ Store actual text/metadata in PostgreSQL
    ✅ Query FAISS for Top-K most similar vectors
    ✅ Fetch metadata mapped to those vectors from PostgreSQL
    ✅ Persist FAISS index to disk

Design Principles Applied:
--------------------------
    SRP — ONLY handles vector storage and vector search.
    DIP — Downstream RAGRetriever depends on search method, not directly on FAISS.
    OCP — Later, we can switch from FlatL2 to IVFFlat or HNSW without affecting
          callers, as long as the inputs and outputs of `search` stay the same.

Important Constraints:
----------------------
    - DO NOT fetch data from OpenBB or web here.
    - DO NOT generate embeddings; input must already be an `np.ndarray`.
    - Dimension MUST explicitly match the EmbeddingModel dimension (384).
"""

import os
import faiss
import numpy as np
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from src.rag.models import RagNewsMetadata
from src.config.logger import setup_logger
from src.rag.embedder import EMBEDDING_DIM

logger = setup_logger(__name__)

INDEX_PATH = "rag_faiss.index"


class FAISSStore:
    """
    Stateful interface to the FAISS vector database + PostgreSQL metadata.
    """

    def __init__(self, index_dim: int = EMBEDDING_DIM, save_path: str = INDEX_PATH) -> None:
        """
        Loads an existing index from disk or initializes a new one.

        Parameters
        ----------
        index_dim : int
            Must match embedding output size (default 384).
        save_path : str
            File mapping for the index to persist across boots.
        """
        self.save_path = save_path
        self.index_dim = index_dim

        if os.path.exists(self.save_path):
            self.index = faiss.read_index(self.save_path)
            logger.info("FAISSStore | Loaded existing FAISS index from '%s' (ntotal: %d)",
                        self.save_path, self.index.ntotal)
        else:
            # We need customized IDs to map FAISS vector to PostgreSQL ID
            base_index = faiss.IndexFlatL2(self.index_dim)
            self.index = faiss.IndexIDMap(base_index)
            logger.info("FAISSStore | Initialized new FAISS FlatL2 + IDMap index (dim: %d)", self.index_dim)

    def save(self) -> None:
        """
        Persists the current FAISS index to disk.
        """
        faiss.write_index(self.index, self.save_path)
        logger.debug("FAISSStore | Index saved to '%s'", self.save_path)

    async def add_vector(
        self,
        chunk_id: str,
        source_id: str,
        symbol: str,
        chunk_index: int,
        chunk_text: str,
        timestamp: datetime,
        vector: np.ndarray,
        document_id: str,
        content_hash: str,
        chunking_version: str,
        db_session: AsyncSession
    ) -> int:
        """
        Inserts new text metadata into the PostgreSQL DB to get an ID.
        Then saves the vector to FAISS bounded to that ID.

        Parameters
        ----------
        chunk_id : str
            The unique identifier for the chunk.
        source_id : str
            The unique identifier for the source.
        symbol : str
            The ticker symbol of the stock.
        chunk_index : int
            The index of the chunk within the source.
        chunk_text : str
            The text of the chunk.
        timestamp : datetime
            The timestamp of the chunk.
        vector : np.ndarray
            The embedding vector of the chunk.
        document_id : str
            The stable identifier for the parent document.
        content_hash : str
            The hash of the parent document content.
        chunking_version : str
            The chunking logic version used.
        db_session : AsyncSession
            The database session.
            
        Returns
        -------
        int
            The newly created PostgreSQL sequence ID.
        """
        # Ensure shape matches FAISS batch input requirement (1, dim)
        if len(vector.shape) == 1:
            vector = vector.reshape(1, -1)

        # Convert timestamp to offset-naive UTC to avoid postgres TIMESTAMP WITHOUT TIME ZONE offset issues
        if timestamp.tzinfo is not None:
            timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)

        # 1. Insert Metadata into Database
        from src.config.settings import settings
        metadata = RagNewsMetadata(
            chunk_id=chunk_id,
            source_id=source_id,
            symbol=symbol,
            chunk_index=chunk_index,
            chunk_text=chunk_text,
            timestamp=timestamp,
            document_id=document_id,
            content_hash=content_hash,
            embedding_model=settings.MODEL_NAME,
            chunking_version=chunking_version
        )
        db_session.add(metadata)
        await db_session.flush()  # We flush to acquire `metadata.id` before commit

        meta_id = metadata.id
        
        # 2. Bind FAISS ID insertion logic
        # FAISS expects int64 1D array for labels
        faiss_id_array = np.array([meta_id], dtype=np.int64)

        try:
            self.index.add_with_ids(vector, faiss_id_array)
            # Both succeeded -> commit DB row
            await db_session.commit()
            logger.debug("FAISSStore | Inserted vector %d for '%s'", meta_id, symbol)
            return meta_id
        except Exception as e:
            # If FAISS throws error, rollback the Postgres metadata insertion
            await db_session.rollback()
            logger.error("FAISSStore | Rollback! Error inserting to FAISS: %s", e)
            raise

    def delete_vectors(self, ids: list[int]) -> None:
        """
        Removes the specified IDs (PostgreSQL sequence IDs) from the FAISS IndexIDMap.
        """
        if not ids:
            return
        try:
            ids_array = np.array(ids, dtype=np.int64)
            self.index.remove_ids(ids_array)
            logger.info("FAISSStore | Removed %d vector IDs from FAISS index", len(ids))
        except Exception as e:
            logger.error("FAISSStore | Error removing IDs from FAISS: %s", e)
            raise

    async def search(self, query_vector: np.ndarray, top_k: int, db_session: AsyncSession) -> list[RagNewsMetadata]:
        """
        Finds the closest vectors in FAISS, queries Postgres for the matched IDs, 
        and extracts the result.

        Parameters
        ----------
        query_vector : np.ndarray
            Embedded question or target symbol vector.
        top_k : int
            Amount of similar components to pull.
        db_session : AsyncSession
            Active database connection pool request.

        Returns
        -------
        list[RagNewsMetadata]
            Populated metadata results, structurally ordered from most 
            similar to least similar based on similarity distances.
        """
        if self.index.ntotal == 0:
            logger.warning("FAISSStore | Search called but index is empty. Returning 0 results.")
            return []

        # Vector format enforcing for querying
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)

        # Retrieve vectors
        # Limit `top_k` to `ntotal` to restrict unnecessary padding / OOB checks.
        k = min(top_k, self.index.ntotal)
        
        distances, indices = self.index.search(query_vector, k)
        
        found_ids = indices[0].tolist()
        
        # Strip elements that were unresolved (-1 ID space)
        valid_ids = [vid for vid in found_ids if vid != -1]

        if not valid_ids:
            return []

        # Resolve IDs against central PostgreSQL mapping
        stmt = select(RagNewsMetadata).where(RagNewsMetadata.id.in_(valid_ids))
        result = await db_session.execute(stmt)
        records = result.scalars().all()
        
        # Ensure semantic similarity sorting order is maintained matching the exact distance
        id_to_record = {r.id: r for r in records}
        sorted_records = [id_to_record[vid] for vid in valid_ids if vid in id_to_record]
        
        logger.debug("FAISSStore | Found %d valid metadata records for Top-%d request.", len(sorted_records), top_k)
        return sorted_records
