"""LLM Service — Single-shot extraction, translation, description, and readback script using Groq Llama 3.3 70B."""

import json
import random
from typing import Any, Optional
import httpx
from pydantic import BaseModel, Field

from app.config import settings
from app.utils.logger import logger


class VoiceExtractedFields(BaseModel):
    title_native: Optional[str] = Field(None, description="Product title in spoken native language")
    title_en: Optional[str] = Field(None, description="Product title translated to English")
    description_native: Optional[str] = Field(None, description="Detailed product description in native language")
    description_en: Optional[str] = Field(None, description="Market-ready product description in English")
    craft_type: Optional[str] = Field("handicraft", description="Detected craft category")
    material: Optional[str] = Field("other", description="Primary raw material used")
    length_cm: Optional[float] = Field(15.0, description="Estimated length in cm")
    width_cm: Optional[float] = Field(15.0, description="Estimated width in cm")
    height_cm: Optional[float] = Field(15.0, description="Estimated height in cm")
    weight_g: Optional[float] = Field(500.0, description="Estimated weight in grams")


class LLMVoiceProcessResult(BaseModel):
    extracted_fields: VoiceExtractedFields
    readback_text: str
    confidence_score: float = 0.85


SYSTEM_PROMPT = """You are Kalakriti AI, a virtual business manager for marginalized Indian artisans.
Your task is to analyze spoken transcript recordings and extract structured handicraft listing details.

Return ONLY a valid JSON object with NO markdown formatting, NO backticks, and NO extra text:
{
  "title_native": "Title in native spoken language",
  "title_en": "Professional product title in English",
  "description_native": "Appealing product description in native language",
  "description_en": "Market-ready, attractive e-commerce description in English",
  "craft_type": "One of: pottery, handloom, woodwork, metalwork, jewelry, painting, embroidery, basketry, stone_carving, lacquerware",
  "material": "One of: clay, cotton, silk, wood, brass, silver, gold, bamboo, stone, lac, wool, jute, iron, copper, other",
  "length_cm": 15.0,
  "width_cm": 15.0,
  "height_cm": 15.0,
  "weight_g": 500.0,
  "readback_text": "Short spoken confirmation sentence in native language asking artisan to verify details"
}"""


def _get_random_groq_key() -> str:
    """Rotate Groq API key to respect rate limits."""
    keys = settings.groq_api_key_list
    if not keys or keys[0] == "placeholder_groq_key":
        return ""
    return random.choice(keys)


async def process_voice_transcription(
    transcript: str,
    source_language: str = "hi",
    artisan_context: Optional[dict[str, Any]] = None,
) -> LLMVoiceProcessResult:
    """
    Passes voice transcript to Groq Llama 3.3 70B to extract structured fields,
    generate bilingual descriptions, and build spoken read-back prompt.
    """
    api_key = _get_random_groq_key()

    # Fallback default response if no Groq API key is supplied yet
    if not api_key:
        logger.warning("No Groq API key found — using heuristic extraction fallback")
        fields = VoiceExtractedFields(
            title_native=transcript[:30] if transcript else "हस्तशिल्प उत्पाद",
            title_en="Handcrafted Artisan Product",
            description_native=transcript or "हाथ से बनाया गया उत्पाद",
            description_en=f"Handcrafted Indian product. Raw transcript: {transcript}",
            craft_type=artisan_context.get("matched_craft") if artisan_context else "handicraft",
            material="other",
            length_cm=15.0,
            width_cm=15.0,
            height_cm=15.0,
            weight_g=500.0,
        )
        return LLMVoiceProcessResult(
            extracted_fields=fields,
            readback_text=f"Aapka product '{fields.title_native}' darj kar liya gaya hai. Kya yeh sahi hai?",
            confidence_score=0.70,
        )

    prompt = f"Spoken Transcript: '{transcript}'\nLanguage Code: '{source_language}'"
    if artisan_context:
        prompt += f"\nArtisan Context: {json.dumps(artisan_context)}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=settings.groq_timeout_seconds) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            logger.error("Groq API error ({}): {}", response.status_code, response.text)
            raise ValueError(f"Groq API returned status {response.status_code}")

        data = response.json()
        raw_content = data["choices"][0]["message"]["content"]
        parsed = json.loads(raw_content)

        fields = VoiceExtractedFields(
            title_native=parsed.get("title_native"),
            title_en=parsed.get("title_en"),
            description_native=parsed.get("description_native"),
            description_en=parsed.get("description_en"),
            craft_type=parsed.get("craft_type", "handicraft"),
            material=parsed.get("material", "other"),
            length_cm=float(parsed.get("length_cm", 15.0)),
            width_cm=float(parsed.get("width_cm", 15.0)),
            height_cm=float(parsed.get("height_cm", 15.0)),
            weight_g=float(parsed.get("weight_g", 500.0)),
        )

        readback = parsed.get(
            "readback_text",
            f"Aapka product '{fields.title_native}' darj kiya gaya hai. Kya yeh theek hai?",
        )

        return LLMVoiceProcessResult(
            extracted_fields=fields,
            readback_text=readback,
            confidence_score=0.90,
        )

    except Exception as exc:
        logger.error("LLM extraction failed, using safe fallback: {}", exc)
        fields = VoiceExtractedFields(
            title_native=transcript[:30] if transcript else "हस्तशिल्प उत्पाद",
            title_en="Handcrafted Artisan Product",
            description_native=transcript or "हाथ से बनाया गया उत्पाद",
            description_en=f"Handcrafted product: {transcript}",
        )
        return LLMVoiceProcessResult(
            extracted_fields=fields,
            readback_text="Aapka product darj kar liya gaya hai. Kripya check karein.",
            confidence_score=0.50,
        )