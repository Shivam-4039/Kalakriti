"""Audio utility helpers — Validation and normalization to WAV 16kHz mono."""

import io
from app.utils.logger import logger


def validate_audio_bytes(audio_bytes: bytes, min_bytes: int = 100) -> bool:
    """Validate that audio payload is non-empty and exceeds minimum byte threshold."""
    if not audio_bytes or len(audio_bytes) < min_bytes:
        return False
    return True


def normalize_audio_to_wav(audio_bytes: bytes, target_sample_rate: int = 16000) -> bytes:
    """
    Normalize arbitrary audio recording (M4A, OGG, MP3, 3GP, WAV) to 16kHz mono WAV.
    Falls back gracefully to raw bytes if ffmpeg or pydub fails.
    """
    if not validate_audio_bytes(audio_bytes):
        return audio_bytes

    try:
        from pydub import AudioSegment

        # Load audio stream from memory
        audio_stream = io.BytesIO(audio_bytes)
        sound = AudioSegment.from_file(audio_stream)

        # Resample to 16kHz mono (standard for Sarvam and Whisper STT models)
        sound = sound.set_channels(1).set_frame_rate(target_sample_rate)

        # Export back to WAV bytes in memory
        output_buffer = io.BytesIO()
        sound.export(output_buffer, format="wav")
        normalized_bytes = output_buffer.getvalue()

        logger.info(
            "Normalized audio: {} bytes -> {} bytes WAV ({}Hz mono)",
            len(audio_bytes),
            len(normalized_bytes),
            target_sample_rate,
        )
        return normalized_bytes

    except Exception as exc:
        logger.warning(
            "Audio normalization fallback triggered (FFmpeg missing or unsupported format): {}",
            exc,
        )
        # Fall back to original bytes if ffmpeg isn't installed locally
        return audio_bytes