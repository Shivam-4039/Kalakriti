"""Image utility helpers — Validation, EXIF orientation transpose, and thumbnail generation."""

import io
from PIL import Image, ImageOps
from app.config import settings
from app.utils.logger import logger

TARGET_SIZE = (1080, 1080)
JPEG_QUALITY = 85


def validate_and_normalize_image(
    raw_image_bytes: bytes,
    original_filename: str = "image.jpg",
) -> tuple[bytes, str]:
    """
    Validates uploaded image, corrects EXIF orientation, and resizes to 1080x1080 standard.
    Returns (normalized_bytes, format_string) e.g., (bytes, "JPEG").
    """
    # 1. Size check
    if len(raw_image_bytes) > settings.max_image_upload_bytes:
        raise ValueError(
            f"Image file size ({len(raw_image_bytes)} bytes) exceeds limit of "
            f"{settings.max_image_upload_bytes} bytes."
        )

    if len(raw_image_bytes) == 0:
        raise ValueError("Uploaded image file is empty.")

    # 2. Open and validate image format via Pillow
    try:
        image = Image.open(io.BytesIO(raw_image_bytes))
        image.verify()  # Verifies file integrity without decoding whole image
        # Re-open because verify() closes the stream
        image = Image.open(io.BytesIO(raw_image_bytes))
    except Exception as exc:
        logger.error("Failed to decode image {}: {}", original_filename, str(exc))
        raise ValueError(
            f"Invalid or corrupted image format for '{original_filename}'. "
            "Supported formats: JPEG, PNG, WEBP."
        ) from exc

    # 3. Correct EXIF orientation (fixes portrait photos taken on mobile)
    image = ImageOps.exif_transpose(image) or image

    # 4. Convert RGBA/Palette to RGB if saving as JPEG
    has_alpha = image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    )

    # 5. Resize to 1080x1080 max bounding box while keeping aspect ratio
    image.thumbnail(TARGET_SIZE, Image.Resampling.LANCZOS)

    # 6. Export to in-memory buffer
    output_buffer = io.BytesIO()
    if has_alpha:
        image.save(output_buffer, format="PNG", optimize=True)
        img_format = "PNG"
    else:
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(output_buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        img_format = "JPEG"

    normalized_bytes = output_buffer.getvalue()

    logger.info(
        "Image normalized: {} -> {} ({}x{}, {} bytes)",
        original_filename,
        img_format,
        image.width,
        image.height,
        len(normalized_bytes),
    )

    return normalized_bytes, img_format


def correct_image_orientation(image_bytes: bytes) -> bytes:
    """Fix image EXIF orientation transpose (common with mobile camera photos)."""
    if not image_bytes:
        return image_bytes

    try:
        image = Image.open(io.BytesIO(image_bytes))
        oriented_image = ImageOps.exif_transpose(image) or image

        if oriented_image.mode in ("RGBA", "P"):
            oriented_image = oriented_image.convert("RGB")

        output_buffer = io.BytesIO()
        oriented_image.save(output_buffer, format="JPEG", quality=JPEG_QUALITY)
        return output_buffer.getvalue()

    except Exception as exc:
        logger.warning("EXIF orientation correction skipped: {}", exc)
        return image_bytes


def create_optimized_thumbnail(image_bytes: bytes, max_dimension: int = 400) -> bytes:
    """Generate a compressed thumbnail for fast mobile grid rendering."""
    if not image_bytes:
        return image_bytes

    try:
        image = Image.open(io.BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image) or image

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        output_buffer = io.BytesIO()
        image.save(output_buffer, format="JPEG", quality=80, optimize=True)
        return output_buffer.getvalue()

    except Exception as exc:
        logger.error("Failed to generate thumbnail: {}", exc)
        return image_bytes