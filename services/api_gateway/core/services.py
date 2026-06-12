"""
API Gateway - Service Clients
HTTP clients for communicating with ASR, LLM, and TTS microservices.
"""

import logging
from typing import Optional

import httpx

from core.config import Settings

logger = logging.getLogger("api_gateway.services")


class ServiceClients:
    """Manages async HTTP clients for all backend services."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._asr_client: Optional[httpx.AsyncClient] = None
        self._llm_client: Optional[httpx.AsyncClient] = None
        self._tts_client: Optional[httpx.AsyncClient] = None

    async def start(self):
        """Initialize all HTTP clients."""
        timeout = httpx.Timeout(timeout=120.0, connect=10.0)

        self._asr_client = httpx.AsyncClient(
            base_url=self.settings.asr_url,
            timeout=timeout,
        )
        self._llm_client = httpx.AsyncClient(
            base_url=self.settings.llm_url,
            timeout=timeout,
        )
        self._tts_client = httpx.AsyncClient(
            base_url=self.settings.tts_url,
            timeout=timeout,
        )

    async def close(self):
        """Close all HTTP clients."""
        for client in [self._asr_client, self._llm_client, self._tts_client]:
            if client:
                await client.aclose()

    @property
    def asr(self) -> httpx.AsyncClient:
        assert self._asr_client, "ASR client not initialized"
        return self._asr_client

    @property
    def llm(self) -> httpx.AsyncClient:
        assert self._llm_client, "LLM client not initialized"
        return self._llm_client

    @property
    def tts(self) -> httpx.AsyncClient:
        assert self._tts_client, "TTS client not initialized"
        return self._tts_client

    async def check_asr_health(self) -> dict:
        """Check ASR service health."""
        try:
            resp = await self._asr_client.get("/health", timeout=5.0)
            return {"status": "healthy", "detail": resp.json()}
        except Exception as e:
            return {"status": "unhealthy", "detail": str(e)}

    async def check_llm_health(self) -> dict:
        """Check LLM service health."""
        try:
            resp = await self._llm_client.get("/health", timeout=5.0)
            return {"status": "healthy", "detail": resp.json()}
        except Exception as e:
            return {"status": "unhealthy", "detail": str(e)}

    async def check_tts_health(self) -> dict:
        """Check TTS service health."""
        try:
            resp = await self._tts_client.get("/health", timeout=5.0)
            return {"status": "healthy", "detail": resp.json()}
        except Exception as e:
            return {"status": "unhealthy", "detail": str(e)}
