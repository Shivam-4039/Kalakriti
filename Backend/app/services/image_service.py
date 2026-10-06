"""Image Service — rembg U2-Net background removal, OpenCV CLAHE & White Balance, 1080x1080 studio canvas."""

import asyncio
import io
import uuid
import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

from app.config import settings
from app.services.supabase_service import upload_file
from app.utils.image import validate_and_normalize_image
from app.utils.logger import logger

# Pre-initialize U2-Net session once at startup to avoid repeated model loading overhead
try:
    _REMBG_SESSION = new_session(model_name="u2net")
except Exception as exc:
    logger.warning("Could not pre-initialize rembg U2-Net session: {}", exc)
    _REMBG_SESSION = None


def _enhance_cv2_pipeline(pil_image_rgba: Image.Image) -> Image.Image:
    """
    Applies OpenCV CLAHE contrast enhancement and automatic white balance
    to the RGB channels while preserving the alpha mask from rembg.
    """
    try:
        # Convert PIL RGBA to numpy array
        rgba_np = np.array(pil_image_rgba)
        bgr = cv2.cvtColor(rgba_np, cv2.COLOR_RGBA2BGR)
        alpha = rgba_np[:, :, 3]

        # 1. Automatic White Balance (Simple Grayworld Algorithm)
        if hasattr(cv2, "xphoto") and hasattr(cv2.xphoto, "createSimpleWB"):
            wb = cv2.xphoto.createSimpleWB()
            result_bgr = wb.balanceWhite(bgr)
        else:
            result_bgr = bgr

        # 2. Contrast Enhancement via CLAHE on the L (Luminance) channel in LAB color space
        lab = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l_channel)

        lab_enhanced = cv2.merge((l_enhanced, a_channel, b_channel))
        enhanced_bgr = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        # Recombine enhanced RGB with original alpha mask
        enhanced_rgba = np.dstack((enhanced_rgb, alpha))
        return Image.fromarray(enhanced_rgba)
    except Exception as exc:
        logger.warning("OpenCV image enhancement skipped: {}", exc)
        return pil_image_rgba


def _composite_on_white_canvas(
    foreground_rgba: Image.Image,
    canvas_size: tuple[int, int] = (1080, 1080)
) -> Image.Image:
    """Centers the product on a crisp white 1080x1080 canvas with comfortable 10% padding."""
    canvas = Image.new("RGB", canvas_size, (255, 255, 255))

    # Scale foreground to fit inside 90% of canvas
    max_w = int(canvas_size[0] * 0.9)
    max_h = int(canvas_size[1] * 0.9)

    fg_copy = foreground_rgba.copy()
    fg_copy.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

    # Center placement coordinates
    offset_x = (canvas_size[0] - fg_copy.width) // 2
    offset_y = (canvas_size[1] - fg_copy.height) // 2

    # Paste using alpha channel as mask
    if fg_copy.mode == "RGBA":
        canvas.paste(fg_copy, (offset_x, offset_y), mask=fg_copy.split()[3])
    else:
        canvas.paste(fg_copy, (offset_x, offset_y))

    return canvas


def _sync_vision_pipeline(normalized_bytes: bytes) -> bytes:
    """Synchronous CPU-bound image enhancement pipeline."""
    input_pil = Image.open(io.BytesIO(normalized_bytes))

    # Step A: U2-Net background removal
    logger.info("Executing rembg U2-Net background removal...")
    try:
        if _REMBG_SESSION:
            cutout_rgba = remove(input_pil, session=_REMBG_SESSION)
        else:
            cutout_rgba = remove(input_pil)
    except Exception as exc:
        logger.warning("rembg background removal fallback: {}", exc)
        cutout_rgba = input_pil.convert("RGBA")

    # Step B: OpenCV white-balance & CLAHE contrast boost
    logger.info("Applying OpenCV CLAHE lighting correction...")
    enhanced_rgba = _enhance_cv2_pipeline(cutout_rgba)

    # Step C: Compose on standardized 1080x1080 white canvas
    studio_image = _composite_on_white_canvas(enhanced_rgba)

    # Step D: Encode as high quality optimized JPEG
    out_buffer = io.BytesIO()
    studio_image.save(out_buffer, format="JPEG", quality=90, optimize=True)
    return out_buffer.getvalue()


async def process_artisan_image(image_bytes: bytes) -> bytes:
    """
    Public async interface for image enhancement pipeline.
    Called directly by routers/image.py.
    """
    if not image_bytes:
        return image_bytes

    try:
        normalized_bytes, _ = validate_and_normalize_image(image_bytes)
    except Exception:
        normalized_bytes = image_bytes

    return await asyncio.to_thread(_sync_vision_pipeline, normalized_bytes)


class ImageEnhancerService:
    async def process_and_upload(
        self,
        raw_image_bytes: bytes,
        original_filename: str = "product.jpg",
    ) -> str:
        """Full Image Studio pipeline with automatic Supabase upload."""
        enhanced_jpeg_bytes = await process_artisan_image(raw_image_bytes)

        destination_path = f"products/enhanced/{uuid.uuid4()}.jpg"
        public_url = await upload_file(
            bucket_name=settings.supabase_storage_bucket,
            file_path=destination_path,
            file_bytes=enhanced_jpeg_bytes,
            content_type="image/jpeg",
        )

        logger.info("Product image enhanced and uploaded: {}", public_url)
        return public_url or ""


image_enhancer_service = ImageEnhancerService()