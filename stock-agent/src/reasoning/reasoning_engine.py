import json
from typing import List, Optional, Any
from src.config.logger import setup_logger
from src.llm.llm_client import LLMClient
from src.llm.prompt_builder import PromptBuilder
from src.metrics import MetricsCollector
from src.reasoning.models import RecommendationResponse, RecommendationType
from src.signals.models import Signal, SignalType
from src.signals.signal_engine import SignalEngine
from src.signals.scoring import SignalScorer, RecommendationCalculator, ConfidenceCalculator
from src.history.models import HistoricalMatch

logger = setup_logger(__name__)

class ReasoningEngine:
    """
    Orchestrates the prompt building, local LLM execution, JSON parsing, 
    and structured data validation for stock investment recommendations,
    incorporating historical analogies and outcomes.
    """

    def __init__(self, llm_client: LLMClient, event_retriever: Optional[Any] = None, outcome_analyzer: Optional[Any] = None):
        """
        Args:
            llm_client: Injected LLM connection (DIP).
            event_retriever: Injected Historical Event Retriever (optional).
            outcome_analyzer: Injected Historical Outcome Analyzer (optional).
        """
        self.llm_client = llm_client
        self.event_retriever = event_retriever
        self.outcome_analyzer = outcome_analyzer

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
                signals=[],
                historical_matches=[]
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
        extracted_signals = extraction.signals
        
        # 5. Historical Analogy Learning Layer (Step 2.5.8)
        historical_matches = []
        historical_signals = []
        if self.event_retriever and self.outcome_analyzer:
            try:
                # Retrieve matching events (using query text for semantic comparison)
                matches = self.event_retriever.retrieve(query, top_k=1)
                for event, similarity in matches:
                    observed_outcome = self.outcome_analyzer.analyze_outcome(event, symbol)
                    historical_matches.append(HistoricalMatch(
                        event=event.title,
                        similarity=similarity,
                        observed_outcome=observed_outcome
                    ))
                    
                    # Compute signal score dynamically: impact_score * similarity
                    sig_score = float(round(event.impact_score * similarity, 2))
                    
                    # Map to positive, negative, or risk based on computed score
                    if sig_score < -0.5:
                        sig_type = SignalType.NEGATIVE
                    elif sig_score > 0.3:
                        sig_type = SignalType.POSITIVE
                    else:
                        sig_type = SignalType.RISK
                        
                    historical_signals.append(Signal(
                        signal_type=sig_type,
                        title=f"Historical Match: {event.title}",
                        description=f"Observed outcome: {observed_outcome}. Similarity: {similarity:.0%}",
                        score=sig_score,
                        citation_ids=[]
                    ))
            except Exception as err:
                logger.error("ReasoningEngine | Failed during historical lookup: %s", err)
        
        # Merge extracted signals with historical signals
        all_signals = extracted_signals + historical_signals
        
        # 6. Signal Scoring Layer
        scored_signals = SignalScorer.score_signals(all_signals)
        
        # 7. Recommendation Threshold Calculation
        recommendation = RecommendationCalculator.calculate_recommendation(scored_signals)
        
        # 8. Confidence Calculation
        confidence = ConfidenceCalculator.calculate_confidence(scored_signals, grounding_confidence_score)
        
        # Extract unique citations referenced in signals
        cited_ids_set = set()
        for sig in scored_signals:
            cited_ids_set.update(sig.citation_ids)
        cited_ids = sorted(list(cited_ids_set))
        
        # Fallback to all citations if none were explicitly referenced but signals exist
        if not cited_ids and scored_signals:
            cited_ids = allowed_citations
            
        # 9. Record Signal & Historical Metrics (Step 2.4.9 / 2.5.10)
        if metrics:
            sig_count = len(scored_signals)
            pos_count = sum(1 for s in scored_signals if s.signal_type == SignalType.POSITIVE)
            neg_count = sum(1 for s in scored_signals if s.signal_type == SignalType.NEGATIVE)
            risk_count = sum(1 for s in scored_signals if s.signal_type == SignalType.RISK)
            
            metrics.set_metadata("signal_count", sig_count)
            metrics.set_metadata("positive_signal_count", pos_count)
            metrics.set_metadata("negative_signal_count", neg_count)
            metrics.set_metadata("risk_signal_count", risk_count)
            
            # Historical metrics
            metrics.set_metadata("historical_matches_found", len(historical_matches))
            metrics.set_metadata("historical_signal_count", len(historical_signals))
            if historical_matches:
                avg_sim = sum(hm.similarity for hm in historical_matches) / len(historical_matches)
                metrics.set_metadata("average_similarity", float(round(avg_sim, 4)))
            else:
                metrics.set_metadata("average_similarity", 0.0)

        # Enhance reasoning with historical match context if matches found
        final_reasoning = extraction.reasoning
        if historical_matches:
            # Append historical context explaining why the decision is reinforced/impacted by analogies
            hm = historical_matches[0]
            final_reasoning = f"{final_reasoning.strip()} A similar event ({hm.event}) occurred previously and {hm.observed_outcome.lower()}."

        return RecommendationResponse(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=final_reasoning,
            citations=cited_ids,
            signals=scored_signals,
            historical_matches=historical_matches
        )
