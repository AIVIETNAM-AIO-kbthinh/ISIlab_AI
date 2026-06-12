"""
API Gateway - Chat Routes
Handles text and voice chat interactions.
"""

import logging
import time
import base64
from typing import Optional

from fastapi import APIRouter, Request, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from schemas.chat import TextChatRequest, TextChatResponse, VoiceChatResponse

router = APIRouter()
logger = logging.getLogger("api_gateway.chat")


@router.post("/text", response_model=TextChatResponse)
async def text_chat(request: Request, body: TextChatRequest):
    """
    Text chat endpoint.
    Sends user message to LLM service and returns the response.
    """
    clients = request.app.state.clients
    start = time.perf_counter()

    try:
        # Call LLM service
        llm_response = await clients.llm.post(
            "/chat",
            json={
                "message": body.message,
                "conversation_id": body.conversation_id,
                "model": body.model,
            },
        )
        llm_response.raise_for_status()
        llm_data = llm_response.json()

        total_ms = (time.perf_counter() - start) * 1000
        logger.info(f"Text chat completed in {total_ms:.0f}ms")

        return TextChatResponse(
            reply=llm_data["text"],
            model=llm_data.get("model", "unknown"),
            latency_ms=total_ms,
        )

    except Exception as e:
        logger.error(f"Text chat error: {e}")
        return JSONResponse(
            status_code=502,
            content={"error": f"LLM service error: {str(e)}"},
        )


@router.post("/voice", response_model=VoiceChatResponse)
async def voice_chat(request: Request, audio: UploadFile = File(...)):
    """
    Voice chat endpoint.
    Accepts audio file → ASR → LLM → TTS → returns response with audio.
    """
    clients = request.app.state.clients
    timings = {}

    try:
        # ── Step 1: ASR — Speech to Text ──
        t0 = time.perf_counter()
        audio_bytes = await audio.read()

        asr_response = await clients.asr.post(
            "/transcribe",
            files={"audio": (audio.filename or "audio.webm", audio_bytes, audio.content_type or "audio/webm")},
        )
        asr_response.raise_for_status()
        asr_data = asr_response.json()
        transcript = asr_data.get("text", "").strip()
        timings["asr_ms"] = (time.perf_counter() - t0) * 1000
        logger.info(f"ASR: \"{transcript}\" ({timings['asr_ms']:.0f}ms)")

        # Handle empty transcript (no speech detected)
        if not transcript:
            return VoiceChatResponse(
                transcript="",
                reply="Xin lỗi, tôi không nghe rõ. Bạn có thể nói lại được không?",
                audio_url=None,
                model="none",
                latency=timings,
            )

        # ── Step 2: LLM — Generate response ──
        t1 = time.perf_counter()
        llm_response = await clients.llm.post(
            "/chat",
            json={"message": transcript},
        )
        llm_response.raise_for_status()
        llm_data = llm_response.json()
        reply_text = llm_data["text"]
        timings["llm_ms"] = (time.perf_counter() - t1) * 1000
        logger.info(f"LLM: \"{reply_text[:80]}...\" ({timings['llm_ms']:.0f}ms)")

        # ── Step 3: TTS — Text to Speech ──
        t2 = time.perf_counter()
        tts_response = await clients.tts.post(
            "/synthesize",
            json={"text": reply_text},
        )
        tts_response.raise_for_status()
        tts_data = tts_response.json()
        timings["tts_ms"] = (time.perf_counter() - t2) * 1000
        logger.info(f"TTS: ({timings['tts_ms']:.0f}ms)")

        timings["total_ms"] = sum(timings.values())

        return VoiceChatResponse(
            transcript=transcript,
            reply=reply_text,
            audio_url=tts_data.get("audio_base64"),
            model=llm_data.get("model", "unknown"),
            latency=timings,
        )

    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        return JSONResponse(
            status_code=502,
            content={"error": f"Voice pipeline error: {str(e)}"},
        )


@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice chat.
    Client sends audio chunks, server returns transcript + audio response.
    """
    await websocket.accept()
    clients = websocket.app.state.clients
    logger.info("WebSocket voice session started")

    try:
        while True:
            # Receive audio data from client
            data = await websocket.receive_bytes()
            timings = {}

            # ── ASR ──
            t0 = time.perf_counter()
            asr_response = await clients.asr.post(
                "/transcribe",
                files={"audio": ("audio.webm", data, "audio/webm")},
            )
            asr_data = asr_response.json()
            transcript = asr_data.get("text", "")
            timings["asr_ms"] = (time.perf_counter() - t0) * 1000

            if not transcript.strip():
                await websocket.send_json({"type": "silence", "message": "No speech detected"})
                continue

            # Send transcript immediately
            await websocket.send_json({
                "type": "transcript",
                "text": transcript,
                "asr_ms": timings["asr_ms"],
            })

            # ── LLM ──
            t1 = time.perf_counter()
            llm_response = await clients.llm.post(
                "/chat",
                json={"message": transcript},
            )
            llm_data = llm_response.json()
            reply_text = llm_data["text"]
            timings["llm_ms"] = (time.perf_counter() - t1) * 1000

            # Send reply text
            await websocket.send_json({
                "type": "reply",
                "text": reply_text,
                "llm_ms": timings["llm_ms"],
            })

            # ── TTS ──
            t2 = time.perf_counter()
            tts_response = await clients.tts.post(
                "/synthesize",
                json={"text": reply_text},
            )
            tts_data = tts_response.json()
            timings["tts_ms"] = (time.perf_counter() - t2) * 1000

            # Send audio response
            await websocket.send_json({
                "type": "audio",
                "audio_base64": tts_data.get("audio_base64", ""),
                "latency": timings,
            })

    except WebSocketDisconnect:
        logger.info("WebSocket voice session ended")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))
