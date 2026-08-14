from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from src.signals.models import Signal
from src.history.models import HistoricalMatch

class RecommendationType(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

class RecommendationResponse(BaseModel):
    """
    Structured response details holding parsed LLM recommendations.
    """
    recommendation: RecommendationType = Field(..., description="Actionable investment recommendation")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0")
    reasoning: str = Field(..., description="Reasoning text supporting decision")
    citations: List[int] = Field(..., description="Source citation IDs referenced as evidence")
    signals: List[Signal] = Field(default_factory=list, description="Extracted signal list supporting recommendation")
    historical_matches: List[HistoricalMatch] = Field(default_factory=list, description="List of matched historical analogies")

class ReasoningResult(BaseModel):
    """
    Result wrapper enclosing validation state, final parsed response, and original raw text.
    """
    success: bool = Field(..., description="Whether LLM parsing and schema validation succeeded")
    response: RecommendationResponse = Field(..., description="The parsed and validated recommendation data")
    raw_llm_response: str = Field(..., description="Original raw response string received from the LLM")
