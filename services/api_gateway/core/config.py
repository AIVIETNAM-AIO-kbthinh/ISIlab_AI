"""
API Gateway - Configuration
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # General
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # API Gateway
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ASR Service
    ASR_HOST: str = "localhost"
    ASR_PORT: int = 8001

    # LLM Service
    LLM_HOST: str = "localhost"
    LLM_PORT: int = 8003

    # TTS Service
    TTS_HOST: str = "localhost"
    TTS_PORT: int = 8002

    # Ollama (direct, for health checks)
    OLLAMA_HOST: str = "http://localhost:11434"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def asr_url(self) -> str:
        return f"http://{self.ASR_HOST}:{self.ASR_PORT}"

    @property
    def llm_url(self) -> str:
        return f"http://{self.LLM_HOST}:{self.LLM_PORT}"

    @property
    def tts_url(self) -> str:
        return f"http://{self.TTS_HOST}:{self.TTS_PORT}"


settings = Settings()
