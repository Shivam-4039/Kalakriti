"""Image router — Vision processing, background removal, and studio quality enhancement."""

import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field

from app.models.artisan import Artisan
from app.routers.auth import get_current_artisan
from app.services.image_service import process_artisan_image
from app.services.supabase_service import upload_file
from app.utils.image import correct_image_orientation, create_optimized_thumbnail
from app.utils.logger import logger

router = APIRouter(prefix="/image", tags=["Image Enhancement"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ImageEnhanceResponse(BaseModel):
    raw_image_url: str = Field(..., description="Public Supabase URL of raw captured photo")
    enhanced_image_url: str = Field(..., description="Public Supabase URL of studio-enhanced photo")
    width: int = 1080
    height: int = 1080
    format: str = "JPEG"
    message: str = "Image enhanced successfully"


class ThumbnailResponse(BaseModel):
    thumbnail_url: str = Field(..., description="Public Supabase URL of optimized thumbnail")
    width: int
    height: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post(
    "/enhance",
    response_model=ImageEnhanceResponse,
    summary="Enhance raw artisan photo to studio quality",
    status_code=status.HTTP_200_OK,
)
async def enhance_product_image(
    image: UploadFile = File(..., description="Raw handicraft photo captured by phone camera"),
    artisan: Artisan = Depends(get_current_artisan),
) -> ImageEnhanceResponse:
    """
    1. Read and validate raw image bytes.
    2. Correct EXIF orientation transpose.
    3. Remove background via rembg U2-Net, enhance with CLAHE, compose on 1080x1080 white canvas.
    4. Upload both raw and studio-enhanced versions to Supabase Storage bucket 'products'.
    """
    raw_bytes = await image.read()
    if not raw_bytes or len(raw_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or empty image file uploaded",
        )

    # 1. Correct mobile EXIF orientation
    try:
        oriented_raw_bytes = correct_image_orientation(raw_bytes)
    except Exception as exc:
        logger.warning("Orientation correction skipped: {}", exc)
        oriented_raw_bytes = raw_bytes

    # 2. Run vision enhancement pipeline (rembg + OpenCV)
    try:
        enhanced_bytes = await process_artisan_image(oriented_raw_bytes)
    except Exception as exc:
        logger.error("Studio image enhancement failed: {}", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process image enhancement. Please retry.",
        )

    # 3. Store assets in Supabase Storage
    unique_id = uuid.uuid4().hex[:12]
    raw_filename = f"artisan_{artisan.id}/raw_{unique_id}.jpg"
    enhanced_filename = f"artisan_{artisan.id}/enhanced_{unique_id}.jpg"

    raw_url = await upload_file(
        bucket_name="products",
        file_path=raw_filename,
        file_bytes=oriented_raw_bytes,
        content_type="image/jpeg",
    )

    enhanced_url = await upload_file(
        bucket_name="products",
        file_path=enhanced_filename,
        file_bytes=enhanced_bytes,
        content_type="image/jpeg",
    )

    if not raw_url or not enhanced_url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to persist enhanced assets to cloud storage",
        )

    logger.info("Enhanced image uploaded for artisan {}: {}", artisan.id, enhanced_url)

    return ImageEnhanceResponse(
        raw_image_url=raw_url,
        enhanced_image_url=enhanced_url,
        width=1080,
        height=1080,
        format="JPEG",
        message="Studio enhancement complete with pure white background",
    )


@router.post(
    "/thumbnail",
    response_model=ThumbnailResponse,
    summary="Generate optimized thumbnail for fast mobile grid",
    status_code=status.HTTP_200_OK,
)
async def generate_thumbnail(
    image: UploadFile = File(..., description="Image file to create thumbnail from"),
    artisan: Artisan = Depends(get_current_artisan),
) -> ThumbnailResponse:
    """Generate a lightweight thumbnail (max 400x400) for catalog list view."""
    raw_bytes = await image.read()
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image file provided",
        )

    try:
        thumb_bytes = create_optimized_thumbnail(raw_bytes, max_dimension=400)
    except Exception as exc:
        logger.error("Thumbnail generation error: {}", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Thumbnail generation failed",
        )

    thumb_filename = f"artisan_{artisan.id}/thumb_{uuid.uuid4().hex[:8]}.jpg"
    thumb_url = await upload_file(
        bucket_name="products",
        file_path=thumb_filename,
        file_bytes=thumb_bytes,
        content_type="image/jpeg",
    )

    if not thumb_url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to upload thumbnail",
        )

    return ThumbnailResponse(
        thumbnail_url=thumb_url,
        width=400,
        height=400,
    )