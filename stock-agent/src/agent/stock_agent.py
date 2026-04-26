"""
Agent Orchestration Layer

Coordinates the entire AI stock market analysis pipeline. Iterates over 
multiple stock symbols, computes signals, queries the LLM Reasoning engine, 
and ranks all outcomes into a finalized output.
"""

from typing import List, Dict, Any
from dataclasses import dataclass

from src.config.logger import setup_logger
from src.data.services.data_service import DataService
from src.processing.data_validator import DataValidator
from src.analysis.market_analyzer import MarketAnalyzer
from src.llm.reasoning import ReasoningEngine, LLMDecision
from src.rag.retriever import RAGRetriever

import asyncio
from src.config.database import AsyncSessionLocal

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


class StockAgent:
    """
    The main Orchestrator that bridges Data, Processing, Analysis, and LLM Logic.
    """

    def __init__(self, data_service: DataService, reasoning_engine: ReasoningEngine, rag_retriever: RAGRetriever | None = None):
        """
        Args:
            data_service: Configured data service instance (DIP).
            reasoning_engine: Configured LLM reasoning instance (DIP).
            rag_retriever: Configured RAG retriever for LLM context enrichment.
        """
        self.data_service = data_service
        self.reasoning_engine = reasoning_engine
        self.rag_retriever = rag_retriever

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
                if self.rag_retriever:
                    try:
                        async def _fetch():
                            async with AsyncSessionLocal() as session:
                                return await self.rag_retriever.retrieve(symbol, session, top_k=5)
                        
                        res = await _fetch()
                        context_text = res.formatted_context
                        context_items = res.context_items
                    except Exception as e:
                        logger.warning("StockAgent | Failed to retrieve RAG context for %s: %s", symbol, e)

                llm_decision: LLMDecision = self.reasoning_engine.make_decision(signals, context_text)

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

                suggestions.append(RankedSuggestion(
                    symbol=symbol,
                    score=round(score, 4),
                    decision=llm_decision.decision,
                    reason=llm_decision.reason,
                    signal_breakdown=signal_breakdown,
                    rag=rag_info,
                    prediction=prediction_meta
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
                    "prediction": s.prediction
                }
                for s in suggestions
            ]
        }
