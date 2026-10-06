# Kalakriti/Backend/app/schemas/artisan.py

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ArtisanBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Ramesh Kumar"])
    village: str = Field(..., min_length=2, max_length=100, examples=["Pochampally"])
    state: str = Field(..., min_length=2, max_length=50, examples=["Telangana"])
    craft_lineage: str | None = Field(
        default=None,
        description="Generational background or history of the artisan's craft",
        examples=["3rd generation Ikat handloom weaver"],
    )
    languages: list[str] = Field(
        default_factory=lambda: ["hi"],
        description="BCP-47 language codes spoken by the artisan",
        examples=[["hi", "te"]],
    )


class ArtisanCreate(ArtisanBase):
    phone: str = Field(..., description="Indian mobile number (10 digits or with +91)")

    @field_validator("phone")
    @classmethod
    def normalize_indian_phone(cls, value: str) -> str:
        # Strip spaces, hyphens, and leading plus/zeros
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


class ArtisanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    village: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=50)
    craft_lineage: str | None = None
    languages: list[str] | None = None


class ArtisanResponse(ArtisanBase):
    id: uuid.UUID
    phone: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)