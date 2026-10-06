"""Pricing service — GradientBoostingRegressor with category-median fallback."""

import asyncio
import pickle
from pathlib import Path

import numpy as np

from app.config import settings
from app.schemas.pricing import PricingRequest, PricingResponse
from app.utils.logger import logger

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------
_model = None
_MODEL_PATH = Path(__file__).resolve().parents[3] / "AI_Model" / "pricing" / "model.pkl"

# Fixed encoding maps — MUST stay in sync with AI_Model/pricing/train.py
CRAFT_ENCODING = {
    "pottery": 0, "handloom": 1, "woodwork": 2, "metalwork": 3,
    "jewelry": 4, "painting": 5, "basketry": 6, "embroidery": 7,
    "stone_carving": 8, "lacquerware": 9,
}

MATERIAL_ENCODING = {
    "clay": 0, "cotton": 1, "silk": 2, "wood": 3, "brass": 4,
    "silver": 5, "gold": 6, "bamboo": 7, "stone": 8, "lac": 9,
    "wool": 10, "jute": 11, "iron": 12, "copper": 13, "other": 14,
}

# Fallback median prices (INR) when model.pkl is unavailable
FALLBACK_MEDIANS: dict[str, float] = {
    "pottery": 300, "handloom": 800, "woodwork": 1200, "metalwork": 1500,
    "jewelry": 2000, "painting": 1000, "basketry": 250, "embroidery": 600,
    "stone_carving": 2500, "lacquerware": 500,
}
DEFAULT_MEDIAN = 500.0


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
def init_pricing_model() -> None:
    """Load model.pkl into memory. Call once from FastAPI lifespan."""
    global _model
    if not _MODEL_PATH.exists():
        logger.warning("model.pkl not found at {} — using fallback medians", _MODEL_PATH)
        _model = None
        return
    try:
        with open(_MODEL_PATH, "rb") as fh:
            _model = pickle.load(fh)
        logger.info("Pricing model loaded ({})", _MODEL_PATH)
    except Exception as exc:
        logger.error("Failed to deserialize model.pkl: {}", exc)
        _model = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _encode(req: PricingRequest) -> np.ndarray:
    """Convert request fields to the 6-feature array the model expects."""
    craft_id = CRAFT_ENCODING.get(req.craft_type.strip().lower(), -1)
    material_id = MATERIAL_ENCODING.get(req.material.strip().lower(), 14)
    length = float(req.length_cm or 15.0)
    width = float(req.width_cm or 15.0)
    height = float(req.height_cm or 15.0)
    weight = float(req.weight_g if req.weight_g is not None else (req.weight_grams or 500.0))
    return np.array([[
        float(craft_id),
        float(material_id),
        length,
        width,
        height,
        weight,
    ]])


def _predict_sync(features: np.ndarray) -> tuple[float, float]:
    """CPU-bound sklearn predict — must run inside asyncio.to_thread."""
    raw = float(_model.predict(features)[0])
    # Simple confidence heuristic: predictions in the common range are more reliable
    confidence = 0.85 if 100.0 <= raw <= 10000.0 else 0.55
    return raw, confidence


def _clamp(value: float) -> float:
    """Enforce hard INR bounds from config."""
    return round(max(settings.price_min, min(settings.price_max, value)), 2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
async def get_price_suggestion(req: PricingRequest) -> PricingResponse:
    """Return suggested price with min/max range and confidence score."""

    # --- Fallback path: no model available ---
    if _model is None:
        median = FALLBACK_MEDIANS.get(req.craft_type.strip().lower(), DEFAULT_MEDIAN)
        suggested = _clamp(median)
        p_min = _clamp(suggested * 0.70)
        p_max = _clamp(suggested * 1.40)
        logger.info("Pricing fallback for '{}': INR {}", req.craft_type, suggested)
        return PricingResponse(
            suggested_price=suggested,
            price_min=p_min,
            price_max=p_max,
            suggested_price_inr=suggested,
            price_min_inr=p_min,
            price_max_inr=p_max,
            confidence_score=0.40,
        )

    # --- Model path ---
    try:
        features = _encode(req)
        raw_price, confidence = await asyncio.to_thread(_predict_sync, features)
    except Exception as exc:
        logger.error("Prediction failed, falling back to median: {}", exc)
        median = FALLBACK_MEDIANS.get(req.craft_type.strip().lower(), DEFAULT_MEDIAN)
        raw_price = median
        confidence = 0.35

    suggested = _clamp(raw_price)
    p_min = _clamp(suggested * 0.75)
    p_max = _clamp(suggested * 1.35)
    return PricingResponse(
        suggested_price=suggested,
        price_min=p_min,
        price_max=p_max,
        suggested_price_inr=suggested,
        price_min_inr=p_min,
        price_max_inr=p_max,
        confidence_score=round(confidence, 2),
    )