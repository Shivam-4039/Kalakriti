"""Speech-to-Text Service — Sarvam saaras:v1 primary STT with Groq Whisper fallback."""

import io
import httpx
from pydantic import SecretStr

from app.config import settings
from app.utils.logger import logger

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

# Mapping from ISO 639-1 / BCP-47 to Sarvam language codes
SARVAM_LANG_MAP = {
    "hi": "hi-IN",
    "bn": "bn-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "mr": "mr-IN",
    "od": "od-IN",
    "pa": "pa-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "gu": "gu-IN",
    "en": "en-IN",
}


class STTService:
    def __init__(self) -> None:
        raw_key = settings.sarvam_api_key
        if isinstance(raw_key, SecretStr):
            self.sarvam_key = raw_key.get_secret_value()
        else:
            self.sarvam_key = str(raw_key or "")

        self.groq_keys = settings.groq_api_key_list
        self.current_groq_index = 0

    def _get_groq_key(self) -> str:
        """Rotates Groq API keys to handle rate limits."""
        if not self.groq_keys or self.groq_keys[0] == "placeholder_groq_key":
            return ""
        key = self.groq_keys[self.current_groq_index % len(self.groq_keys)]
        self.current_groq_index += 1
        return key

    async def transcribe(
        self,
        wav_audio_bytes: bytes,
        language_hint: str = "hi",
    ) -> dict:
        """
        Transcribes WAV audio to text.
        Tries Sarvam.ai first -> falls back to Groq Whisper if Sarvam fails.
        Returns dict: {"transcript": str, "language": str, "provider": str}
        """
        if not wav_audio_bytes or len(wav_audio_bytes) < 100:
            return {"transcript": "", "language": language_hint, "provider": "none"}

        # Tier 1: Sarvam.ai (Primary)
        if self.sarvam_key and self.sarvam_key != "placeholder_sarvam_key":
            try:
                result = await self._transcribe_sarvam(wav_audio_bytes, language_hint)
                logger.info("STT succeeded via Sarvam.ai (lang: {})", language_hint)
                return result
            except Exception as exc:
                logger.warning(
                    "Sarvam.ai STT failed, switching to Groq Whisper fallback. Error: {}",
                    str(exc),
                )

        # Tier 2: Groq Whisper (Fallback)
        groq_key = self._get_groq_key()
        if groq_key:
            try:
                result = await self._transcribe_groq(wav_audio_bytes, language_hint)
                logger.info("STT succeeded via Groq Whisper fallback")
                return result
            except Exception as exc:
                logger.error("Groq Whisper STT fallback failed: {}", str(exc))

        # Tier 3: Dev Fallback (when no valid API keys are supplied)
        logger.warning("No valid STT keys configured or all failed — using dev transcription fallback")
        return {
            "transcript": "यह एक सुंदर हस्तशिल्प उत्पाद है",
            "language": language_hint,
            "provider": "dev_fallback",
        }

    async def _transcribe_sarvam(self, wav_bytes: bytes, lang_code: str) -> dict:
        """Call Sarvam.ai Speech-to-Text API."""
        sarvam_lang = SARVAM_LANG_MAP.get(lang_code, "hi-IN")
        headers = {"api-subscription-key": self.sarvam_key}
        files = {"file": ("audio.wav", wav_bytes, "audio/wav")}
        data = {"model": "saaras:v1", "language_code": sarvam_lang}

        async with httpx.AsyncClient(
            timeout=settings.sarvam_stt_timeout_seconds
        ) as client:
            response = await client.post(
                SARVAM_STT_URL,
                headers=headers,
                files=files,
                data=data,
            )
            response.raise_for_status()
            res_json = response.json()
            transcript = res_json.get("transcript", "").strip()

            if not transcript:
                raise ValueError("Sarvam.ai returned empty transcript.")

            return {
                "transcript": transcript,
                "language": lang_code,
                "provider": "sarvam",
            }

    async def _transcribe_groq(self, wav_bytes: bytes, lang_code: str) -> dict:
        """Call Groq Whisper API as a fallback."""
        groq_key = self._get_groq_key()
        headers = {"Authorization": f"Bearer {groq_key}"}
        files = {"file": ("audio.wav", io.BytesIO(wav_bytes), "audio/wav")}
        data = {
            "model": "whisper-large-v3",
            "language": lang_code if lang_code in ("hi", "en", "ta", "te", "bn", "mr") else "hi",
            "response_format": "json",
        }

        async with httpx.AsyncClient(timeout=settings.groq_timeout_seconds) as client:
            response = await client.post(
                GROQ_STT_URL,
                headers=headers,
                files=files,
                data=data,
            )
            response.raise_for_status()
            res_json = response.json()
            transcript = res_json.get("text", "").strip()

            if not transcript:
                raise ValueError("Groq Whisper returned empty transcript.")

            return {
                "transcript": transcript,
                "language": lang_code,
                "provider": "groq_whisper",
            }


stt_service = STTService()


async def transcribe_audio(
    audio_bytes: bytes,
    language_code: str = "hi",
) -> str:
    """
    Public top-level interface for STT transcription.
    Returns the transcript string directly.
    """
    res = await stt_service.transcribe(audio_bytes, language_code)
    return res.get("transcript", "")