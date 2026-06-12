"""
API Gateway - Pydantic Schemas for Chat
Request and response models for chat endpoints.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


# ── Request Models ──────────────────────────────────────────

class TextChatRequest(BaseModel):
    """Request body for text chat."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message in Vietnamese")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    model: Optional[str] = Field(None, description="Override LLM model name")


class TTSSynthesizeRequest(BaseModel):
    """Request body for TTS synthesis."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    voice: Optional[str] = Field(None, description="TTS voice name override")


# ── Response Models ─────────────────────────────────────────

class ASRResult(BaseModel):
    """ASR transcription result."""
    text: str
    language: str = "vi"
    confidence: Optional[float] = None
    duration_ms: Optional[float] = None


class LLMResult(BaseModel):
    """LLM generation result."""
    text: str
    model: str
    generation_ms: Optional[float] = None


class TTSResult(BaseModel):
    """TTS synthesis result."""
    audio_url: Optional[str] = None
    duration_ms: Optional[float] = None


class TextChatResponse(BaseModel):
    """Response for text chat."""
    reply: str
    model: str
    latency_ms: float


class VoiceChatResponse(BaseModel):
    """Response for voice chat."""
    transcript: str
    reply: str
    audio_url: Optional[str] = None
    model: str
    latency: dict = Field(
        default_factory=dict,
        description="Latency breakdown: asr_ms, llm_ms, tts_ms, total_ms"
    )


class HealthStatus(BaseModel):
    """Health check response."""
    status: str
    services: dict
    version: str = "0.1.0"


class ModelInfo(BaseModel):
    """Model information."""
    name: str
    size: Optional[str] = None
    family: Optional[str] = None
