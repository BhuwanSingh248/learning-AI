"""
Agent Orchestration Layer

Coordinates the entire AI stock market analysis pipeline. Iterates over 
multiple stock symbols, computes signals, queries the LLM Reasoning engine, 
and ranks all outcomes into a finalized output.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.config.logger import setup_logger
from src.data.services.data_service import DataService
from src.processing.data_validator import DataValidator
from src.analysis.market_analyzer import MarketAnalyzer
from src.reasoning.reasoning_engine import ReasoningEngine
from src.reasoning.models import RecommendationResponse
from src.rag.retriever import RAGRetriever
from src.rag.indexer import NewsIndexer

import asyncio
from src.config.database import AsyncSessionLocal
from src.metrics import MetricsCollector, PipelineMetrics

logger = setup_logger(__name__)


@dataclass(frozen=True)
class RankedSuggestion:
    """Represents a final scored and reasoned recommendation for a single asset."""
    symbol: str
    score: float
    decision: str
    reason: str
    signal_breakdown: Dict[str, Any] | None = None
    rag: Dict[str, Any] | None = None
    prediction: Dict[str, Any] | None = None
    metrics: PipelineMetrics | None = None



class StockAgent:
    """
    The main Orchestrator that bridges Data, Processing, Analysis, and LLM Logic.
    """

    def __init__(self, data_service: DataService, reasoning_engine: ReasoningEngine, rag_retriever: RAGRetriever | None = None, news_indexer: Optional[NewsIndexer] = None):
        """
        Args:
            data_service: Configured data service instance (DIP).
            reasoning_engine: Configured LLM reasoning instance (DIP).
            rag_retriever: Configured RAG retriever for LLM context enrichment.
        """
        self.data_service = data_service
        self.reasoning_engine = reasoning_engine
        self.rag_retriever = rag_retriever
        self.news_indexer = news_indexer

    async def analyze_stocks(self, symbols: List[str], lookback_days: int = 90) -> Dict[str, Any]:
        """
        Runs the full analysis pipeline for a list of symbols and ranks them.
        
        Args:
            symbols: List of stock ticker symbols (e.g., ["AAPL", "MSFT"]).
            lookback_days: Depth of historical price data to fetch.
            
        Returns:
            Dictionary containing a list of ranked suggestions.
        """
        logger.info("StockAgent | Beginning analysis for %d symbols.", len(symbols))
        
        suggestions: List[RankedSuggestion] = []

        for symbol in symbols:
            metrics = MetricsCollector()
            metrics.start_stage("total")
            try:
                # 1. Fetch Raw Data
                raw_prices = self.data_service.get_price_data(symbol, lookback_days)
                raw_news = self.data_service.get_news(symbol)
                raw_actions = self.data_service.get_corporate_actions(symbol)
                
                # If we couldn't even retrieve price data, skip safely to avoid crashes
                if not raw_prices:
                    logger.warning("StockAgent | Failed to retrieve price data for %s. Skipping.", symbol)
                    continue

                # 2. Process and Standardize
                clean_prices = DataValidator.clean_price_data(raw_prices)
                clean_news = DataValidator.clean_news_data(raw_news)
                clean_actions = DataValidator.clean_corporate_actions(raw_actions)

                # Need clean prices to proceed with math
                if clean_prices is None or clean_prices.empty:
                     logger.warning("StockAgent | Cleaned price data was empty for %s. Skipping.", symbol)
                     continue
                
                # 2.a. Index news into FAISS (Must happen before RAG retrieval)
                if self.news_indexer and raw_news:
                    async with AsyncSessionLocal() as session:
                        await self.news_indexer.index_news(symbol, raw_news, session)

                # 3. Generate Signals
                signals = MarketAnalyzer.generate_signals(
                    symbol=symbol,
                    clean_prices=clean_prices,
                    clean_news=clean_news,
                    clean_actions=clean_actions
                )

                # 4. Generate AI Decision
                context_text = ""
                context_items = []
                grounding_decision = None
                available_citation_ids = []
                if self.rag_retriever:
                    try:
                        async def _fetch():
                            async with AsyncSessionLocal() as session:
                                return await self.rag_retriever.retrieve(symbol, session, top_k=5, metrics=metrics)
                        
                        res = await _fetch()
                        context_text = res.formatted_context
                        context_items = res.context_items
                        available_citation_ids = [c.citation_id for c in res.citations]
                        if hasattr(res, "grounding") and res.grounding:
                            grounding_decision = res.grounding
                    except Exception as e:
                        logger.warning("StockAgent | Failed to retrieve RAG context for %s: %s", symbol, e)

                is_grounded = grounding_decision.is_grounded if grounding_decision else True
                refusal_reason = grounding_decision.reason if grounding_decision else "Grounding failed."
                
                query = f"Based on market signals (Trend: {signals.price_signals.trend}, Momentum: {signals.price_signals.momentum}, Sentiment: {signals.news_signals.sentiment_score}, Event Score: {signals.event_signals.event_score}), should I buy, hold, or sell {symbol}?"
                
                llm_decision = self.reasoning_engine.make_decision(
                    symbol=symbol,
                    query=query,
                    context_text=context_text,
                    is_grounded=is_grounded,
                    available_citation_ids=available_citation_ids,
                    metrics=metrics,
                    refusal_reason=refusal_reason,
                    grounding_confidence_score=grounding_decision.confidence_score if grounding_decision else 0.0
                )

                # 5. Calculate Ranking Score 
                # Formula: (momentum * 0.4) + (sentiment * 0.4) + (event_score * 0.2)
                score = (signals.price_signals.momentum * 0.4) + \
                        (signals.news_signals.sentiment_score * 0.4) + \
                        (signals.event_signals.event_score * 0.2)
                
                # Build Signal Breakdown
                signal_breakdown = {
                    "trend": signals.price_signals.trend,
                    "momentum": signals.price_signals.momentum,
                    "volatility": signals.price_signals.volatility,
                    "sentiment_score": signals.news_signals.sentiment_score,
                    "event_score": signals.event_signals.event_score
                }

                # Build RAG Debug Info
                rag_info = {
                    "enabled": bool(self.rag_retriever),
                    "query": f"Recent context and news updates for {symbol}" if self.rag_retriever else None,
                    "retrieval_strategy": "similarity_search" if self.rag_retriever else None,
                    "top_k": 5 if self.rag_retriever else None,
                    "embedding_model": "all-MiniLM-L6-v2" if self.rag_retriever else None,
                    "vector_dimension": 384 if self.rag_retriever else None,
                    "index_type": "flat_l2" if self.rag_retriever else None,
                    "fallback_used": not bool(context_items) if self.rag_retriever else False,
                    "context_preview": context_text[:200] + "..." if context_text else None,
                    "context_items": context_items
                }

                # Build Prediction Meta
                prediction_meta = {
                    "horizon": "short_term",
                    "rank_bucket": "top_candidate" if score > 0.6 else ("neutral" if score >= 0.4 else "low_candidate"),
                    "confidence": round(abs(score), 2),
                    "expected_direction": "bullish" if score > 0.6 else ("neutral" if score >= 0.4 else "bearish")
                }

                metrics.end_stage("total")
                symbol_metrics = metrics.get_metrics()
                symbol_metrics.grounded = is_grounded
                
                # Emit structured logs for Langfuse / monitoring
                logger.info(
                    "[METRICS] Symbol=%s Total=%.1fms Retrieval=%.1fms Reranker=%.1fms Grounding=%.1fms LLM=%.1fms Grounded=%s",
                    symbol,
                    symbol_metrics.total_duration_ms,
                    symbol_metrics.retrieval_duration_ms,
                    symbol_metrics.reranker_duration_ms,
                    symbol_metrics.grounding_duration_ms,
                    symbol_metrics.llm_duration_ms,
                    "True" if symbol_metrics.grounded else "False"
                )

                suggestions.append(RankedSuggestion(
                    symbol=symbol,
                    score=round(score, 4),
                    decision=llm_decision.recommendation.value,
                    reason=llm_decision.reasoning,
                    signal_breakdown=signal_breakdown,
                    rag=rag_info,
                    prediction=prediction_meta,
                    metrics=symbol_metrics
                ))

                logger.debug("StockAgent | Successfully analyzed %s. Score: %.3f", symbol, score)

            except Exception as e:
                logger.error("StockAgent | Exception failed pipeline for symbol %s: %s", symbol, e)
                # DO NOT crash the entire system over one failing stock.

        # 6. Rank stocks by score descending
        suggestions.sort(key=lambda x: x.score, reverse=True)

        return {
            "suggestions": [
                {
                    "symbol": s.symbol,
                    "score": s.score,
                    "decision": s.decision,
                    "reason": s.reason,
                    "signal_breakdown": s.signal_breakdown,
                    "rag": s.rag,
                    "prediction": s.prediction,
                    "metrics": s.metrics.model_dump() if s.metrics else None
                }
                for s in suggestions
            ]
        }
