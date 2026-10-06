"""Voice Assistant Router — Voice-first cataloging, transcription, LLM extraction, and TTS."""

import base64
import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.artisan import Artisan
from app.models.conversation import Conversation
from app.routers.auth import get_current_artisan
from app.schemas.pricing import PricingRequest
from app.schemas.voice import (
    ExtractedProductFields,
    VoiceApprovalRequest,
    VoiceProcessResponse,
)
from app.services.craft_service import match_craft_and_gi
from app.services.llm_service import process_voice_transcription
from app.services.pricing_service import get_price_suggestion
from app.services.stt_service import transcribe_audio
from app.services.tts_service import synthesize_speech
from app.utils.audio import normalize_audio_to_wav, validate_audio_bytes
from app.utils.logger import logger

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])


# ---------------------------------------------------------------------------
# Auxiliary Request Schemas
# ---------------------------------------------------------------------------
class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Text to synthesize")
    language_code: str = Field("hi", description="ISO 639-1 language code", examples=["hi", "ta", "bn"])


class SynthesizeResponse(BaseModel):
    audio_base64: str
    content_type: str = "audio/wav"
    language_code: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post(
    "/process",
    response_model=VoiceProcessResponse,
    summary="Process voice recording into structured catalog draft",
    status_code=status.HTTP_200_OK,
)
async def process_voice_listing(
    audio_file: UploadFile = File(..., description="Audio recording of artisan description"),
    language_code: str = Form("hi", description="Spoken language code (e.g., hi, bn, ta, te)"),
    conversation_id: Optional[str] = Form(None, description="Existing conversation session UUID"),
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> VoiceProcessResponse:
    """
    End-to-end voice processing pipeline:
    Audio -> STT -> Craft/GI Detection -> LLM Extraction -> ML Pricing -> TTS Readback.
    """
    # 1. Read and validate raw audio upload
    raw_audio = await audio_file.read()
    if not validate_audio_bytes(raw_audio):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or empty audio file provided",
        )

    # 2. Normalize audio to WAV 16kHz mono for STT engines
    try:
        normalized_audio = normalize_audio_to_wav(raw_audio)
    except Exception as exc:
        logger.error("Audio normalization failed: {}", exc)
        normalized_audio = raw_audio

    # 3. Speech-to-Text transcription (Sarvam with Whisper fallback)
    transcript = await transcribe_audio(
        audio_bytes=normalized_audio,
        language_code=language_code,
    )
    if not transcript or not transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not detect clear speech in the audio recording. Please speak clearly and retry.",
        )

    logger.info("Artisan {}: Transcribed {} chars of speech", artisan.id, len(transcript))

    # 4. Craft and GI Tag keyword detection
    craft_match = match_craft_and_gi(
        transcript=transcript,
        artisan_state=artisan.state,
    )

    # 5. LLM extraction and bilingual description generation (Groq Llama 3.3)
    llm_result = await process_voice_transcription(
        transcript=transcript,
        source_language=language_code,
        artisan_context={
            "name": artisan.name,
            "state": artisan.state,
            "craft_lineage": artisan.craft_lineage,
            "matched_craft": craft_match.craft_type if craft_match else None,
        },
    )

    # 6. Dynamic ML pricing estimation
    pricing_req = PricingRequest(
        craft_type=llm_result.extracted_fields.craft_type or (craft_match.craft_type if craft_match else "handicraft"),
        material=llm_result.extracted_fields.material or "other",
        length_cm=llm_result.extracted_fields.length_cm or 15.0,
        width_cm=llm_result.extracted_fields.width_cm or 15.0,
        height_cm=llm_result.extracted_fields.height_cm or 15.0,
        weight_g=llm_result.extracted_fields.weight_g or 500.0,
    )
    pricing_result = await get_price_suggestion(pricing_req)

    # 7. Generate readback audio confirmation in native tongue (Sarvam TTS with Edge TTS fallback)
    readback_text = llm_result.readback_text or (
        f"Aapka product {llm_result.extracted_fields.title_native or 'kala'} "
        f"INR {pricing_result.suggested_price} me darj kiya gaya hai. Kya yeh theek hai?"
    )
    tts_audio_bytes = await synthesize_speech(
        text=readback_text,
        language_code=language_code,
    )
    audio_b64 = base64.b64encode(tts_audio_bytes).decode("utf-8") if tts_audio_bytes else ""

    # 8. Manage Conversation session state in PostgreSQL
    session_id = uuid.UUID(conversation_id) if conversation_id else uuid.uuid4()
    stmt = select(Conversation).where(Conversation.id == session_id)
    res = await db.execute(stmt)
    conv = res.scalar_one_or_none()

    extracted_fields_data = ExtractedProductFields(
        title_en=llm_result.extracted_fields.title_en,
        title_hi=llm_result.extracted_fields.title_native,
        title_native=llm_result.extracted_fields.title_native,
        craft_type=llm_result.extracted_fields.craft_type or "handicraft",
        material=llm_result.extracted_fields.material or "other",
        description_en=llm_result.extracted_fields.description_en,
        description_native=llm_result.extracted_fields.description_native,
        length_cm=llm_result.extracted_fields.length_cm,
        width_cm=llm_result.extracted_fields.width_cm,
        height_cm=llm_result.extracted_fields.height_cm,
        weight_g=llm_result.extracted_fields.weight_g,
        gi_tag=craft_match.gi_tag_name if craft_match else None,
    )

    extracted_dict = extracted_fields_data.model_dump()
    extracted_dict["pricing"] = pricing_result.model_dump()
    if craft_match:
        extracted_dict["gi_tag"] = craft_match.model_dump()

    if conv:
        conv.raw_transcript = transcript
        conv.extracted_fields = extracted_dict
        conv.language = language_code
        conv.status = "awaiting_approval"
    else:
        conv = Conversation(
            id=session_id,
            artisan_id=artisan.id,
            raw_transcript=transcript,
            extracted_fields=extracted_dict,
            language=language_code,
            status="awaiting_approval",
        )
        db.add(conv)

    await db.commit()

    return VoiceProcessResponse(
        conversation_id=str(session_id),
        transcript=transcript,
        raw_transcript=transcript,
        language_detected=language_code,
        extracted_fields=extracted_fields_data,
        pricing=pricing_result,
        gi_match=craft_match,
        readback_text=readback_text,
        readback_audio_base64=audio_b64,
        confidence_score=llm_result.confidence_score,
    )


