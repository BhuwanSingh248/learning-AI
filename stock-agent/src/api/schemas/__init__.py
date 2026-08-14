"""
API Schemas

Defines the Input/Output Pydantic contracts for the HTTP Application layer.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator
from src.data.models import Citation
from src.metrics.models import PipelineMetrics


class SuggestRequest(BaseModel):
    """Payload requested by the user to analyze stocks."""
    symbols: List[str] = Field(..., description="List of stock tickers (e.g., ['AAPL', 'MSFT'])")
    lookback_days: int = Field(90, description="Number of days to analyze historically.")

    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, v: List[str]) -> List[str]:
        from src.config.settings import settings
        if not v:
            raise ValueError("The 'symbols' list cannot be empty.")
        if len(v) > settings.MAX_SYMBOLS:
            raise ValueError(f"Number of symbols exceeds budget limit of {settings.MAX_SYMBOLS}.")
        return v

    @field_validator("lookback_days")
    @classmethod
    def validate_lookback_days(cls, v: int) -> int:
        from src.config.settings import settings
        if v > settings.MAX_LOOKBACK_DAYS:
            raise ValueError(f"Lookback days exceeds budget limit of {settings.MAX_LOOKBACK_DAYS}.")
        return v


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

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, v: int) -> int:
        from src.config.settings import settings
        if v > settings.MAX_TOP_K:
            raise ValueError(f"top_k exceeds budget limit of {settings.MAX_TOP_K}.")
        return v

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        from src.config.settings import settings
        if len(v) > settings.MAX_QUERY_CHARS:
            raise ValueError(f"Query length exceeds character budget limit of {settings.MAX_QUERY_CHARS}.")
        return v


from src.reasoning.models import RecommendationType
from src.signals.models import Signal
from src.history.models import HistoricalMatch

class AnalyzeResponse(BaseModel):
    recommendation: RecommendationType
    confidence: float
    reasoning: str
    grounded: bool
    citations: List[Citation]
    signals: List[Signal] = Field(default_factory=list)
    historical_matches: List[HistoricalMatch] = Field(default_factory=list)
    diagnostics: Optional[dict] = None
    metrics: Optional[PipelineMetrics] = None


