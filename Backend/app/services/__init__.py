"""Services module aggregator — clean import surface for business logic and AI pipelines."""

from app.services.craft_service import match_craft_and_gi
from app.services.image_service import process_artisan_image
from app.services.llm_service import process_voice_transcription
from app.services.ondc_service import (
    build_ondc_catalog,
    build_ondc_item,
    build_statutory_tags,
    publish_item_to_ondc,
)
from app.services.pricing_service import get_price_suggestion, init_pricing_model
from app.services.stt_service import transcribe_audio
from app.services.supabase_service import (
    send_otp,
    upload_file,
    verify_jwt_token,
    verify_otp,
)
from app.services.tts_service import synthesize_speech

__all__ = [
    # STT & TTS
    "transcribe_audio",
    "synthesize_speech",
    # LLM & Extraction
    "process_voice_transcription",
    # Vision & Image Processing
    "process_artisan_image",
    # GI & Craft Detection
    "match_craft_and_gi",
    # Pricing ML
    "init_pricing_model",
    "get_price_suggestion",
    # ONDC & Beckn Protocol
    "build_statutory_tags",
    "build_ondc_item",
    "build_ondc_catalog",
    "publish_item_to_ondc",
    # Supabase Auth & Storage
    "send_otp",
    "verify_otp",
    "upload_file",
    "verify_jwt_token",
]