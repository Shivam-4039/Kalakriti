"""QR Phygital Bridge Router — Public artisan story resolution and QR tag generation."""

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.artisan import Artisan
from app.models.product import Product
from app.utils.logger import logger

router = APIRouter(prefix="/qr", tags=["QR Phygital Bridge"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ArtisanStorySnippet(BaseModel):
    id: uuid.UUID
    name: Optional[str] = None
    state: Optional[str] = None
    craft_lineage: Optional[str] = None
    profile_photo_url: Optional[str] = None


class ProductQRStoryResponse(BaseModel):
    product_id: uuid.UUID
    title: str
    craft_type: str
    material: Optional[str] = None
    price: Optional[float] = None
    images: list[str] = []
    artisan_story: Optional[str] = None
    gi_tag_name: Optional[str] = None
    is_gi_certified: bool = False
    gi_proof_url: Optional[str] = None
    dimensions: Optional[dict[str, Any]] = None
    weight_g: Optional[float] = None
    artisan: ArtisanStorySnippet


class QRLinkResponse(BaseModel):
    product_id: uuid.UUID
    qr_payload_url: str = Field(..., description="Target web resolution URL encoded in QR")
    printable_label: str = Field(..., description="Human readable label for packaging tag")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get(
    "/product/{product_id}",
    response_model=ProductQRStoryResponse,
    summary="Public scan resolver — Artisan story & GI tag proof",
    status_code=status.HTTP_200_OK,
)
async def get_product_qr_story(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProductQRStoryResponse:
    """
    Public endpoint triggered when a buyer scans a physical QR code on packaging.
    Returns product origin, GI certification details, and artisan heritage story.
    """
    stmt = (
        select(Product, Artisan)
        .join(Artisan, Product.artisan_id == Artisan.id)
        .where(Product.id == product_id, Product.ondc_status != "unlisted")
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craft item not found or listing is inactive",
        )

    product, artisan = row
    images = list(product.image_urls or [])

    dims = None
    if product.length_cm or product.width_cm or product.height_cm:
        dims = {
            "length_cm": product.length_cm,
            "width_cm": product.width_cm,
            "height_cm": product.height_cm,
        }

    weight = float(product.weight_grams) if product.weight_grams is not None else None
    gi_tag_val = product.gi_tag

    logger.info("Public QR scan resolved for product {} (Artisan: {})", product.id, artisan.id)

    return ProductQRStoryResponse(
        product_id=product.id,
        title=product.title_en or product.title_hi or "Handmade Indian Craft",
        craft_type=product.craft_type,
        material=product.material,
        price=product.final_price or product.suggested_price,
        images=images,
        artisan_story=artisan.craft_lineage,
        gi_tag_name=gi_tag_val,
        is_gi_certified=bool(gi_tag_val),
        gi_proof_url=None,
        dimensions=dims,
        weight_g=weight,
        artisan=ArtisanStorySnippet(
            id=artisan.id,
            name=artisan.name or "Master Artisan",
            state=artisan.state,
            craft_lineage=artisan.craft_lineage,
            profile_photo_url=None,
        ),
    )


@router.get(
    "/product/{product_id}/link",
    response_model=QRLinkResponse,
    summary="Get QR payload link for label printing",
    status_code=status.HTTP_200_OK,
)
async def get_qr_code_metadata(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> QRLinkResponse:
    """Generate the target scan URL to encode inside the frontend react-native-qrcode-svg component."""
    stmt = select(Product).where(Product.id == product_id, Product.ondc_status != "unlisted")
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Resolution URL points to public web view or mobile deep-link
    qr_url = f"https://kalakriti.app/story/{product.id}"
    label = f"{product.title_en or product.craft_type.title()} | Verified Handicraft"

    return QRLinkResponse(
        product_id=product.id,
        qr_payload_url=qr_url,
        printable_label=label,
    )