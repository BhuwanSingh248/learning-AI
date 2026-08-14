# Ingestion, Chunking and Embeddings

**Status:** Implemented, with correctness improvements planned

## Flow
```text
raw news/article
  -> normalization
  -> chunking
  -> embedding model
  -> vector + metadata
  -> persistent storage / FAISS index
```

## Chunker
The chunker turns long documents into retrieval-sized units and preserves metadata needed for citations and filtering.

**Important:** the roadmap includes replacing the current approximation with real tokenizer-based chunking so `chunk_size` and `overlap` represent tokens rather than sentence/character estimates.

## Embeddings
The embedding model converts each chunk into a dense vector. The model identity and vector dimension must be part of index metadata because changing the model invalidates an existing vector index.

## Required invariants
- Stable document/chunk identity.
- Deterministic content hashing.
- Model/version metadata.
- Consistent dimension.
- Idempotent re-ingestion.
- No duplicate vectors for the same canonical chunk.

## Planned optimization
Batch embedding, embedding cache, incremental ingestion and index generation/versioning.
