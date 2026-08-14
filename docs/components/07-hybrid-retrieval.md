# Hybrid Retrieval

**Status:** Implemented, with ranking/efficiency improvements planned

## Components
- **BM25Retriever:** lexical/keyword retrieval.
- **FAISS retrieval:** semantic similarity retrieval.
- **HybridRetriever:** combines candidate sets.

## Flow
```text
query
  ├──> BM25 --------┐
  └──> embedding -> FAISS
                    │
                    ▼
              candidate merge
                    │
                    ▼
              hybrid ranking
```

## Why hybrid retrieval
BM25 is strong for exact entities, tickers and terminology. Dense retrieval handles semantic similarity and paraphrases. Combining them reduces dependence on either signal alone.

## Current improvement targets
- Use reciprocal-rank fusion or another score-aware method instead of treating heterogeneous raw scores as directly comparable.
- Persist/incrementally update BM25 instead of rebuilding it for every request.
- Filter semantic candidates by symbol/metadata before final ranking where appropriate.
- Batch and cache query embeddings.
