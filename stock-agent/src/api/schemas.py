"""
API Schemas

Defines the Input/Output Pydantic contracts for the HTTP Application layer.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SuggestRequest(BaseModel):
    """Payload requested by the user to analyze stocks."""
    symbols: List[str] = Field(..., description="List of stock tickers (e.g., ['AAPL', 'MSFT'])")
    lookback_days: int = Field(90, description="Number of days to analyze historically.")


class SuggestionItem(BaseModel):
    """Payload representing a single stock's analysis result."""
    symbol: str
    score: float
    decision: str
    reason: str


class SuggestResponse(BaseModel):
    """Full HTTP response returned to the client."""
    suggestions: List[SuggestionItem]
