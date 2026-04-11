"""
Prompt Builder Module

Responsible for constructing structured prompts for the LLM based on 
engineered financial signals. Enforces strict input layouts and output formatting
expectations to minimize LLM hallucinations.
"""

from src.analysis.signals import CombinedMarketSignal


class PromptBuilder:
    """
    Constructs deterministic prompts for financial reasoning.
    """

    @staticmethod
    def build_financial_reasoning_prompt(signals: CombinedMarketSignal) -> str:
        """
        Creates a structured prompt from combined market signals.
        
        Args:
            signals: The unified signal payload containing trend, momentum, sentiment, etc.
            
        Returns:
            A formatted prompt string ready to be sent to the LLM.
        """
        # Formulate a structured string based on inputs
        data_context = (
            f"Stock: {signals.symbol}\n"
            f"Trend: {signals.price_signals.trend.capitalize()}\n"
            f"Momentum: {signals.price_signals.momentum}\n"
            f"Sentiment: {signals.news_signals.sentiment_score}\n"
            f"Event Score: {signals.event_signals.event_score}\n"
        )

        instructions = (
            "You are a professional financial analyst.\n"
            "Based ONLY on the provided data signals above, determine whether the "
            "stock is presently Bullish, Bearish, or Neutral.\n"
            "Do not assume any external information. Do not hallucinate data. "
            "Keep your reasoning concise and strictly tied to the signals provided.\n\n"
            "You MUST format your output exactly as follows:\n\n"
            "Decision: (Bullish / Bearish / Neutral)\n\n"
            "Reason:\n"
            "- [Point 1]\n"
            "- [Point 2]\n"
            "- [Point 3]"
        )

        final_prompt = f"--- START OF DATA ---\n{data_context}\n--- END OF DATA ---\n\n{instructions}"
        return final_prompt
