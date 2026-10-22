"""Google Gemini API client with disk caching, rate limiting, and structured output."""

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from src.packcheck.config import (
    CACHE_DIR,
    GEMINI_API_KEY,
    GEMINI_FALLBACK_MODEL,
    GEMINI_MODEL,
    GEMINI_RPM,
)

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """Simple rate limiter ensuring requests stay within free tier RPM limits."""

    def __init__(self, rpm: int = 10):
        self.rpm = max(1, rpm)
        self.interval = 60.0 / self.rpm
        self.last_call_time = 0.0

    def wait_for_slot(self) -> None:
        """Block if needed to respect the minimum interval between requests."""
        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self.last_call_time = time.time()


class GeminiClient:
    """Production-grade client for Google Gemini API with disk caching and graceful fallback."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        cache_dir: Path | str | None = None,
    ):
        self.api_key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model = model or GEMINI_MODEL
        self.fallback_model = GEMINI_FALLBACK_MODEL
        self.cache_dir = Path(cache_dir or CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.limiter = TokenBucketRateLimiter(rpm=GEMINI_RPM)
        self._client: Any = None

    def is_available(self) -> bool:
        """Check if client has an API key configured."""
        return bool(
            self.api_key and self.api_key.strip() and self.api_key != "your_gemini_api_key_here"
        )

    def _get_client(self) -> Any:
        if self._client is None:
            if not self.is_available():
                raise ValueError("GEMINI_API_KEY is not configured. Set GEMINI_API_KEY in .env.")
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _cache_key(self, prompt: str, content: str, model: str) -> str:
        data = f"{model}:::{prompt}:::{content}".encode()
        return hashlib.sha256(data).hexdigest()

    def _read_cache(self, key: str) -> dict[str, Any] | None:
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("Failed to read cache file %s: %s", cache_file, e)
        return None

    def _write_cache(self, key: str, data: dict[str, Any]) -> None:
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning("Failed to write cache file %s: %s", cache_file, e)

    def generate_json(
        self,
        prompt: str,
        content: str,
        image_bytes: bytes | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any] | None:
        """Call Gemini to generate structured JSON output with disk caching and retry."""
        cache_key = self._cache_key(prompt, content, self.model)
        cached = self._read_cache(cache_key)
        if cached is not None:
            return cached

        if not self.is_available():
            logger.info("Gemini API key not configured; skipping semantic call.")
            return None

        client = self._get_client()

        models_to_try = [self.model, self.fallback_model]
        last_error = None

        for cur_model in models_to_try:
            for attempt in range(max_retries):
                try:
                    self.limiter.wait_for_slot()

                    contents: list[Any] = [f"{prompt}\n\n{content}"]
                    if image_bytes:
                        from google.genai import types

                        contents.append(
                            types.Part.from_bytes(data=image_bytes, mime_type="image/png")
                        )

                    response = client.models.generate_content(
                        model=cur_model,
                        contents=contents,
                        config={"response_mime_type": "application/json"},
                    )

                    text_out = response.text
                    if text_out:
                        # Parse JSON from response
                        parsed = json.loads(text_out)
                        self._write_cache(cache_key, parsed)
                        return parsed

                except Exception as e:
                    last_error = e
                    logger.warning(
                        "Gemini request failed (model=%s, attempt=%d/%d): %s",
                        cur_model,
                        attempt + 1,
                        max_retries,
                        e,
                    )
                    time.sleep(1.5 * (attempt + 1))  # Exponential backoff

        logger.error("All Gemini retries exhausted: %s", last_error)
        return None

    def generate_text(
        self,
        prompt: str,
        content: str,
        max_retries: int = 2,
    ) -> str | None:
        """Call Gemini for free-form text response (used for Q&A)."""
        cache_key = self._cache_key(prompt, content, f"{self.model}_text")
        cached = self._read_cache(cache_key)
        if cached is not None and "answer" in cached:
            return str(cached["answer"])

        if not self.is_available():
            return None

        client = self._get_client()
        for attempt in range(max_retries):
            try:
                self.limiter.wait_for_slot()
                response = client.models.generate_content(
                    model=self.model,
                    contents=f"{prompt}\n\n{content}",
                )
                if response.text:
                    self._write_cache(cache_key, {"answer": response.text})
                    return response.text
            except Exception as e:
                logger.warning("Gemini text call failed (attempt %d): %s", attempt + 1, e)
                time.sleep(1.5 * (attempt + 1))

        return None
