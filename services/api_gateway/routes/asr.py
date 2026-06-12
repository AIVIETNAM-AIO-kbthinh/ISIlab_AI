"""
API Gateway - ASR Routes
Standalone ASR endpoint for direct speech-to-text.
"""

import logging
import time

from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import JSONResponse

from schemas.chat import ASRResult

router = APIRouter()
logger = logging.getLogger("api_gateway.asr")


@router.post("/transcribe", response_model=ASRResult)
async def transcribe_audio(request: Request, audio: UploadFile = File(...)):
    """
    Transcribe audio file to text.
    Accepts audio in any common format (wav, mp3, webm, ogg).
    """
    clients = request.app.state.clients

    try:
        t0 = time.perf_counter()
        audio_bytes = await audio.read()

        response = await clients.asr.post(
            "/transcribe",
            files={"audio": (audio.filename or "audio.webm", audio_bytes, audio.content_type or "audio/webm")},
        )
        response.raise_for_status()
        data = response.json()

        duration_ms = (time.perf_counter() - t0) * 1000
        logger.info(f"ASR transcription: \"{data['text']}\" ({duration_ms:.0f}ms)")

        return ASRResult(
            text=data["text"],
            language=data.get("language", "vi"),
            confidence=data.get("confidence"),
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error(f"ASR error: {e}")
        return JSONResponse(
            status_code=502,
            content={"error": f"ASR service error: {str(e)}"},
        )
