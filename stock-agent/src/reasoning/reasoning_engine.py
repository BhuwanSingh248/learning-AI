import json
from typing import List, Optional
from src.config.logger import setup_logger
from src.llm.llm_client import LLMClient
from src.llm.prompt_builder import PromptBuilder
from src.metrics import MetricsCollector
from src.reasoning.models import RecommendationResponse, RecommendationType
from src.signals.models import Signal, SignalType
from src.signals.signal_engine import SignalEngine
from src.signals.scoring import SignalScorer, RecommendationCalculator, ConfidenceCalculator

logger = setup_logger(__name__)

class ReasoningEngine:
    """
    Orchestrates the prompt building, local LLM execution, JSON parsing, 
    and structured data validation for stock investment recommendations.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Args:
            llm_client: Injected LLM connection (DIP).
        """
        self.llm_client = llm_client

    def make_decision(
        self,
        symbol: str,
        query: str,
        context_text: str,
        is_grounded: bool,
        available_citation_ids: Optional[List[int]] = None,
        metrics: Optional[MetricsCollector] = None,
        refusal_reason: Optional[str] = None,
        grounding_confidence_score: Optional[float] = None
    ) -> RecommendationResponse:
        """
        Executes prompt construction and model inference to produce a validated
        RecommendationResponse object containing extracted signals, scored recommendation,
        and deterministic confidence. Enforces safe fallbacks on grounding gate failures or JSON errors.
        """
        logger.info("ReasoningEngine | Making structured decision for %s", symbol)
        allowed_citations = available_citation_ids or []
        
        # 1. Grounding Integration (Step 2.3.8 / 2.4.10 refusal)
        if not is_grounded:
            logger.warning("ReasoningEngine | Grounding refusal triggered for %s. Bypassing LLM call.", symbol)
            reasoning_str = "Grounding failed. Insufficient evidence available to answer this question reliably."
            if refusal_reason:
                reasoning_str += f" Details: {refusal_reason}"
            return RecommendationResponse(
                recommendation=RecommendationType.INSUFFICIENT_DATA,
                confidence=0.0,
                reasoning=reasoning_str,
                citations=[],
                signals=[]
            )

        # 2. Build structured prompt (v2 system and user payload)
        if metrics:
            metrics.start_stage("prompt_build")
        payload = PromptBuilder.build_recommendation_prompt(query, symbol, context_text, version="v2")
        if metrics:
            metrics.end_stage("prompt_build")

        # 3. Query LLM enforcing format="json"
        if metrics:
            metrics.start_stage("llm")
            metrics.set_model_name(self.llm_client.model_name)
        raw_response = self.llm_client.generate_response(
            prompt=payload.user_prompt,
            system=payload.system_prompt,
            format="json"
        )
        if metrics:
            metrics.end_stage("llm")

        # 4. JSON Parsing & Signal Extraction Layer
        extraction = SignalEngine.extract_signals(raw_response, allowed_citations)
        
        # 5. Signal Scoring Layer
        scored_signals = SignalScorer.score_signals(extraction.signals)
        
        # 6. Recommendation Threshold Calculation
        recommendation = RecommendationCalculator.calculate_recommendation(scored_signals)
        
        # 7. Confidence Calculation
        confidence = ConfidenceCalculator.calculate_confidence(scored_signals, grounding_confidence_score)
        
        # Extract unique citations referenced in signals
        cited_ids_set = set()
        for sig in scored_signals:
            cited_ids_set.update(sig.citation_ids)
        cited_ids = sorted(list(cited_ids_set))
        
        # Fallback to all citations if none were explicitly referenced but signals exist
        if not cited_ids and scored_signals:
            cited_ids = allowed_citations
            
        # 8. Record Signal Metrics (Step 2.4.9)
        if metrics:
            sig_count = len(scored_signals)
            pos_count = sum(1 for s in scored_signals if s.signal_type == SignalType.POSITIVE)
            neg_count = sum(1 for s in scored_signals if s.signal_type == SignalType.NEGATIVE)
            risk_count = sum(1 for s in scored_signals if s.signal_type == SignalType.RISK)
            
            metrics.set_metadata("signal_count", sig_count)
            metrics.set_metadata("positive_signal_count", pos_count)
            metrics.set_metadata("negative_signal_count", neg_count)
            metrics.set_metadata("risk_signal_count", risk_count)

        return RecommendationResponse(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=extraction.reasoning,
            citations=cited_ids,
            signals=scored_signals
        )
