from abc import ABC, abstractmethod
from typing import Optional

class LLMProvider(ABC):
    """
    Abstract interface for LLM execution providers.
    Allows swappable backends (Ollama, OpenAI, Anthropic, Gemini, etc.)
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        format: Optional[str] = None,
        timeout_seconds: int = 120
    ) -> str:
        """
        Sends a prompt to the LLM provider and retrieves the generated response.
        """
        pass
