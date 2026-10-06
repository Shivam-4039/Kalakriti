# Kalakriti/Backend/app/schemas/__init__.py

from app.schemas.artisan import (
    ArtisanCreate,
    ArtisanResponse,
    ArtisanUpdate,
)
from app.schemas.b2b import (
    B2BInquiryCreate,
    B2BInquiryResponse,
    B2BInquiryUpdate,
    B2BStatus,
)
from app.schemas.ondc import (
    ONDCItemSchema,
    ONDCPublishRequest,
    ONDCPublishResponse,
)
from app.schemas.pricing import PricingRequest, PricingResponse
from app.schemas.product import (
    ONDCStatus,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.voice import (
    ExtractedProductFields,
    VoiceApprovalRequest,
    VoiceProcessResponse,
)

__all__ = [
    # Artisan
    "ArtisanCreate",
    "ArtisanUpdate",
    "ArtisanResponse",
    # Product
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ONDCStatus",
    # Voice
    "ExtractedProductFields",
    "VoiceProcessResponse",
    "VoiceApprovalRequest",
    # Pricing
    "PricingRequest",
    "PricingResponse",
    # ONDC
    "ONDCItemSchema",
    "ONDCPublishRequest",
    "ONDCPublishResponse",
    # B2B
    "B2BInquiryCreate",
    "B2BInquiryUpdate",
    "B2BInquiryResponse",
    "B2BStatus",
]