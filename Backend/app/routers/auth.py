"""Authentication router — Phone OTP lifecycle and artisan session management."""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.artisan import Artisan
from app.schemas.artisan import ArtisanResponse, ArtisanUpdate
from app.services.supabase_service import (
    send_otp,
    verify_jwt_token,
    verify_otp,
)
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# ---------------------------------------------------------------------------
# Request/Response Schemas for Auth Flow
# ---------------------------------------------------------------------------
class SendOTPRequest(BaseModel):
    phone_number: str = Field(
        ...,
        pattern=r"^\+91[6-9]\d{9}$",
        description="E.164 formatted Indian phone number (+91XXXXXXXXXX)",
        examples=["+919876543210"]
    )


class VerifyOTPRequest(BaseModel):
    phone_number: str = Field(
        ...,
        pattern=r"^\+91[6-9]\d{9}$",
        description="E.164 formatted Indian phone number (+91XXXXXXXXXX)",
        examples=["+919876543210"]
    )
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit verification code",
        examples=["123456"]
    )


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    artisan: ArtisanResponse


# ---------------------------------------------------------------------------
# Auth Dependency
# ---------------------------------------------------------------------------
async def get_current_artisan(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
) -> Artisan:
    """Validate bearer token and resolve authenticated artisan from database."""
    token = credentials.credentials
    user_payload = await verify_jwt_token(token)
    if not user_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    phone = user_payload.get("phone") or user_payload.get("phone_number")
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing phone identity claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(Artisan).where(Artisan.phone == phone)
    result = await db.execute(stmt)
    artisan = result.scalar_one_or_none()

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artisan account not found",
        )

    return artisan


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post(
    "/send-otp",
    summary="Request SMS OTP for phone number",
    status_code=status.HTTP_200_OK
)
async def request_otp(payload: SendOTPRequest) -> dict[str, Any]:
    """Trigger SMS OTP delivery to artisan's mobile number."""
    success = await send_otp(payload.phone_number)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to dispatch OTP SMS. Verify phone number and retry."
        )

    logger.info("OTP dispatched successfully to {}", payload.phone_number)
    return {"message": "OTP sent successfully", "phone_number": payload.phone_number}


@router.post(
    "/verify-otp",
    response_model=AuthResponse,
    summary="Verify OTP and obtain access token",
    status_code=status.HTTP_200_OK
)
async def verify_and_authenticate(
    payload: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """Verify phone OTP, provision artisan profile if first login, return JWT session."""
    auth_result = await verify_otp(payload.phone_number, payload.otp)
    if not auth_result or "access_token" not in auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP code"
        )

    access_token = auth_result["access_token"]

    # Check if artisan exists in PostgreSQL; create if first login
    stmt = select(Artisan).where(Artisan.phone == payload.phone_number)
    result = await db.execute(stmt)
    artisan = result.scalar_one_or_none()

    if not artisan:
        logger.info("First-time login detected. Registering artisan {}", payload.phone_number)
        artisan = Artisan(
            phone=payload.phone_number,
            name=f"Artisan {payload.phone_number[-4:]}",
            village="Artisan Cluster",
            state="Rajasthan",
            craft_lineage="Traditional Handicraft Artisan",
            languages=["hi"]
        )
        db.add(artisan)
        await db.commit()
        await db.refresh(artisan)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        artisan=ArtisanResponse.model_validate(artisan)
    )


@router.get(
    "/me",
    response_model=ArtisanResponse,
    summary="Get current artisan profile",
    status_code=status.HTTP_200_OK
)
async def get_profile(
    artisan: Artisan = Depends(get_current_artisan)
) -> ArtisanResponse:
    """Fetch profile data for the authenticated artisan."""
    return ArtisanResponse.model_validate(artisan)


@router.put(
    "/me",
    response_model=ArtisanResponse,
    summary="Update artisan profile details",
    status_code=status.HTTP_200_OK
)
async def update_profile(
    update_data: ArtisanUpdate,
    artisan: Artisan = Depends(get_current_artisan),
    db: AsyncSession = Depends(get_db)
) -> ArtisanResponse:
    """Update name, village, state, lineage, or languages."""
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(artisan, field, value)

    await db.commit()
    await db.refresh(artisan)
    logger.info("Updated profile for artisan {}", artisan.id)
    return ArtisanResponse.model_validate(artisan)