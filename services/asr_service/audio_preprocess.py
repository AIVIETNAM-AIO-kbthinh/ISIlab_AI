"""
ASR Service - Audio Preprocessing
Converts audio to 16kHz mono WAV format for optimal ASR performance.
"""

import logging
import os
import tempfile

from pydub import AudioSegment

logger = logging.getLogger("asr_service.audio_preprocess")

# Target audio format for ASR
TARGET_SAMPLE_RATE = 16000
TARGET_CHANNELS = 1  # mono
TARGET_SAMPLE_WIDTH = 2  # 16-bit


def preprocess_audio(input_path: str) -> str:
    """
    Preprocess audio file for ASR:
    - Convert to WAV format (16kHz, mono, 16-bit)
    - This ensures compatibility with faster-whisper
    
    Args:
        input_path: Path to input audio file
        
    Returns:
        Path to preprocessed WAV file
    """
    try:
        file_size = os.path.getsize(input_path)
        logger.info(f"Preprocessing: {os.path.basename(input_path)} ({file_size} bytes)")

        # Load audio with pydub (handles webm, ogg, mp3, wav, etc.)
        # For webm/opus from browsers, pydub uses ffmpeg to decode
        audio = AudioSegment.from_file(input_path)

        logger.info(
            f"Loaded audio: {audio.duration_seconds:.2f}s, "
            f"{audio.frame_rate}Hz, {audio.channels}ch, "
            f"{audio.sample_width * 8}-bit, dBFS={audio.dBFS:.1f}"
        )

        # Convert to mono
        if audio.channels != TARGET_CHANNELS:
            audio = audio.set_channels(TARGET_CHANNELS)

        # Resample to 16kHz
        if audio.frame_rate != TARGET_SAMPLE_RATE:
            audio = audio.set_frame_rate(TARGET_SAMPLE_RATE)

        # Set sample width to 16-bit
        if audio.sample_width != TARGET_SAMPLE_WIDTH:
            audio = audio.set_sample_width(TARGET_SAMPLE_WIDTH)

        # DO NOT trim silence — let Whisper handle it.
        # Browser-recorded audio (webm/opus) often has different
        # volume characteristics that our simple trim could mishandle.

        # Export as WAV (PCM format for best compatibility)
        output_path = tempfile.mktemp(suffix=".wav")
        audio.export(output_path, format="wav")

        output_size = os.path.getsize(output_path)
        logger.info(
            f"Preprocessed: {audio.duration_seconds:.2f}s, "
            f"{TARGET_SAMPLE_RATE}Hz mono 16-bit, "
            f"{output_size} bytes"
        )

        return output_path

    except Exception as e:
        logger.error(f"Audio preprocessing failed: {e}", exc_info=True)
        # Return original path — faster-whisper may still handle it via ffmpeg
        return input_path
