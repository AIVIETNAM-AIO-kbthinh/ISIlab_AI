"""
AI Lab Assistant - API Gateway
Main entry point for the FastAPI application.
Serves as the central hub routing requests to ASR, LLM, and TTS services.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.config import settings
from core.services import ServiceClients
from routes import chat, health, asr, tts

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api_gateway")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize and cleanup service clients."""
    logger.info("🚀 Starting AI Lab Assistant API Gateway")
    logger.info(f"   ASR Service: {settings.asr_url}")
    logger.info(f"   LLM Service: {settings.llm_url}")
    logger.info(f"   TTS Service: {settings.tts_url}")

    # Initialize shared HTTP clients
    app.state.clients = ServiceClients(settings)
    await app.state.clients.start()
    logger.info("✅ Service clients initialized")

    yield

    # Cleanup
    await app.state.clients.close()
    logger.info("👋 API Gateway shut down")


app = FastAPI(
    title="AI Lab Assistant",
    description="Vietnamese AI Assistant for University Labs — API Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} ({duration_ms:.0f}ms)"
    )
    return response


# Register API routes
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(asr.router, prefix="/asr", tags=["ASR"])
app.include_router(tts.router, prefix="/tts", tags=["TTS"])

# Serve frontend static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the web frontend."""
    return FileResponse("static/index.html")
