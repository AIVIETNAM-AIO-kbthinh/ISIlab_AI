"""
Tests for ASR Service.
Run with: pytest tests/test_asr.py -v
Requires ASR service to be running on port 8001.
"""

import pytest
import httpx


@pytest.mark.asyncio
async def test_asr_health(asr_base_url):
    """Test ASR service health endpoint."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{asr_base_url}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "model" in data


@pytest.mark.asyncio
async def test_asr_transcribe_requires_audio(asr_base_url):
    """Test that /transcribe requires an audio file."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{asr_base_url}/transcribe")
        assert resp.status_code == 422  # Validation error
