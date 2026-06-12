"""
ASR Service - Whisper Transcriber
Wraps faster-whisper for Vietnamese speech recognition.
Can be swapped with PhoWhisper by changing model_size to a HuggingFace model path.
"""

import logging
import os
from typing import Optional

from faster_whisper import WhisperModel

from audio_preprocess import preprocess_audio

logger = logging.getLogger("asr_service.transcriber")


class WhisperTranscriber:
    """
    Vietnamese speech-to-text using faster-whisper (CTranslate2 backend).
    
    For PhoWhisper, set model_size to:
      - "vinai/PhoWhisper-base"
      - "vinai/PhoWhisper-small"
      - "vinai/PhoWhisper-medium"
      - "vinai/PhoWhisper-large"
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "vi",
    ):
        self.language = language
        self.device = device

        # Adjust compute type based on device
        if device == "cuda":
            compute_type = "float16"

        logger.info(f"Loading Whisper model: {model_size} ({device}, {compute_type})")
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )
        logger.info("Whisper model loaded successfully")

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> dict:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Override language code (default: Vietnamese)
            
        Returns:
            dict with keys: text, language, confidence
        """
        lang = language or self.language

        # Preprocess audio (convert to 16kHz mono WAV)
        processed_path = preprocess_audio(audio_path)

        # Log audio file info for debugging
        file_size = os.path.getsize(processed_path) if os.path.exists(processed_path) else 0
        logger.info(f"Audio file for transcription: {processed_path} ({file_size} bytes)")

        # First attempt: WITHOUT VAD filter
        # VAD can be too aggressive with browser-recorded audio (webm/opus)
        # and may filter out all speech, so we try without it first.
        segments, info = self.model.transcribe(
            processed_path,
            language=lang,
            beam_size=5,
            vad_filter=False,
        )

        # Collect all segments
        full_text = ""
        total_confidence = 0.0
        segment_count = 0

        for segment in segments:
            logger.debug(f"Segment [{segment.start:.1f}s - {segment.end:.1f}s]: {segment.text}")
            full_text += segment.text
            total_confidence += segment.avg_log_prob
            segment_count += 1

        avg_confidence = (
            total_confidence / segment_count if segment_count > 0 else 0.0
        )

        logger.info(
            f"Transcription result: {segment_count} segments, "
            f"text='{full_text.strip()[:100]}', confidence={avg_confidence:.3f}"
        )

        # Clean up preprocessed file if different from input
        if processed_path != audio_path and os.path.exists(processed_path):
            os.unlink(processed_path)

        return {
            "text": full_text.strip(),
            "language": info.language if info.language else lang,
            "confidence": round(avg_confidence, 4),
        }
