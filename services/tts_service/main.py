"""
TTS Service - Main Application
Text-to-speech service using edge-tts with Vietnamese voices.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from synthesizer import TTSSynthesizer
from text_normalizer import normalize_vietnamese_text

# Configuration
TTS_ENGINE = os.getenv("TTS_ENGINE", "edge-tts")
TTS_VOICE = os.getenv("TTS_VOICE", "vi-VN-HoaiMyNeural")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("tts_service")

# Global synthesizer
synthesizer: TTSSynthesizer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global synthesizer
    logger.info(f"🔊 Initializing TTS engine: {TTS_ENGINE}")
    logger.info(f"   Voice: {TTS_VOICE}")
    synthesizer = TTSSynthesizer(engine=TTS_ENGINE, voice=TTS_VOICE)
    logger.info("✅ TTS engine ready")
    yield
    logger.info("👋 TTS service shut down")


app = FastAPI(
    title="TTS Service",
    description="Vietnamese Text-to-Speech service",
    version="0.1.0",
    lifespan=lifespan,
)


class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: Optional[str] = None


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "engine": TTS_ENGINE,
        "voice": TTS_VOICE,
    }


@app.get("/voices")
async def list_voices():
    """List available Vietnamese voices."""
    voices = await synthesizer.list_voices()
    return {"voices": voices}


@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    """
    Synthesize text to speech.
    Returns base64-encoded audio (MP3).
    """
    try:
        # Normalize Vietnamese text
        normalized_text = normalize_vietnamese_text(request.text)
        logger.info(f"Synthesizing: \"{normalized_text[:80]}...\"")

        # Synthesize
        voice = request.voice or TTS_VOICE
        result = await synthesizer.synthesize(normalized_text, voice=voice)

        return {
            "audio_base64": result["audio_base64"],
            "duration_ms": result.get("duration_ms"),
            "format": "mp3",
        }

    except Exception as e:
        logger.error(f"Synthesis error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"TTS synthesis failed: {str(e)}"},
        )
