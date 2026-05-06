"""
Embedding Module
================

Phase 7.2 — RAG Integration: Embedding Layer

This is the SINGLE authoritative place where text is converted to vectors.
No other module in the codebase should produce embeddings independently.

Architecture Placement:
-----------------------
    News Text
        ↓
    EmbeddingModel          ← YOU ARE HERE
        ↓
    Vector (384-dim)
        ↓
    FAISS (Phase 7.3)

Responsibilities (SRP):
-----------------------
    ✅  Load the embedding model (once, on first use)
    ✅  Convert a single text string  → numpy float32 vector
    ✅  Convert a list of text strings → list of numpy float32 vectors
    ✅  Pre-format raw news fields (title + summary) into a single embedding string

NOT responsible for:
--------------------
    ❌  Storing or indexing vectors → Phase 7.3 (FAISS)
    ❌  Searching / retrieving      → src/rag/retriever.py
    ❌  Fetching news               → src/data/
    ❌  Building LLM prompts        → src/llm/

Design Principles Applied:
--------------------------
    SRP — EmbeddingModel does ONE thing: text → vector.
    DIP — Callers depend on the returned numpy array, not on the model internals.
          Swapping the model (e.g. to a larger one) only requires changing this file.
    OCP — Model name is injected at construction time, making it easy to upgrade
          without modifying the interface or any downstream code.

Consistency Rule (critical):
----------------------------
    ⚠️  The SAME EmbeddingModel instance (or at minimum the same model name)
        MUST be used at both:
          • Indexing time  (storing vectors in FAISS)
          • Query time     (searching FAISS for Top-K)
        Using different models breaks retrieval silently and is very hard to debug.

Chosen Model:
-------------
    all-MiniLM-L6-v2  (sentence-transformers)
        - Lightweight and fast
        - Good semantic understanding for short texts
        - Produces 384-dimensional float32 vectors
        - Matches FAISS index dimension configured in Phase 7.3
"""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer
from src.config.settings import settings
from src.config.logger import setup_logger

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL_NAME: str = settings.MODEL_NAME
"""
The model used for all embedding operations in this project.

⚠️  Do NOT change this value without re-indexing the entire FAISS store.
    Changing the model invalidates all previously stored vectors.
"""

EMBEDDING_DIM: int = settings.VECTOR_DIMENSION
"""
Output dimensionality of ``MODEL_NAME``.
FAISS index must be initialised with this exact value (Phase 7.3).
"""


# ---------------------------------------------------------------------------
# Embedding Model
# ---------------------------------------------------------------------------

class EmbeddingModel:
    """
    Wraps ``sentence-transformers`` to provide a stable, project-wide
    embedding interface.

    The underlying ``SentenceTransformer`` is loaded lazily on first use
    to avoid import-time cost when the class is imported but not used.

    Usage:
    ------
        model = EmbeddingModel()

        # Single text
        vector = model.embed_text("Apple reports strong Q2 earnings.")
        # vector.shape → (384,)

        # Batch of texts
        vectors = model.embed_batch(["Apple Q2 beat.", "Fed raises rates."])
        # vectors.shape → (2, 384)

        # From raw news fields (recommended)
        vector = model.embed_news("Apple beats earnings", "Revenue up 20%.")
    """

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        """
        Parameters
        ----------
        model_name : str
            HuggingFace / sentence-transformers model identifier.
            Defaults to ``all-MiniLM-L6-v2``.
            Override only for testing or future model upgrades.
        """
        self._model_name = model_name
        self._model: SentenceTransformer | None = None
        logger.debug("EmbeddingModel | Configured with model '%s' (lazy load)", model_name)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> SentenceTransformer:
        """
        Lazily loads the SentenceTransformer model on first call.
        Subsequent calls return the cached instance.
        """
        if self._model is None:
            logger.info("EmbeddingModel | Loading model '%s' …", self._model_name)
            self._model = SentenceTransformer(self._model_name)
            logger.info(
                "EmbeddingModel | Model loaded. Output dim = %d",
                self._model.get_sentence_embedding_dimension(),
            )
        return self._model

    @staticmethod
    def prepare_text(title: str, summary: str) -> str:
        """
        Combines news ``title`` and ``summary`` into a single string
        optimised for semantic embedding.

        Formatting both fields together gives the model richer context
        than embedding either field alone.

        Parameters
        ----------
        title : str
            The headline of the news article.
        summary : str
            A short description or body of the article.

        Returns
        -------
        str
            Formatted string ready to pass to :meth:`embed_text`.

        Example
        -------
        >>> EmbeddingModel.prepare_text("Apple beats expectations", "Revenue up 20%")
        'Title: Apple beats expectations. Summary: Revenue up 20%'
        """
        title = title.strip().rstrip(".")
        summary = summary.strip()
        return f"Title: {title}. Summary: {summary}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_text(self, text: str) -> np.ndarray:
        """
        Convert a single text string into a float32 embedding vector.

        Parameters
        ----------
        text : str
            Any plain-text string.  For news, prefer using
            :meth:`prepare_text` to combine title + summary first.

        Returns
        -------
        np.ndarray
            Shape ``(384,)``, dtype ``float32``.

        Raises
        ------
        ValueError
            If ``text`` is empty or whitespace-only.
        """
        text = text.strip()
        if not text:
            raise ValueError("EmbeddingModel.embed_text: 'text' must not be empty.")

        logger.debug("EmbeddingModel | Embedding single text (%d chars)", len(text))
        model = self._load()
        vector: np.ndarray = model.encode(text, convert_to_numpy=True)
        return vector.astype(np.float32)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """
        Convert a list of text strings into a 2-D float32 embedding matrix.

        Batch encoding is significantly faster than calling :meth:`embed_text`
        in a loop because sentence-transformers parallelises internally.

        Parameters
        ----------
        texts : list[str]
            One or more plain-text strings.

        Returns
        -------
        np.ndarray
            Shape ``(len(texts), 384)``, dtype ``float32``.

        Raises
        ------
        ValueError
            If ``texts`` is empty.
        """
        if not texts:
            raise ValueError("EmbeddingModel.embed_batch: 'texts' must not be empty.")

        logger.debug("EmbeddingModel | Embedding batch of %d texts", len(texts))
        model = self._load()
        matrix: np.ndarray = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return matrix.astype(np.float32)

    def embed_news(self, title: str, summary: str) -> np.ndarray:
        """
        Convenience wrapper: prepares then embeds a news article.

        Internally calls :meth:`prepare_text` followed by :meth:`embed_text`.

        Parameters
        ----------
        title : str
            News headline.
        summary : str
            News body / description.

        Returns
        -------
        np.ndarray
            Shape ``(384,)``, dtype ``float32``.

        Example
        -------
        >>> model = EmbeddingModel()
        >>> vec = model.embed_news("Apple Q2 earnings beat", "Revenue increased 20%")
        >>> vec.shape
        (384,)
        """
        text = self.prepare_text(title, summary)
        return self.embed_text(text)

    @property
    def dimension(self) -> int:
        """
        Return the output embedding dimension.

        Loads the model if it has not been loaded yet.
        Use this to validate FAISS index configuration in Phase 7.3.

        Returns
        -------
        int
            Should always be ``384`` for ``all-MiniLM-L6-v2``.
        """
        return self._load().get_sentence_embedding_dimension()
