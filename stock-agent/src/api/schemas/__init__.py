"""
API Schemas

Defines the Input/Output Pydantic contracts for the HTTP Application layer.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from src.data.models import Citation
from src.metrics.models import PipelineMetrics


class SuggestRequest(BaseModel):
    """Payload requested by the user to analyze stocks."""
    symbols: List[str] = Field(..., description="List of stock tickers (e.g., ['AAPL', 'MSFT'])")
    lookback_days: int = Field(90, description="Number of days to analyze historically.")


class SignalBreakdown(BaseModel):
    trend: str
    momentum: float
    volatility: float
    sentiment_score: float
    event_score: float


class RagContextItem(BaseModel):
    title: str
    summary: str
    source: str
    timestamp: str
    relevance_score: float


class RagDebugInfo(BaseModel):
    enabled: bool
    query: Optional[str] = None
    retrieval_strategy: Optional[str] = None
    top_k: Optional[int] = None
    embedding_model: Optional[str] = None
    vector_dimension: Optional[int] = None
    index_type: Optional[str] = None
    fallback_used: Optional[bool] = None
    context_preview: Optional[str] = None
    context_items: List[RagContextItem] = Field(default_factory=list)


class PredictionMeta(BaseModel):
    horizon: str
    rank_bucket: str
    confidence: float
    expected_direction: str


class SuggestionItem(BaseModel):
    """Payload representing a single stock's analysis result."""
    symbol: str
    score: float
    decision: str
    reason: str
    
    signal_breakdown: Optional[SignalBreakdown] = None
    rag: Optional[RagDebugInfo] = None
    prediction: Optional[PredictionMeta] = None
    metrics: Optional[PipelineMetrics] = None



class SuggestResponse(BaseModel):
    """Full HTTP response returned to the client."""
    suggestions: List[SuggestionItem]


class HealthCheckItem(BaseModel):
    status: str
    summary: str
    embedding_model: Optional[str] = None
    vector_dimension: Optional[int] = None
    index_type: Optional[str] = None
    top_k: Optional[int] = None
    retrieval_strategy: Optional[str] = None
    prompt_mode: Optional[str] = None


class HealthResponse(BaseModel):
    level: str
    summary: str
    details: str
    probe_target: str
    checks: Dict[str, HealthCheckItem]


class AnalyzeRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g. INFY, AAPL)")
    query: str = Field(..., description="User query driven stock analysis question")
    top_k: int = Field(10, description="Number of candidate chunks to fetch")


from src.reasoning.models import RecommendationType

class AnalyzeResponse(BaseModel):
    recommendation: RecommendationType
    confidence: float
    reasoning: str
    grounded: bool
    citations: List[Citation]
    diagnostics: Optional[dict] = None
    metrics: Optional[PipelineMetrics] = None


