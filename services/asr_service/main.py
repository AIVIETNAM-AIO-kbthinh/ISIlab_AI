"""
ASR Service - Main Application
Speech-to-text service using faster-whisper with Vietnamese support.
"""

import logging
import os
import time
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

from transcriber import WhisperTranscriber

# Configuration
ASR_MODEL_SIZE = os.getenv("ASR_MODEL_SIZE", "base")
ASR_DEVICE = os.getenv("ASR_DEVICE", "cpu")
ASR_LANGUAGE = os.getenv("ASR_LANGUAGE", "vi")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("asr_service")

# Global transcriber instance
transcriber: WhisperTranscriber = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global transcriber
    logger.info(f"🎙️  Loading ASR model: {ASR_MODEL_SIZE} (device: {ASR_DEVICE})")
    transcriber = WhisperTranscriber(
        model_size=ASR_MODEL_SIZE,
        device=ASR_DEVICE,
        language=ASR_LANGUAGE,
    )
    logger.info("✅ ASR model loaded")
    yield
    logger.info("👋 ASR service shut down")


app = FastAPI(
    title="ASR Service",
    description="Speech-to-text service for Vietnamese",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model": ASR_MODEL_SIZE,
        "device": ASR_DEVICE,
        "language": ASR_LANGUAGE,
    }


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """
    Transcribe audio file to Vietnamese text.
    Accepts: wav, mp3, webm, ogg, flac, m4a
    """
    try:
        t0 = time.perf_counter()

        # Save uploaded audio to temp file
        suffix = os.path.splitext(audio.filename or "audio.webm")[1] or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Transcribe
        result = transcriber.transcribe(tmp_path)

        # Cleanup
        os.unlink(tmp_path)

        duration_ms = (time.perf_counter() - t0) * 1000
        logger.info(f"Transcribed: \"{result['text']}\" ({duration_ms:.0f}ms)")

        return {
            "text": result["text"],
            "language": result.get("language", ASR_LANGUAGE),
            "confidence": result.get("confidence"),
            "duration_ms": duration_ms,
        }

    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Transcription failed: {str(e)}"},
        )
