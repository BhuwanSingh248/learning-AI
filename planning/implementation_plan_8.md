# Implementation Plan: Bug - News Indexing Idempotency & Chunk Identity Collisions

## Goal
Resolve issue #8 by enforcing unique constraints, introducing stable document and chunk identifiers, implementing clean upserts (replacing chunks when content changes), separating news ingestion from the `/suggest` retrieval hot-path, and providing a migration/rebuild script for existing duplicates.

## User Review Required
> [!IMPORTANT]
> The database schema changes will require applying unique constraints on `chunk_id` and adding new metadata fields (`document_id`, `content_hash`, `embedding_model`, and `chunking_version`).
> When content changes for an existing article, the old chunks must be safely removed from both PostgreSQL and the FAISS index before the new chunks are indexed.
> The hot-path indexing inside `StockAgent.analyze_stocks` will be removed. Ingestion will be decoupled into a separate endpoint (`POST /ingest`) to protect retrieval performance.

## Proposed Changes

We will modify/create the following files to implement the changes:

---

### 1. Database Schema Extension

#### [MODIFY] [models.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/rag/models.py)
Extend `RagNewsMetadata` schema:
- Add `unique=True` constraint on `chunk_id`.
- Add new columns:
  - `document_id` (String, indexed, nullable=False): The stable identifier computed for the source document.
  - `content_hash` (String, nullable=False): MD5/SHA256 hash of the title + summary.
  - `embedding_model` (String, nullable=False): Identifies the embedding model (e.g. `all-MiniLM-L6-v2`).
  - `chunking_version` (String, nullable=False): Tracks the chunker logic version (e.g. `v1`).

---

### 2. Stable Document and Chunk Identity

#### [MODIFY] [chunker.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/rag/chunker.py)
Update chunk metadata assignment:
- Accept `document_id` (computed during indexing) and `chunking_version` (default `"v1"`).
- Calculate `chunk_id = hashlib.sha256(f"{document_id}_{index}_{chunking_version}".encode()).hexdigest()`.
- Return fully populated `NewsChunk` objects containing these security boundaries.

---

### 3. Idempotent Ingestion & Vector Cleanup

#### [MODIFY] [faiss_store.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/rag/faiss_store.py)
Add support for deleting vectors:
- Implement `delete_vectors(meta_ids: List[int])` to cleanly call `self.index.remove_ids(np.array(meta_ids, dtype=np.int64))` and rebuild mapping coordinates.

#### [MODIFY] [indexer.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/rag/indexer.py)
Implement the idempotent upsert pipeline:
1. Compute stable `document_id = sha256(f"{symbol}_{canonical_url/source}_{timestamp}_{title}")`.
2. Compute `content_hash = sha256(f"{title}_{summary}")`.
3. Check the database for any existing `RagNewsMetadata` rows matching `document_id`:
   - If **found** and `content_hash` matches:
     - Article is unchanged. Skip indexing for this article (idempotent no-op).
   - If **found** but `content_hash` differs:
     - Article updated! Delete old database rows and remove their corresponding IDs from FAISS using `faiss_store.delete_vectors()`, then chunk and re-index the new content.
   - If **not found**:
     - Insert chunks normally.

---

### 4. Decoupling Ingestion from Retrieval

#### [MODIFY] [stock_agent.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/agent/stock_agent.py)
- Remove `self.news_indexer.index_news` from the hot path inside `analyze_stocks` to ensure that querying `/suggest` does not perform synchronous vector store writes.

#### [MODIFY] [__init__.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/api/routes/__init__.py)
- Add a new endpoint `POST /ingest` to execute news ingestion and FAISS indexing independently.
- Accepts `symbol: str` and uses `data_service.get_news(symbol)` to fetch and index news in the database and FAISS.

---

### 5. Rebuild & Cleanup Tools

#### [NEW] [rebuild_index.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/src/rag/rebuild_index.py)
Provide a command-line utility to:
- Identify and clear duplicate news metadata records from PostgreSQL.
- Re-index and rebuild the FAISS vector index from scratch using unique database references.

---

### 6. Automated Testing

#### [NEW] [test_idempotency.py](file:///c:/Users/bhuwa/study/ai_stock_market/stock-agent/tests/rag/test_idempotency.py)
Write tests to verify:
- Repeated indexing of the same news article does not increase database rows or FAISS index size.
- Updating an article's summary replaces the old chunks with the new ones.
- Collision tests to ensure two different articles get unique chunk IDs.

## Verification Plan

### Automated Tests
- Run the new idempotency and collision tests, as well as the full regression suite:
  ```bash
  .venv\Scripts\pytest
  ```

### Manual Verification
- Run the `rebuild_index.py` tool.
- Send consecutive `POST /ingest` requests for a symbol and verify that the database record count does not grow.
