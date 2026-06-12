"""
TTS Service - Synthesizer
Text-to-speech engine abstraction.
Phase 1: edge-tts (Microsoft Edge TTS, free, excellent Vietnamese)
Future: Piper TTS, viXTTS
"""

import base64
import io
import logging
import time
from typing import Optional

import edge_tts

logger = logging.getLogger("tts_service.synthesizer")

# Available Vietnamese voices in edge-tts
VIETNAMESE_VOICES = {
    "vi-VN-HoaiMyNeural": "Female - Hoài My",
    "vi-VN-NamMinhNeural": "Male - Nam Minh",
}


class TTSSynthesizer:
    """
    TTS engine abstraction.
    Supports multiple backends with a common interface.
    """

    def __init__(self, engine: str = "edge-tts", voice: str = "vi-VN-HoaiMyNeural"):
        self.engine = engine
        self.default_voice = voice
        logger.info(f"TTS Synthesizer initialized: engine={engine}, voice={voice}")

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        volume: str = "+0%",
    ) -> dict:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            voice: Voice name override
            rate: Speech rate adjustment (e.g., "+10%", "-5%")
            volume: Volume adjustment
            
        Returns:
            dict with audio_base64 (base64-encoded MP3) and duration_ms
        """
        if self.engine == "edge-tts":
            return await self._synthesize_edge_tts(text, voice, rate, volume)
        else:
            raise ValueError(f"Unsupported TTS engine: {self.engine}")

    async def _synthesize_edge_tts(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        volume: str = "+0%",
    ) -> dict:
        """Synthesize using edge-tts."""
        voice = voice or self.default_voice
        t0 = time.perf_counter()

        communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)

        # Collect audio data into memory
        audio_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        audio_bytes = audio_buffer.getvalue()
        duration_ms = (time.perf_counter() - t0) * 1000

        if not audio_bytes:
            raise RuntimeError("TTS produced no audio output")

        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        logger.info(
            f"Synthesized {len(text)} chars → {len(audio_bytes)} bytes audio "
            f"({duration_ms:.0f}ms)"
        )

        return {
            "audio_base64": audio_base64,
            "duration_ms": round(duration_ms, 1),
            "size_bytes": len(audio_bytes),
        }

    async def list_voices(self) -> list[dict]:
        """List available Vietnamese voices."""
        if self.engine == "edge-tts":
            return await self._list_edge_voices()
        return []

    async def _list_edge_voices(self) -> list[dict]:
        """List Vietnamese voices from edge-tts."""
        try:
            all_voices = await edge_tts.list_voices()
            vi_voices = [
                {
                    "name": v["ShortName"],
                    "gender": v.get("Gender", ""),
                    "locale": v.get("Locale", ""),
                }
                for v in all_voices
                if v.get("Locale", "").startswith("vi")
            ]
            return vi_voices
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return [
                {"name": name, "description": desc}
                for name, desc in VIETNAMESE_VOICES.items()
            ]
