"""B2B schemas — Pydantic models for bulk purchase inquiries and lead management."""

import re
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

B2BStatus = Literal["pending", "reviewed", "matched", "fulfilled", "closed"]


class B2BInquiryBase(BaseModel):
    buyer_name: str = Field(..., min_length=2, max_length=100, examples=["Priya Sharma"])
    buyer_organization: str = Field(
        ..., min_length=2, max_length=150, examples=["Taj Hotels Procurement"]
    )
    buyer_email: EmailStr = Field(..., examples=["procurement@tajhotels.com"])
    buyer_phone: str = Field(..., examples=["+919876543210"])

    craft_type: str = Field(..., min_length=2, max_length=100, examples=["Blue Pottery"])
    quantity: int = Field(..., gt=0, examples=[500], description="Bulk order quantity (units)")
    target_budget_inr: float | None = Field(
        default=None, gt=0, examples=[250000.0], description="Total target budget in INR"
    )
    requirements_description: str = Field(
        ...,
        min_length=10,
        examples=["Need 500 ceramic dinner plates for new resort opening by Dec 2025."],
    )

    @field_validator("buyer_phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)]", "", value)
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        elif cleaned.startswith("0") and len(cleaned) == 11:
            cleaned = cleaned[1:]

        if not re.fullmatch(r"[6-9]\d{9}", cleaned):
            raise ValueError(
                "Invalid Indian mobile number. Must be 10 digits starting with 6, 7, 8, or 9."
            )
        return f"+91{cleaned}"


class B2BInquiryCreate(B2BInquiryBase):
    product_id: uuid.UUID | None = Field(
        default=None, description="Optional link to a specific product listing"
    )
    artisan_id: uuid.UUID | None = Field(
        default=None, description="Optional link to a specific artisan"
    )


class B2BInquiryUpdate(BaseModel):
    status: B2BStatus = Field(..., description="Updated inquiry status")


# Alias expected by routers/b2b.py
B2BInquiryStatusUpdate = B2BInquiryUpdate


class B2BInquiryResponse(B2BInquiryBase):
    id: uuid.UUID
    product_id: uuid.UUID | None = None
    artisan_id: uuid.UUID | None = None
    status: B2BStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class B2BInquiryListResponse(BaseModel):
    items: list[B2BInquiryResponse]
    total: int
    page: int
    limit: int