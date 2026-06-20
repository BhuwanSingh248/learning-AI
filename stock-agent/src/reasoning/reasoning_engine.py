import json
from typing import List, Optional
from src.config.logger import setup_logger
from src.llm.llm_client import LLMClient
from src.llm.prompt_builder import PromptBuilder
from src.metrics import MetricsCollector
from src.reasoning.models import RecommendationResponse, RecommendationType

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
        refusal_reason: Optional[str] = None
    ) -> RecommendationResponse:
        """
        Executes prompt construction and model inference to produce a validated
        RecommendationResponse object. Enforces safe fallbacks on grounding gate failures or JSON errors.
        """
        logger.info("ReasoningEngine | Making structured decision for %s", symbol)
        
        # 1. Grounding Integration (Step 2.3.8)
        if not is_grounded:
            logger.warning("ReasoningEngine | Grounding refusal triggered for %s. Bypassing LLM call.", symbol)
            reasoning_str = "Grounding failed. Insufficient evidence available to answer this question reliably."
            if refusal_reason:
                reasoning_str += f" Details: {refusal_reason}"
            return RecommendationResponse(
                recommendation=RecommendationType.INSUFFICIENT_DATA,
                confidence=0.0,
                reasoning=reasoning_str,
                citations=[]
            )

        # 2. Build structured prompt (v1 system and user payload)
        if metrics:
            metrics.start_stage("prompt_build")
        payload = PromptBuilder.build_recommendation_prompt(query, symbol, context_text)
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

        # 4. JSON Parsing & Validation Layer
        recommendation = RecommendationType.INSUFFICIENT_DATA
        confidence = 0.0
        reasoning = "Unable to parse model response."
        citations = []

        try:
            parsed = json.loads(raw_response)
            
            # Recommendation validation (Step 2.3.5)
            rec_str = parsed.get("recommendation", "").upper().strip()
            if rec_str in [rt.value for rt in RecommendationType]:
                recommendation = RecommendationType(rec_str)
            else:
                logger.warning("ReasoningEngine | Received invalid recommendation '%s'. Defaulting to INSUFFICIENT_DATA.", rec_str)
            
            # Confidence validation & clamping (Step 2.3.6)
            try:
                raw_conf = float(parsed.get("confidence", 0.0))
                confidence = max(0.0, min(1.0, raw_conf))
            except (ValueError, TypeError):
                confidence = 0.0
                
            reasoning = parsed.get("reasoning", str(parsed))
            
            # Citations validation (Step 2.3.7)
            raw_citations = parsed.get("citations", [])
            valid_citations = []
            if isinstance(raw_citations, list):
                allowed_ids = available_citation_ids or []
                for cit in raw_citations:
                    try:
                        cit_int = int(cit)
                        if cit_int in allowed_ids:
                            valid_citations.append(cit_int)
                        else:
                            logger.warning("ReasoningEngine | Hallucinated citation %d filtered out.", cit_int)
                    except (ValueError, TypeError):
                        continue
            citations = valid_citations

        except json.JSONDecodeError as parse_err:
            logger.error("ReasoningEngine | JSON decoding failed: %s", parse_err)
            reasoning = f"Unable to parse model response. Raw response: {raw_response[:200]}"
        except Exception as err:
            logger.error("ReasoningEngine | Unexpected validation error: %s", err)
            reasoning = f"An unexpected parsing validation error occurred: {err}"

        return RecommendationResponse(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            citations=citations
        )