@router.post(
    "/synthesize",
    response_model=SynthesizeResponse,
    summary="Synthesize arbitrary text to speech audio",
    status_code=status.HTTP_200_OK,
)
async def synthesize_text(
    payload: SynthesizeRequest,
    artisan: Artisan = Depends(get_current_artisan),
) -> SynthesizeResponse:
    """Convert text into speech audio for native voice UI prompts."""
    audio_bytes = await synthesize_speech(
        text=payload.text,
        language_code=payload.language_code,
    )
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Speech synthesis failed across both primary and fallback engines",
        )

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return SynthesizeResponse(
        audio_base64=audio_b64,
        content_type="audio/wav",
        language_code=payload.language_code,
    )


@router.post(
    "/approve",
    summary="Approve or adjust catalog fields extracted from voice session",
    status_code=status.HTTP_200_OK,
)
async def approve_voice_listing(
    payload: VoiceApprovalRequest,
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Lock conversation extracted fields upon artisan voice or touch confirmation."""
    stmt = select(Conversation).where(
        Conversation.id == payload.conversation_id,
        Conversation.artisan_id == artisan.id,
    )
    res = await db.execute(stmt)
    conv = res.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice conversation session not found",
        )

    conv.status = "approved" if payload.is_approved else "rejected"
    if payload.corrected_fields:
        current_data = dict(conv.extracted_fields or {})
        current_data.update(payload.corrected_fields)
        conv.extracted_fields = current_data

    await db.commit()
    logger.info("Conversation {} status updated to {}", conv.id, conv.status)

    return {
        "status": conv.status,
        "conversation_id": str(conv.id),
        "message": "Voice catalog draft approved successfully" if payload.is_approved else "Voice catalog draft rejected",
    }