"""
API Gateway - TTS Routes
Standalone TTS endpoint for text-to-speech synthesis.
"""

import logging
import time

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from schemas.chat import TTSSynthesizeRequest

router = APIRouter()
logger = logging.getLogger("api_gateway.tts")


@router.post("/tts/synthesize")
async def synthesize_speech(request: Request, body: TTSSynthesizeRequest):
    """
    Synthesize text to speech.
    Returns base64-encoded audio.
    """
    clients = request.app.state.clients

    try:
        t0 = time.perf_counter()

        response = await clients.tts.post(
            "/synthesize",
            json={"text": body.text, "voice": body.voice},
        )
        response.raise_for_status()
        data = response.json()

        duration_ms = (time.perf_counter() - t0) * 1000
        logger.info(f"TTS synthesis ({duration_ms:.0f}ms)")

        return {
            "audio_base64": data.get("audio_base64"),
            "duration_ms": duration_ms,
        }

    except Exception as e:
        logger.error(f"TTS error: {e}")
        return JSONResponse(
            status_code=502,
            content={"error": f"TTS service error: {str(e)}"},
        )
