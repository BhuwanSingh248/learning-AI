"""
Reasoning Module

Acts as the end-to-end bridge between quantitative signals and LLM outputs.
Takes CombinedMarketSignals, queries the LLM, and strictly parses the string 
results into a structured JSON-friendly Decision model.
"""

import re
from dataclasses import dataclass

from src.analysis.signals import CombinedMarketSignal
from src.llm.llm_client import LLMClient
from src.llm.prompt_builder import PromptBuilder
from src.config.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class LLMDecision:
    """
    A strictly structured recommendation decision.
    """
    symbol: str
    decision: str  # "Bullish", "Bearish", "Neutral"
    reason: str    # The reasoning bullet points from the model.


class ReasoningEngine:
    """
    Orchestrates prompting, requesting, and parsing the LLM pipeline.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Args:
            llm_client: Injected LLM connection (DIP).
        """
        self.llm_client = llm_client

    def make_decision(self, signals: CombinedMarketSignal) -> LLMDecision:
        """
        Full reasoning pipeline: Signals -> Prompt -> LLM -> Structured Decision.
        """
        logger.info("ReasoningEngine | Making decision for %s", signals.symbol)
        
        # 1. Generate Prompt
        prompt = PromptBuilder.build_financial_reasoning_prompt(signals)
        
        # 2. Query LLM
        raw_response = self.llm_client.generate_response(prompt)
        
        # 3. Parse Structurally
        return self._parse_response(raw_response, signals.symbol)

    def _parse_response(self, text: str, symbol: str) -> LLMDecision:
        """
        Extracts the Decision and Reason fields securely from raw text output.
        Safeguards included ensuring 'Neutral' fallbacks on crashes.
        """
        decision, reason = "Neutral", "Internal fallback generated."

        try:
            # Look for Decision: Bullish/Bearish/Neutral
            decision_match = re.search(r"Decision:\s*([a-zA-Z]+)", text, re.IGNORECASE)
            if decision_match:
                extracted = decision_match.group(1).capitalize()
                if extracted in ["Bullish", "Bearish", "Neutral"]:
                    decision = extracted
                else:
                    logger.warning("ReasoningEngine | Found invalid decision type '%s'. Defaulting to Neutral.", extracted)
            else:
                logger.warning("ReasoningEngine | Could not extract strict decision pattern.")

            # Look for Reason: block (everything after it)
            reason_match = re.search(r"Reason:\s*(.*)", text, re.IGNORECASE | re.DOTALL)
            if reason_match:
                reason_raw = reason_match.group(1).strip()
                if reason_raw:
                    reason = reason_raw
            
            # If completely unparseable, keep raw text in reason as emergency logging
            if decision == "Neutral" and not reason_match:
                if text.startswith("Error:"):
                     reason = text
                else:
                     reason = f"Unparseable AI output snippet: {text[:150]}..."

        except Exception as e:
            logger.error("ReasoningEngine | Critical Parsing Error: %s", e)
            reason = "A systemic parsing error occurred."

        return LLMDecision(
            symbol=symbol,
            decision=decision,
            reason=reason
        )
