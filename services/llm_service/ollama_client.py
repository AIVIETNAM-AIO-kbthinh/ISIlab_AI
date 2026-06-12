"""
LLM Service - Ollama Client
Async HTTP client for communicating with Ollama REST API.
"""

import logging
import time
from typing import Optional

import httpx

logger = logging.getLogger("llm_service.ollama_client")


class OllamaClient:
    """
    Async client for the Ollama REST API.
    
    Ollama API reference:
      - POST /api/chat   (multi-turn chat)
      - POST /api/generate (single-turn)
      - GET  /api/tags   (list models)
      - GET  /         (health check)
    """

    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "qwen3:8b"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self._client: Optional[httpx.AsyncClient] = None

    async def start(self):
        """Initialize the HTTP client."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout=300.0, connect=10.0),
        )

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()

    async def is_healthy(self) -> bool:
        """Check if Ollama is running."""
        try:
            resp = await self._client.get("/", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[dict]:
        """List available models in Ollama."""
        try:
            resp = await self._client.get("/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "name": m["name"],
                    "size": m.get("size"),
                    "modified_at": m.get("modified_at"),
                }
                for m in data.get("models", [])
            ]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    async def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> dict:
        """
        Send a chat completion request to Ollama.
        
        Args:
            messages: List of {"role": ..., "content": ...} dicts
            model: Model name override
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            dict with keys: text, model, generation_ms
        """
        model = model or self.default_model

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        t0 = time.perf_counter()

        try:
            resp = await self._client.post("/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

            generation_ms = (time.perf_counter() - t0) * 1000

            response_text = data.get("message", {}).get("content", "")

            logger.info(
                f"Chat response ({model}): {len(response_text)} chars, "
                f"{generation_ms:.0f}ms"
            )

            return {
                "text": response_text,
                "model": model,
                "generation_ms": round(generation_ms, 1),
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code} {e.response.text}")
            raise
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: 'ollama serve'"
            )
