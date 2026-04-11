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

logger = setup_logger(__name__)


class LLMClient:
    """
    A simple wrapper for local Ollama LLM queries.
    """

    def __init__(self, model_name: str = "mistral", base_url: str = "http://localhost:11434"):
        """
        Initializes the LLM CLI interface parameters.
        
        Args:
            model_name: The name of the local Ollama model to invoke (e.g. "mistral").
            base_url: The base HTTP URL where Ollama is running.
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_endpoint = f"{self.base_url}/api/generate"

    def generate_response(self, prompt: str, timeout_seconds: int = 120) -> str:
        """
        Sends a prompt to the LLM and retrieves the text response.
        
        Args:
            prompt: The text prompt to reason about.
            timeout_seconds: Amount of time to wait before falling back.
            
        Returns:
            The raw text response from the model, or a safe fallback on failure.
        """
        logger.debug("LLMClient | Sending prompt to %s (len: %d)", self.model_name, len(prompt))

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
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
                    logger.error("LLMClient | Received anomalous status code: %s", response.status)
                    return "Error: LLM service returned unexpected status code."

                response_data = json.loads(response.read().decode("utf-8"))
                output_text = response_data.get("response", "").strip()

                if not output_text:
                    logger.warning("LLMClient | Model returned an empty response.")
                    return "Error: LLM service returned empty response."
                
                return output_text

        except urllib.error.URLError as e:
            logger.error("LLMClient | Connection error communicating with Ollama: %s", e)
            return "Error: Cannot connect to LLM service."
        except TimeoutError:
            logger.error("LLMClient | Request timed out after %s seconds.", timeout_seconds)
            return "Error: LLM service request timed out."
        except Exception as e:
            logger.error("LLMClient | Unexpected failure: %s", e)
            return "Error: An unexpected error occurred while communicating with the LLM."
