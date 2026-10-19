"""Text-to-Speech Service — Sarvam bulbul:v1 primary TTS with Edge TTS fallback."""

import base64
import io
import uuid
import edge_tts
import httpx
from pydantic import SecretStr

from app.config import settings
from app.services.supabase_service import upload_file
from app.utils.logger import logger

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

# Minimal valid WAV (silent) — prevents empty-body 500s when all TTS providers fail
DUMMY_WAV_HEADER = (
    b"RIFF"
    b"\x24\x00\x00\x00"  # chunk size
    b"WAVE"
    b"fmt "
    b"\x10\x00\x00\x00"  # subchunk1 size
    b"\x01\x00"          # PCM
    b"\x01\x00"          # mono
    b"\x40\x1f\x00\x00"  # 8000 Hz
    b"\x40\x1f\x00\x00"  # byte rate
    b"\x01\x00"          # block align
    b"\x08\x00"          # bits per sample
    b"data"
    b"\x00\x00\x00\x00"  # data size 0
)

SARVAM_VOICE_MAP = {
    "hi": {"language_code": "hi-IN", "speaker": "meera"},
    "bn": {"language_code": "bn-IN", "speaker": "tanushree"},
    "kn": {"language_code": "kn-IN", "speaker": "ananya"},
    "ml": {"language_code": "ml-IN", "speaker": "arya"},
    "mr": {"language_code": "mr-IN", "speaker": "aarohi"},
    "od": {"language_code": "od-IN", "speaker": "subhashree"},
    "pa": {"language_code": "pa-IN", "speaker": "jasleen"},
    "ta": {"language_code": "ta-IN", "speaker": "saranya"},
    "te": {"language_code": "te-IN", "speaker": "lalitha"},
    "gu": {"language_code": "gu-IN", "speaker": "dhwani"},
    "en": {"language_code": "en-IN", "speaker": "meera"},
}

EDGE_VOICE_MAP = {
    "hi": "hi-IN-SwaraNeural",
    "bn": "bn-IN-TanishaaNeural",
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "mr": "mr-IN-AarohiNeural",
    "gu": "gu-IN-DhwaniNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "en": "en-IN-NeerjaNeural",
}


class TTSService:
    def __init__(self) -> None:
        raw_key = settings.sarvam_api_key
        if isinstance(raw_key, SecretStr):
            self.sarvam_key = raw_key.get_secret_value()
        else:
            self.sarvam_key = str(raw_key or "")

    async def synthesize(self, text: str, language: str = "hi") -> bytes:
        """Synthesizes text to audio bytes (Sarvam.ai -> Edge TTS -> dummy WAV)."""
        if not text or not text.strip():
            return DUMMY_WAV_HEADER

        # Tier 1: Sarvam.ai TTS
        if self.sarvam_key and self.sarvam_key != "placeholder_sarvam_key":
            try:
                audio_bytes = await self._synthesize_sarvam(text, language)
                logger.info("TTS succeeded via Sarvam.ai (lang: {})", language)
                return audio_bytes
            except Exception as exc:
                logger.warning(
                    "Sarvam.ai TTS failed, falling back to Edge TTS. Error: {}",
                    str(exc),
                )

        # Tier 2: Edge TTS
        try:
            audio_bytes = await self._synthesize_edge_tts(text, language)
            logger.info("TTS succeeded via Edge TTS fallback (lang: {})", language)
            return audio_bytes
        except Exception as exc:
            logger.error(
                "All TTS providers failed; returning dummy WAV. Edge TTS error: {}",
                str(exc),
            )
            return DUMMY_WAV_HEADER

    async def synthesize_and_upload(
        self,
        text: str,
        language: str = "hi",
    ) -> str:
        """Synthesize, upload to Supabase Storage, return public URL."""
        audio_bytes = await self.synthesize(text, language)
        if not audio_bytes or audio_bytes == DUMMY_WAV_HEADER:
            # Still upload dummy so callers get a URL in dev, or return "" if you prefer
            pass

        if not audio_bytes:
            return ""

        destination_path = f"voice/readback/{uuid.uuid4()}.wav"
        public_url = await upload_file(
            bucket_name=settings.supabase_storage_bucket,
            file_path=destination_path,
            file_bytes=audio_bytes,
            content_type="audio/wav",
        )
        return public_url or ""

    async def _synthesize_sarvam(self, text: str, language: str) -> bytes:
        voice_cfg = SARVAM_VOICE_MAP.get(language, SARVAM_VOICE_MAP["hi"])
        headers = {
            "api-subscription-key": self.sarvam_key,
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": [text[:500]],
            "target_language_code": voice_cfg["language_code"],
            "speaker": voice_cfg["speaker"],
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": 16000,
            "enable_preprocessing": True,
            "model": "bulbul:v1",
        }

        async with httpx.AsyncClient(
            timeout=settings.sarvam_tts_timeout_seconds
        ) as client:
            response = await client.post(
                SARVAM_TTS_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            res_json = response.json()
            audios = res_json.get("audios", [])

            if not audios or not audios[0]:
                raise ValueError("Sarvam.ai returned empty audio data.")

            return base64.b64decode(audios[0])

    async def _synthesize_edge_tts(self, text: str, language: str) -> bytes:
        voice = EDGE_VOICE_MAP.get(language, "hi-IN-SwaraNeural")
        communicate = edge_tts.Communicate(text, voice)
        audio_stream = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])

        audio_bytes = audio_stream.getvalue()
        if not audio_bytes:
            raise ValueError("Edge TTS generated empty audio.")

        return audio_bytes


tts_service = TTSService()


async def synthesize_speech(
    text: str,
    language_code: str = "hi",
) -> bytes:
    """Public top-level function for routers/voice.py."""
    return await tts_service.synthesize(text, language_code)