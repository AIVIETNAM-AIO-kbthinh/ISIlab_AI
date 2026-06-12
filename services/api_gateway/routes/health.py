"""
API Gateway - Health Check Routes
"""

import logging

from fastapi import APIRouter, Request

from schemas.chat import HealthStatus

router = APIRouter()
logger = logging.getLogger("api_gateway.health")


@router.get("/health", response_model=HealthStatus)
async def health_check(request: Request):
    """Check health of all services."""
    clients = request.app.state.clients

    asr_health = await clients.check_asr_health()
    llm_health = await clients.check_llm_health()
    tts_health = await clients.check_tts_health()

    services = {
        "asr": asr_health,
        "llm": llm_health,
        "tts": tts_health,
    }

    all_healthy = all(s["status"] == "healthy" for s in services.values())

    return HealthStatus(
        status="healthy" if all_healthy else "degraded",
        services=services,
    )


@router.get("/models")
async def list_models(request: Request):
    """List available LLM models from Ollama."""
    clients = request.app.state.clients

    try:
        resp = await clients.llm.get("/models")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return {"models": [], "error": str(e)}
