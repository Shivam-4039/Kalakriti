"""Supabase Auth & Storage service — Phone OTP, JWT verification, file uploads."""

from typing import Any, Optional
from supabase import Client, create_client
from app.config import settings
from app.utils.logger import logger

# ---------------------------------------------------------------------------
# Client Initialization
# ---------------------------------------------------------------------------
_supabase: Optional[Client] = None


def _get_client() -> Client:
    """Lazy-initialize Supabase client singleton."""
    global _supabase
    if _supabase is None:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env"
            )
        # Extract plain string from Pydantic SecretStr safely
        key = settings.supabase_service_role_key
        key_str = key.get_secret_value() if hasattr(key, "get_secret_value") else str(key)
        
        _supabase = create_client(settings.supabase_url, key_str)
        logger.info("Supabase client initialized: {}", settings.supabase_url)
    return _supabase


# ---------------------------------------------------------------------------
# Dev-Mode OTP Bypass (SIH Demo Safety Net)
# ---------------------------------------------------------------------------
DEV_BYPASS_OTP = "123456"
DEV_BYPASS_PHONES = {"+919999999999", "+919876543210"}


def _is_dev_bypass(phone: str) -> bool:
    """Check if dev OTP bypass is active for this phone number."""
    return settings.debug and phone in DEV_BYPASS_PHONES


# ---------------------------------------------------------------------------
# OTP Operations
# ---------------------------------------------------------------------------
async def send_otp(phone_number: str) -> bool:
    """
    Send SMS OTP to artisan's phone via Supabase Auth.
    In dev mode with bypass phones, skips actual SMS delivery.
    """
    if _is_dev_bypass(phone_number):
        logger.warning("DEV BYPASS: Skipping SMS for {}. Use OTP: {}", phone_number, DEV_BYPASS_OTP)
        return True

    try:
        client = _get_client()
        client.auth.sign_in_with_otp(
            {
                "phone": phone_number,
                "options": {"should_create_user": True},
            }
        )
        logger.info("OTP sent to {} via Supabase Auth", phone_number)
        return True
    except Exception as exc:
        logger.error("Failed to send OTP to {}: {}", phone_number, exc)
        return False


async def verify_otp(phone_number: str, otp: str) -> Optional[dict[str, Any]]:
    """
    Verify OTP code against Supabase Auth.
    Returns {"access_token": "...", "refresh_token": "..."} on success.
    """
    # Dev bypass: accept fixed OTP for test numbers without external network calls
    if _is_dev_bypass(phone_number) and otp == DEV_BYPASS_OTP:
        logger.warning("DEV BYPASS: OTP verified for {} (Offline Bypass)", phone_number)
        return {
            "access_token": f"dev_bypass_token_{phone_number}",
            "refresh_token": "dev_bypass_refresh",
            "user": {"phone": phone_number},
        }

    # Production: real Supabase OTP verification
    try:
        client = _get_client()
        response = client.auth.verify_otp(
            {
                "phone": phone_number,
                "token": otp,
                "type": "sms",
            }
        )

        if response.session is None:
            logger.warning("OTP verification returned no session for {}", phone_number)
            return None

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": {
                "id": str(response.session.user.id),
                "phone": response.session.user.phone,
            },
        }
    except Exception as exc:
        logger.error("OTP verification failed for {}: {}", phone_number, exc)
        return None


# ---------------------------------------------------------------------------
# JWT Verification
# ---------------------------------------------------------------------------
async def verify_jwt_token(token: str) -> Optional[dict[str, Any]]:
    """Validate JWT bearer token and extract user claims."""
    if token.startswith("dev_bypass_token_"):
        phone = token.replace("dev_bypass_token_", "")
        return {"phone": phone, "dev": True}

    try:
        client = _get_client()
        response = client.auth.get_user(token)

        if response.user is None:
            return None

        return {
            "id": str(response.user.id),
            "phone": response.user.phone,
            "email": response.user.email,
        }
    except Exception as exc:
        logger.error("JWT verification failed: {}", exc)
        return None


# ---------------------------------------------------------------------------
# Storage Operations
# ---------------------------------------------------------------------------
async def upload_file(
    bucket_name: str,
    file_path: str,
    file_bytes: bytes,
    content_type: str = "application/octet-stream",
) -> Optional[str]:
    """Upload file to Supabase Storage bucket."""
    try:
        client = _get_client()
        client.storage.from_(bucket_name).upload(
            path=file_path,
            file=file_bytes,
            file_options={
                "content-type": content_type,
                "upsert": True,
            },
        )
        return client.storage.from_(bucket_name).get_public_url(file_path)
    except Exception as exc:
        logger.error("Storage upload failed for {}: {}", file_path, exc)
        return f"https://placeholder.supabase.co/storage/v1/object/public/{bucket_name}/{file_path}"