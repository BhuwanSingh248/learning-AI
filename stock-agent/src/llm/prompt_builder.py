"""
Prompt Builder Module

Responsible for constructing structured prompts for the LLM based on 
engineered financial signals. Enforces strict input layouts and output formatting
expectations to minimize LLM hallucinations.
"""

import os
from src.analysis.signals import CombinedMarketSignal
from src.llm.models import PromptPayload


class PromptBuilder:
    """
    Constructs deterministic prompts for financial reasoning.
    """

    @staticmethod
    def load_system_prompt(version: str = "v1") -> str:
        """
        Loads the system prompt text from the corresponding version file.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "prompts", f"system_{version}.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"System prompt version file not found: system_{version}.txt")

    @staticmethod
    def build_recommendation_prompt(query: str, symbol: str, context_text: str, version: str = "v1") -> PromptPayload:
        """
        Constructs a PromptPayload containing the system prompt and structured user prompt.
        """
        system_prompt = PromptBuilder.load_system_prompt(version)
        
        user_prompt = (
            f"Stock: {symbol.upper()}\n"
            f"Question: {query}\n\n"
            f"--- START OF CONTEXT ---\n"
            f"{context_text}\n"
            f"--- END OF CONTEXT ---\n"
        )
        
        return PromptPayload(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

    @staticmethod
    def build_financial_reasoning_prompt(signals: CombinedMarketSignal, context_text: str = "") -> str:
        """
        Creates a structured prompt from combined market signals.
        
        Args:
            signals: The unified signal payload containing trend, momentum, sentiment, etc.
            context_text: Optional retrieved news context from the RAG layer.
            
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
        
        if context_text:
            data_context += f"\n\n--- RELEVANT NEWS CONTEXT ---\n{context_text}\n--- END OF NEWS CONTEXT ---\n"

        instructions = (
            "You are a professional financial analyst.\n"
            "Based ONLY on the provided data signals and context above, determine whether the "
            "stock is presently Bullish, Bearish, or Neutral.\n\n"
            "IMPORTANT RULES:\n"
            "1. Prioritize signals first. The signals represent structured quantitative truth.\n"
            "2. Use the news context as supporting evidence only.\n"
            "3. If context is missing or weak, fall back purely to signals.\n"
            "4. Mention uncertainty if there are conflicting signals vs news.\n"
            "5. Do not assume any external information and do not hallucinate data.\n"
            "Keep your reasoning concise and strictly tied to the signals and context provided.\n\n"
            "You MUST format your output exactly as follows:\n\n"
            "Decision: (Bullish / Bearish / Neutral)\n\n"
            "Reason:\n"
            "- [Point 1]\n"
            "- [Point 2]\n"
            "- [Point 3]"
        )

        final_prompt = f"--- START OF DATA ---\n{data_context}\n--- END OF DATA ---\n\n{instructions}"
        return final_prompt

    @staticmethod
    def build_custom_query_prompt(query: str, context_text: str) -> str:
        """
        Creates a structured prompt from custom user queries and news context.
        """
        instructions = (
            "You are a professional financial analyst.\n"
            f"Answer the user's question: '{query}'\n"
            "Based ONLY on the provided news context below. Do not use any external information or assumptions.\n"
            "Cite the source chunks using their bracketed numbers (e.g. [1], [2]) when referencing facts.\n"
            "If the context does not contain enough information to answer the question, state that clearly.\n"
            "Keep your answer concise and directly supported by the context.\n"
        )
        final_prompt = f"--- START OF CONTEXT ---\n{context_text}\n--- END OF CONTEXT ---\n\n{instructions}"
        return final_prompt

