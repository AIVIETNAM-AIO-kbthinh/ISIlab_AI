"""
Test configuration and shared fixtures.
"""

import pytest


@pytest.fixture
def api_base_url():
    """Base URL for the API gateway."""
    return "http://localhost:8000"


@pytest.fixture
def asr_base_url():
    """Base URL for the ASR service."""
    return "http://localhost:8001"


@pytest.fixture
def llm_base_url():
    """Base URL for the LLM service."""
    return "http://localhost:8003"


@pytest.fixture
def tts_base_url():
    """Base URL for the TTS service."""
    return "http://localhost:8002"


@pytest.fixture
def sample_vietnamese_messages():
    """Sample Vietnamese messages for testing."""
    return [
        "Xin chào, bạn là ai?",
        "Bạn có thể làm gì?",
        "Nội quy phòng lab là gì?",
        "Làm sao để sử dụng máy in 3D?",
    ]
