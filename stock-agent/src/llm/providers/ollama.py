import urllib.request
import urllib.error
import json
import asyncio
from typing import Optional
from src.llm.providers.base import LLMProvider
from src.config.logger import setup_logger

logger = setup_logger(__name__)

class OllamaProvider(LLMProvider):
    """
    Concrete implementation of LLMProvider targeting a local Ollama service.
    """
    
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_endpoint = f"{self.base_url}/api/generate"

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        format: Optional[str] = None,
        timeout_seconds: int = 120
    ) -> str:
        """
        Non-blocking generate call wrapping the synchronous urllib query in asyncio.to_thread.
        """
        logger.debug("OllamaProvider | Generating response for %s", self.model_name)
        return await asyncio.to_thread(self._generate_sync, prompt, system, format, timeout_seconds)

    def _generate_sync(
        self,
        prompt: str,
        system: Optional[str],
        format: Optional[str],
        timeout_seconds: int
    ) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
        if format:
            payload["format"] = format
            
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.api_endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
                if response.status != 200:
                    logger.error("OllamaProvider | Unexpected HTTP status: %d", response.status)
                    return "Error: Ollama service returned unexpected status."
                response_data = json.loads(response.read().decode("utf-8"))
                return response_data.get("response", "").strip()
        except Exception as e:
            logger.error("OllamaProvider | Error communicating with Ollama: %s", e)
            return f"Error: Cannot connect to Ollama service. Details: {e}"
