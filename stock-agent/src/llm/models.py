from pydantic import BaseModel, Field
from typing import List

class RecommendationPrompt(BaseModel):
    """
    Structured model holding input variables needed to format the recommendation prompt.
    """
    symbol: str = Field(..., description="Stock symbol (e.g. INFY)")
    query: str = Field(..., description="User query driving the recommendation")
    context: str = Field(..., description="Grounded news text context retrieved from RAG")
    citations: List[int] = Field(default_factory=list, description="Ordered source chunk indexes")

class PromptPayload(BaseModel):
    """
    Constructed system and user prompt strings ready to be sent to the LLM.
    """
    system_prompt: str
    user_prompt: str

class RecommendationResponse(BaseModel):
    """
    Structured JSON response schema expected from the LLM.
    """
    recommendation: str = Field(..., description="Financial recommendation action (BUY, SELL, or HOLD)")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(..., description="Detailed text explanation of the recommendation")
    citations: List[int] = Field(..., description="Indices of the cited chunks supporting the recommendation")
