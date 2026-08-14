"""
LLM Client Wrapper

Isolated module responsible for communication with the LLM (Mistral via Ollama).
Enforces the Dependency Inversion Principle — the rest of the application 
only interfaces with this wrapper, not directly with Ollama.
"""

import urllib.request
import urllib.error
import json

from src.config.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__)


class LLMClient:
    """
    A simple wrapper for local Ollama LLM queries.
    """

    def __init__(self, model_name: str = settings.LLM_MODEL, base_url: str = settings.OLLAMA_LOCAL_URL):
        """
        Initializes the LLM CLI interface parameters.
        
        Args:
            model_name: The name of the local Ollama model to invoke (e.g. "mistral").
            base_url: The base HTTP URL where Ollama is running.
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_endpoint = f"{self.base_url}/api/generate"

    def generate_response(self, prompt: str, system: str | None = None, format: str | None = None, timeout_seconds: int = 120) -> str:
        """
        Sends a prompt to the LLM and retrieves the text response by delegating
        to the unified OllamaProvider abstraction.
        """
        logger.debug("LLMClient | Sending prompt to %s (len: %d) via provider", self.model_name, len(prompt))
        from src.llm.providers.ollama import OllamaProvider
        provider = OllamaProvider(model_name=self.model_name, base_url=self.base_url)
        return provider._generate_sync(prompt, system, format, timeout_seconds)
