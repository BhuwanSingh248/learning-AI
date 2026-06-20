from pydantic import BaseModel, Field

class DebugRetrievalRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g. INFY, AAPL)")
    query: str = Field(..., description="Search query string")
    top_k: int = Field(10, description="Number of candidate chunks to fetch")

class DebugRerankRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g. INFY, AAPL)")
    query: str = Field(..., description="Query string used for cross-encoder scoring")
    top_k: int = Field(10, description="Number of sorted chunks to return")

class DebugGroundingRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g. INFY, AAPL)")
    query: str = Field(..., description="Query string")
    top_k: int = Field(10, description="Number of candidate chunks")

class RetrievedChunkResponse(BaseModel):
    chunk_id: str
    symbol: str
    source_id: str
    timestamp: str | None = None
    chunk_text: str

class DebugRetrievalResponse(BaseModel):
    faiss_results: list[RetrievedChunkResponse]
    bm25_results: list[RetrievedChunkResponse]
    merged_results: list[RetrievedChunkResponse]

from typing import Any
from src.metrics.models import PipelineMetrics

class RerankedChunkResponse(BaseModel):
    chunk_id: str
    score: float
    chunk_text: str

class DebugRerankResponse(BaseModel):
    reranked_chunks: list[RerankedChunkResponse]

class DebugGroundingResponse(BaseModel):
    is_grounded: bool
    confidence_score: float
    reason: str
    candidate_count: int
    best_score: float
    average_score: float

class DebugAnalyzeResponse(BaseModel):
    prompt: str
    recommendation: Any
    metrics: PipelineMetrics
