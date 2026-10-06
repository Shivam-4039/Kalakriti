"""Pricing router — AI/ML dynamic pricing estimation for artisan catalog items."""

from fastapi import APIRouter, Depends, status

from app.models.artisan import Artisan
from app.routers.auth import get_current_artisan
from app.schemas.pricing import PricingRequest, PricingResponse
from app.services.pricing_service import get_price_suggestion
from app.utils.logger import logger

router = APIRouter(prefix="/pricing", tags=["Dynamic Pricing"])


@router.post(
    "/estimate",
    response_model=PricingResponse,
    status_code=status.HTTP_200_OK,
    summary="Estimate competitive price range using ML",
)
async def estimate_price(
    payload: PricingRequest,
    artisan: Artisan = Depends(get_current_artisan),
) -> PricingResponse:
    """
    Predict fair market price using GradientBoostingRegressor.
    Takes craft type, material, dimensions, and weight.
    Returns suggested price, min/max price bracket, and confidence score.
    """
    logger.info(
        "Pricing calculation requested by artisan {}: craft='{}', material='{}', weight={}g",
        artisan.id,
        payload.craft_type,
        payload.material,
        payload.weight_g,
    )

    pricing_result = await get_price_suggestion(payload)

    logger.info(
        "Pricing prediction completed: Suggested INR {} [{} - {}] (Conf: {})",
        pricing_result.suggested_price,
        pricing_result.price_min,
        pricing_result.price_max,
        pricing_result.confidence_score,
    )

    return pricing_result