from pydantic import BaseModel
from typing import List, Optional
from src.data.models.grounding import GroundingDecision

class Citation(BaseModel):
    """
    A lightweight, serializable model representing an evidence citation.
    This is passed back to the client in the API response to prove the source of reasoning.
    """
    citation_id: int        # Mapped to the bracketed numbers in the prompt (e.g. [1])
    chunk_id: str           # Unique chunk database identifier (e.g. "Bloomberg_AAPL_0")
    source_id: str          # Source name (e.g. "Reuters", "Bloomberg")
    timestamp: str          # Raw date/time string of the article
    text_preview: str       # Short summary or snippet of the text (e.g., first 150 chars)

class CitationContext(BaseModel):
    """
    The value object returned by ContextBuilder containing the combined LLM prompt text
    and the list of serializable citation records.
    """
    formatted_text: str                               # The context text injected into the LLM prompt
    citations: List[Citation]                         # The serialized citations list for API output
    grounding: Optional[GroundingDecision] = None     # Grounding decision of the pipeline


    @property
    def formatted_context(self) -> str:
        """
        Backward-compatible property mapping formatted_text to formatted_context.
        """
        return self.formatted_text

    @property
    def context_items(self) -> List[dict]:
        """
        Backward-compatible property mapping citations back to raw dict context items.
        """
        return [
            {
                "title": f"Context for {c.source_id}",
                "summary": c.text_preview,
                "source": c.source_id,
                "timestamp": c.timestamp,
                "relevance_score": 0.90
            }
            for c in self.citations
        ]

