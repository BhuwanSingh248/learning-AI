# Storage and Indexing

**Status:** Implemented

## PostgreSQL
Stores canonical news/document metadata and the mapping required to recover source content and citation information.

## FAISS
Stores dense vectors for semantic nearest-neighbor retrieval.

## Flow
```text
canonical chunk
  -> PostgreSQL metadata
  -> embedding
  -> FAISS vector + stable mapping
```

## Critical consistency rule
PostgreSQL and FAISS represent one logical corpus. A vector must never point at missing/incorrect metadata, and metadata must not claim an active vector that is absent from the active index.

## Planned evolution
- Reconciliation job.
- Versioned index generations.
- Atomic activation of rebuilt indexes.
- Rollback to the previous healthy generation.
- Safe incremental updates/deletes.
