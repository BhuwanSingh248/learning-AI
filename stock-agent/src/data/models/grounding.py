from pydantic import BaseModel

class GroundingDecision(BaseModel):
    """
    Represents the output of the grounding checks.
    Tracks whether retrieval relevance is sufficient or if the pipeline should trigger a safe refusal.
    """
    is_grounded: bool          # True to proceed with LLM reasoning; False to block and refuse
    reason: str                 # Descriptive explanation of why validation succeeded or failed
    confidence_score: float     # Quantitative score of validation strength (e.g. best reranker score)
