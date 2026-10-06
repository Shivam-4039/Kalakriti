"""Product catalog router — CRUD endpoints and catalog management for artisans."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.artisan import Artisan
from app.models.product import Product
from app.routers.auth import get_current_artisan
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.utils.logger import logger

router = APIRouter(prefix="/products", tags=["Product Catalog"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new catalog item",
)
async def create_product(
    payload: ProductCreate,
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Create a new product listing linked to the authenticated artisan."""
    image_urls = list(payload.image_urls or [])
    if not image_urls:
        if payload.raw_image_url:
            image_urls.append(payload.raw_image_url)
        elif payload.enhanced_image_urls:
            image_urls.extend(payload.enhanced_image_urls)

    weight_grams = payload.weight_grams
    if weight_grams is None and payload.weight_g is not None:
        weight_grams = int(payload.weight_g)

    gi_tag = payload.gi_tag or payload.gi_tag_name
    title_hi = payload.title_hi or payload.title_native
    description_hi = payload.description_hi or payload.description_native
    final_price = payload.final_price or payload.suggested_price

    product = Product(
        artisan_id=artisan.id,
        title_en=payload.title_en,
        title_hi=title_hi,
        description_en=payload.description_en,
        description_hi=description_hi,
        craft_type=payload.craft_type,
        material=payload.material,
        color=payload.color,
        gi_tag=gi_tag,
        length_cm=payload.length_cm,
        width_cm=payload.width_cm,
        height_cm=payload.height_cm,
        weight_grams=weight_grams,
        suggested_price=payload.suggested_price,
        final_price=final_price,
        currency=payload.currency or "INR",
        image_urls=image_urls,
        ondc_status="draft",
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    logger.info("Product created: {} by artisan {}", product.id, artisan.id)
    return ProductResponse.model_validate(product)


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List all products for the authenticated artisan",
)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    ondc_status: Optional[str] = Query(None, description="Filter by ONDC status (draft, published, unlisted)"),
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """Retrieve paginated list of catalog products for the current artisan."""
    query = select(Product).where(Product.artisan_id == artisan.id)

    if is_active is not None:
        if is_active:
            query = query.where(Product.ondc_status != "unlisted")
        else:
            query = query.where(Product.ondc_status == "unlisted")
    if ondc_status:
        query = query.where(Product.ondc_status == ondc_status)

    # Count total matching items
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination and sorting
    offset = (page - 1) * limit
    paginated_query = query.order_by(Product.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(paginated_query)
    products = result.scalars().all()

    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get single product details",
)
async def get_product(
    product_id: uuid.UUID,
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Fetch product by ID, verifying artisan ownership."""
    stmt = select(Product).where(
        Product.id == product_id,
        Product.artisan_id == artisan.id,
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product listing not found",
        )

    return ProductResponse.model_validate(product)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product details",
)
async def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Update editable fields of an existing product."""
    stmt = select(Product).where(
        Product.id == product_id,
        Product.artisan_id == artisan.id,
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product listing not found",
        )

    update_dict = payload.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if field == "gi_tag_name":
            product.gi_tag = value
        elif field == "weight_g" and value is not None:
            product.weight_grams = int(value)
        elif field == "title_native":
            product.title_hi = value
        elif field == "description_native":
            product.description_hi = value
        elif field == "is_active":
            product.is_active = value
        elif hasattr(product, field):
            setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    logger.info("Product {} updated by artisan {}", product.id, artisan.id)
    return ProductResponse.model_validate(product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft delete a product listing",
)
async def delete_product(
    product_id: uuid.UUID,
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Soft delete product by setting ondc_status to 'unlisted'."""
    stmt = select(Product).where(
        Product.id == product_id,
        Product.artisan_id == artisan.id,
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product listing not found",
        )

    product.ondc_status = "unlisted"
    await db.commit()

    logger.info("Product {} soft-deleted by artisan {}", product.id, artisan.id)
    return {"message": "Product deactivated successfully", "product_id": str(product.id)}