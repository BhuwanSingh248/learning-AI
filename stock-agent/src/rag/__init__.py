"""
RAG (Retrieval-Augmented Generation) Layer
============================================

Phase 7 — RAG Integration

This package owns the ENTIRE retrieval pipeline.  It sits architecturally
**between** the Analysis layer and the LLM Reasoning layer:

    Data → Processing → Analysis
                            ↓
                        RAG Layer          ← YOU ARE HERE
                            ↓
                    Reasoning (LLM)
                            ↓
                        Agent → API

Responsibilities (SRP):
-----------------------
    ✅  Embed and store news documents (offline indexing)
    ✅  Retrieve Top-K relevant news items for a given symbol / query
    ✅  Return a plain list of news strings ready to be appended to the LLM prompt

NOT responsible for:
--------------------
    ❌  Fetching raw data           → src/data/
    ❌  Cleaning / normalising data → src/processing/
    ❌  Scoring / signal creation   → src/analysis/
    ❌  Sending prompts to the LLM  → src/llm/

Design Principles Applied:
--------------------------
    SRP  — RAG layer does one thing: retrieval.
    DIP  — LLM doesn't know where context comes from; it receives plain strings.
    OCP  — Vector DB backend, retrieval strategy, and filters are swappable
           without touching the LLM or analysis layers.

NOTE (Phase 7.1):
-----------------
    This package currently contains DESIGN STUBS ONLY.
    No FAISS code, no embedding calls, and no LLM modifications are made here yet.
    Implementation begins in Phase 7.2.
"""

from src.rag.embedder import EMBEDDING_DIM, MODEL_NAME, EmbeddingModel
from src.rag.models import RagNewsMetadata
from src.rag.faiss_store import FAISSStore
from src.rag.retriever import RAGRetriever, RetrievalResult

__all__ = [
    # Phase 7.1 — design stubs
    "RAGRetriever",
    "RetrievalResult",
    # Phase 7.2 — embedding layer
    "EmbeddingModel",
    "MODEL_NAME",
    "EMBEDDING_DIM",
    # Phase 7.3 — FAISS storage & retrieval
    "RagNewsMetadata",
    "FAISSStore",
]
