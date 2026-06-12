"""
End-to-End Voice Pipeline Test.
Run with: pytest tests/test_e2e_voice.py -v
Requires ALL services to be running.
"""

import pytest
import httpx


@pytest.mark.asyncio
async def test_e2e_text_chat(api_base_url):
    """Test full text chat through API gateway."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{api_base_url}/chat/text",
            json={"message": "Xin chào, bạn là ai?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert len(data["reply"]) > 0
        assert "latency_ms" in data
        print(f"Reply: {data['reply']}")
        print(f"Latency: {data['latency_ms']:.0f}ms")


@pytest.mark.asyncio
async def test_e2e_health_check(api_base_url):
    """Test health endpoint returns all service statuses."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{api_base_url}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "services" in data
        assert "asr" in data["services"]
        assert "llm" in data["services"]
        assert "tts" in data["services"]
        print(f"Overall: {data['status']}")
        for svc, status in data["services"].items():
            print(f"  {svc}: {status['status']}")


@pytest.mark.asyncio
async def test_e2e_frontend_served(api_base_url):
    """Test that frontend is served at root."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{api_base_url}/")
        assert resp.status_code == 200
        assert "Lab Assistant" in resp.text
