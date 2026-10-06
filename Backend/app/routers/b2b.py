"""B2B router — Bulk order inquiry processing and artisan lead management."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.artisan import Artisan
from app.models.b2b_inquiry import B2BInquiry
from app.models.product import Product
from app.routers.auth import get_current_artisan
from app.schemas.b2b import (
    B2BInquiryCreate,
    B2BInquiryListResponse,
    B2BInquiryResponse,
    B2BInquiryStatusUpdate,
)
from app.utils.logger import logger

router = APIRouter(prefix="/b2b", tags=["B2B Bulk Inquiries"])


@router.post(
    "/inquiries",
    response_model=B2BInquiryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a bulk purchase inquiry (Buyer facing)",
)
async def submit_b2b_inquiry(
    payload: B2BInquiryCreate,
    db: AsyncSession = Depends(get_db),
) -> B2BInquiryResponse:
    """Public endpoint for institutional buyers to submit bulk inquiry on a product."""
    product = None
    artisan_id = payload.artisan_id
    craft_type = payload.craft_type

    if payload.product_id:
        stmt = select(Product).where(
            Product.id == payload.product_id,
            Product.ondc_status != "unlisted",
        )
        res = await db.execute(stmt)
        product = res.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target product not found or no longer active",
            )
        artisan_id = product.artisan_id
        if not craft_type:
            craft_type = product.craft_type

    inquiry = B2BInquiry(
        product_id=product.id if product else payload.product_id,
        artisan_id=artisan_id,
        buyer_name=payload.buyer_name,
        buyer_organization=payload.buyer_organization,
        buyer_email=payload.buyer_email,
        buyer_phone=payload.buyer_phone,
        craft_type=craft_type or "handicraft",
        quantity=payload.quantity,
        target_budget_inr=payload.target_budget_inr,
        requirements_description=payload.requirements_description,
        status="pending",
    )

    db.add(inquiry)
    await db.commit()
    await db.refresh(inquiry)

    logger.info(
        "New B2B inquiry created: ID {} for product {} by {}",
        inquiry.id,
        inquiry.product_id,
        payload.buyer_name,
    )

    return B2BInquiryResponse.model_validate(inquiry)


@router.get(
    "/inquiries",
    response_model=B2BInquiryListResponse,
    summary="List all bulk inquiries for the authenticated artisan",
)
async def list_artisan_inquiries(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, reviewed, matched, fulfilled, closed"),
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> B2BInquiryListResponse:
    """Retrieve paginated bulk inquiries received by the authenticated artisan."""
    query = select(B2BInquiry).where(B2BInquiry.artisan_id == artisan.id)

    if status_filter:
        query = query.where(B2BInquiry.status == status_filter)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * limit
    paginated_query = query.order_by(B2BInquiry.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(paginated_query)
    inquiries = result.scalars().all()

    return B2BInquiryListResponse(
        items=[B2BInquiryResponse.model_validate(item) for item in inquiries],
        total=total,
        page=page,
        limit=limit,
    )


@router.patch(
    "/inquiries/{inquiry_id}/status",
    response_model=B2BInquiryResponse,
    summary="Update inquiry processing status",
)
async def update_inquiry_status(
    inquiry_id: uuid.UUID,
    payload: B2BInquiryStatusUpdate,
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db),
) -> B2BInquiryResponse:
    """Update status of a received inquiry (e.g. pending -> reviewed -> fulfilled)."""
    stmt = select(B2BInquiry).where(
        B2BInquiry.id == inquiry_id,
        B2BInquiry.artisan_id == artisan.id,
    )
    res = await db.execute(stmt)
    inquiry = res.scalar_one_or_none()

    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found or access denied",
        )

    inquiry.status = payload.status
    await db.commit()
    await db.refresh(inquiry)

    logger.info("Inquiry {} updated to status '{}' by artisan {}", inquiry.id, inquiry.status, artisan.id)
    return B2BInquiryResponse.model_validate(inquiry)