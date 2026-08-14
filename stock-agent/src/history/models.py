from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class HistoricalEvent(BaseModel):
    """
    Represents a major historical market event and its sector/stock return outcomes.
    """
    event_id: str = Field(..., description="Unique event identifier")
    title: str = Field(..., description="Short name of the event")
    description: str = Field(..., description="Detailed description of the event")
    event_date: str = Field(..., description="Date when the event occurred (YYYY-MM-DD)")
    sector: str = Field(..., description="Primary sector impacted by this event")
    impact_score: float = Field(..., description="Base macro impact score from -1.0 to 1.0")
    sector_outcomes: List[Dict[str, Any]] = Field(default_factory=list, description="List of sector-level average returns")
    stock_outcomes: List[Dict[str, Any]] = Field(default_factory=list, description="List of stock-specific returns")

class HistoricalMatch(BaseModel):
    """
    Structured model returned in API responses detailing a matched historical analogy.
    """
    event: str = Field(..., description="Title of the matched historical event")
    similarity: float = Field(..., description="Semantic similarity score from 0.0 to 1.0")
    observed_outcome: str = Field(..., description="Observed performance outcome of the asset/sector during that event")
