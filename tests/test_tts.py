"""
Tests for TTS Service.
Run with: pytest tests/test_tts.py -v
Requires TTS service to be running on port 8002.
"""

import pytest
import httpx


@pytest.mark.asyncio
async def test_tts_health(tts_base_url):
    """Test TTS service health endpoint."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{tts_base_url}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_tts_list_voices(tts_base_url):
    """Test listing available voices."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{tts_base_url}/voices")
        assert resp.status_code == 200
        data = resp.json()
        assert "voices" in data


@pytest.mark.asyncio
async def test_tts_synthesize_vietnamese(tts_base_url):
    """Test Vietnamese text synthesis."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{tts_base_url}/synthesize",
            json={"text": "Xin chào, tôi là trợ lý phòng thí nghiệm."},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "audio_base64" in data
        assert len(data["audio_base64"]) > 100  # Should have meaningful audio data


@pytest.mark.asyncio
async def test_tts_synthesize_empty_text(tts_base_url):
    """Test that empty text returns error."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{tts_base_url}/synthesize",
            json={"text": ""},
        )
        assert resp.status_code == 422
