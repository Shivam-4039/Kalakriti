# Kalakriti/Backend/app/schemas/voice.py

import uuid
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.pricing import PricingResponse
from app.services.craft_service import CraftGIMatch


class ExtractedProductFields(BaseModel):
    """Structured fields extracted by LLM from the artisan's voice transcript."""

    title_en: Optional[str] = Field(None, description="Short e-commerce title in English")
    title_hi: Optional[str] = Field(None, description="Short e-commerce title in Hindi")
    title_native: Optional[str] = Field(None, description="Product title in spoken native language")
    craft_type: str = Field("handicraft", description="Craft or weaving technique identified")
    material: str = Field("other", description="Primary raw material used")
    color: Optional[str] = Field(None, description="Primary color or color scheme")
    description_en: Optional[str] = Field(None, description="Market-ready product description in English")
    description_hi: Optional[str] = Field(None, description="Market-ready product description in Hindi")
    description_native: Optional[str] = Field(None, description="Detailed product description in native language")
    length_cm: Optional[float] = Field(15.0, description="Estimated length in cm")
    width_cm: Optional[float] = Field(15.0, description="Estimated width in cm")
    height_cm: Optional[float] = Field(15.0, description="Estimated height in cm")
    weight_g: Optional[float] = Field(500.0, description="Estimated weight in grams")
    price_expectation_inr: Optional[float] = Field(
        default=None, description="Artisan's stated price expectation if mentioned"
    )
    gi_tag: Optional[str] = Field(
        default=None, description="Matched GI Tag code or name"
    )


class VoiceProcessResponse(BaseModel):
    """Complete output returned after processing a voice note."""

    conversation_id: str = Field(..., description="Conversation UUID")
    transcript: str = Field(..., description="Original transcript in native language")
    raw_transcript: Optional[str] = Field(default=None, description="Alias for transcript")
    language_detected: Optional[str] = Field(default="hi", description="BCP-47 language code")
    english_transcript: Optional[str] = Field(default=None, description="English translation")
    extracted_fields: ExtractedProductFields
    pricing: Optional[PricingResponse] = None
    gi_match: Optional[CraftGIMatch] = None
    readback_text: str = Field(..., description="The text read aloud by TTS")
    readback_audio_base64: Optional[str] = Field(default="", description="Base64 encoded audio for instant mobile playback")
    readback_audio_url: Optional[str] = Field(default=None, description="Storage URL of audio")
    confidence_score: float = Field(default=0.85, description="Overall pipeline confidence")

    @model_validator(mode="after")
    def sync_transcripts(self) -> "VoiceProcessResponse":
        if self.raw_transcript is None:
            self.raw_transcript = self.transcript
        return self


class VoiceApprovalRequest(BaseModel):
    """Artisan's approval decision for a voice-generated listing draft."""

    conversation_id: uuid.UUID
    is_approved: bool = True
    decision: Optional[Literal["approved", "rejected", "modified"]] = None
    corrected_fields: Optional[dict[str, Any]] = None
    final_price_inr: Optional[float] = None
    image_urls: Optional[list[str]] = None