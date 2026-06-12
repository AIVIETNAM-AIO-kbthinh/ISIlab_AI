"""
LLM Service - Main Application
Wrapper around Ollama API with Vietnamese lab assistant persona.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ollama_client import OllamaClient
from prompts import get_system_prompt

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("llm_service")

# Global Ollama client
ollama: OllamaClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ollama
    logger.info(f"🧠 Connecting to Ollama at {OLLAMA_HOST}")
    logger.info(f"   Default model: {OLLAMA_MODEL}")
    ollama = OllamaClient(base_url=OLLAMA_HOST, default_model=OLLAMA_MODEL)
    await ollama.start()

    # Check connection
    if await ollama.is_healthy():
        logger.info("✅ Ollama connection verified")
    else:
        logger.warning("⚠️  Ollama not reachable — will retry on requests")

    yield

    await ollama.close()
    logger.info("👋 LLM service shut down")


app = FastAPI(
    title="LLM Service",
    description="Vietnamese Lab Assistant LLM — Ollama wrapper",
    version="0.1.0",
    lifespan=lifespan,
)


# ── Request/Response Models ─────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    text: str
    model: str
    generation_ms: Optional[float] = None


# ── In-memory conversation store (Phase 1) ──────────────────

conversations: dict[str, list[dict]] = {}
MAX_HISTORY = 10  # Max messages per conversation


# ── Routes ──────────────────────────────────────────────────

@app.get("/health")
async def health():
    healthy = await ollama.is_healthy()
    return {
        "status": "healthy" if healthy else "unhealthy",
        "ollama_host": OLLAMA_HOST,
        "model": OLLAMA_MODEL,
    }


@app.get("/models")
async def list_models():
    """List available Ollama models."""
    try:
        models = await ollama.list_models()
        return {"models": models}
    except Exception as e:
        return {"models": [], "error": str(e)}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the Vietnamese lab assistant.
    Maintains conversation history per conversation_id.
    """
    model = request.model or OLLAMA_MODEL
    conv_id = request.conversation_id or "default"

    # Get or create conversation history
    if conv_id not in conversations:
        conversations[conv_id] = []

    history = conversations[conv_id]

    # Build messages with system prompt
    messages = [
        {"role": "system", "content": get_system_prompt()},
    ]
    messages.extend(history[-MAX_HISTORY:])
    messages.append({"role": "user", "content": request.message})

    try:
        # Call Ollama
        result = await ollama.chat(messages=messages, model=model)

        # Update conversation history
        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": result["text"]})

        # Trim history if too long
        if len(history) > MAX_HISTORY * 2:
            conversations[conv_id] = history[-MAX_HISTORY * 2:]

        return ChatResponse(
            text=result["text"],
            model=result.get("model", model),
            generation_ms=result.get("generation_ms"),
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return JSONResponse(
            status_code=502,
            content={"error": f"LLM generation failed: {str(e)}"},
        )


@app.post("/generate")
async def generate(request: ChatRequest):
    """
    Single-turn generation without conversation history.
    Useful for standalone text generation tasks.
    """
    model = request.model or OLLAMA_MODEL

    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": request.message},
    ]

    try:
        result = await ollama.chat(messages=messages, model=model)
        return ChatResponse(
            text=result["text"],
            model=result.get("model", model),
            generation_ms=result.get("generation_ms"),
        )
    except Exception as e:
        logger.error(f"Generate error: {e}")
        return JSONResponse(
            status_code=502,
            content={"error": f"LLM generation failed: {str(e)}"},
        )
