"""Optional offline fallback client for local Ollama models."""

import json
import logging
from typing import Any

import requests

from src.packcheck.config import OLLAMA_BASE_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)


class OllamaClient:
    """Offline local LLM client using Ollama REST API."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def is_available(self) -> bool:
        """Check if local Ollama daemon is running."""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=1.5)
            return r.status_code == 200
        except Exception:
            return False

    def generate_json(self, prompt: str, content: str) -> dict[str, Any] | None:
        """Call Ollama with JSON formatting."""
        if not self.is_available():
            return None

        try:
            payload = {
                "model": self.model,
                "prompt": f"{prompt}\n\n{content}",
                "format": "json",
                "stream": False,
            }
            res = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60,
            )
            if res.status_code == 200:
                data = res.json()
                response_str = data.get("response", "")
                return json.loads(response_str)
        except Exception as e:
            logger.warning("Ollama generation failed: %s", e)

        return None
