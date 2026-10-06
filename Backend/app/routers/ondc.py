"""ONDC Router — Beckn Protocol RET10 handicraft cataloging and network gateway integration."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.artisan import Artisan
from app.models.product import Product
from app.routers.auth import get_current_artisan
from app.services.ondc_service import build_ondc_catalog, publish_item_to_ondc
from app.utils.logger import logger

router = APIRouter(prefix="/ondc", tags=["ONDC Integration"])


@router.post(
    "/publish/{product_id}",
    summary="Publish catalog item to ONDC seller network",
    status_code=status.HTTP_200_OK,
)
async def publish_product_to_network(
    product_id: uuid.UUID,
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Validates product data, builds Beckn RET10 schema payload,
    simulates network publication, and updates database status to 'published'.
    """
    stmt = select(Product).where(
        Product.id == product_id,
        Product.artisan_id == artisan.id,
    )
    res = await db.execute(stmt)
    product = res.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Validation checks before publishing
    if not (product.final_price or product.suggested_price):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product must have a confirmed price before publishing to ONDC",
        )

    if not product.image_urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product must have at least one image before publishing to ONDC",
        )

    # Publish via ONDC service
    ondc_ack = await publish_item_to_ondc(product=product, artisan=artisan)

    # Update database status
    product.ondc_status = "published"
    await db.commit()

    logger.info("Product {} published to ONDC for artisan {}", product.id, artisan.id)

    return {
        "status": "success",
        "message": "Product published to ONDC network",
        "product_id": str(product.id),
        "ondc_receipt": ondc_ack,
    }


@router.post(
    "/unpublish/{product_id}",
    summary="Unlist product from ONDC seller network",
    status_code=status.HTTP_200_OK,
)
async def unpublish_product_from_network(
    product_id: uuid.UUID,
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Unlist active product from ONDC marketplace."""
    stmt = select(Product).where(
        Product.id == product_id,
        Product.artisan_id == artisan.id,
    )
    res = await db.execute(stmt)
    product = res.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    product.ondc_status = "unlisted"
    await db.commit()

    logger.info("Product {} unlisted from ONDC by artisan {}", product.id, artisan.id)

    return {
        "status": "success",
        "message": "Product unlisted from ONDC network",
        "product_id": str(product.id),
    }


@router.get(
    "/catalog",
    summary="Get full Beckn RET10 provider catalog for artisan",
    status_code=status.HTTP_200_OK,
)
async def get_artisan_ondc_catalog(
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Generate complete Beckn Provider Catalog payload for the artisan."""
    stmt = select(Product).where(
        Product.artisan_id == artisan.id,
        Product.ondc_status != "unlisted",
    )
    res = await db.execute(stmt)
    products = list(res.scalars().all())

    catalog_payload = build_ondc_catalog(artisan=artisan, products=products)
    return catalog_payload