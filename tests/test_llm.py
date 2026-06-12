"""
Tests for LLM Service.
Run with: pytest tests/test_llm.py -v
Requires LLM service to be running on port 8003 and Ollama running.
"""

import pytest
import httpx


@pytest.mark.asyncio
async def test_llm_health(llm_base_url):
    """Test LLM service health endpoint."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{llm_base_url}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data


@pytest.mark.asyncio
async def test_llm_list_models(llm_base_url):
    """Test listing available models."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{llm_base_url}/models")
        assert resp.status_code == 200
        data = resp.json()
        assert "models" in data


@pytest.mark.asyncio
async def test_llm_chat_vietnamese(llm_base_url):
    """Test Vietnamese chat response."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{llm_base_url}/chat",
            json={"message": "Xin chào, bạn là ai?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "text" in data
        assert len(data["text"]) > 0
        assert "model" in data


@pytest.mark.asyncio
async def test_llm_chat_empty_message(llm_base_url):
    """Test that empty message returns error."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{llm_base_url}/chat",
            json={"message": ""},
        )
        assert resp.status_code == 422
