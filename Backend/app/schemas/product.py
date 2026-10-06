"""Product catalog schemas — Pydantic models for artisan products and ONDC listings."""

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


ONDCStatus = Literal["draft", "pending", "published", "unlisted", "failed"]


class ProductBase(BaseModel):
    title_en: str = Field(..., min_length=3, max_length=200, examples=["Handwoven Pochampally Ikat Silk Saree"])
    title_hi: Optional[str] = Field(default=None, max_length=200, examples=["हथकरघा पोचमपल्ली इकत सिल्क साड़ी"])
    title_native: Optional[str] = Field(default=None, max_length=200, description="Alias for title in native language")
    
    description_en: str = Field(..., min_length=10, examples=["Authentic handwoven silk saree with geometric patterns..."])
    description_hi: Optional[str] = Field(default=None, examples=["पारंपरिक ज्यामितीय पैटर्न वाली प्रामाणिक रेशम साड़ी..."])
    description_native: Optional[str] = Field(default=None, description="Alias for description in native language")

    craft_type: str = Field(..., min_length=2, max_length=100, examples=["Ikat Weaving"])
    material: str = Field(..., min_length=2, max_length=100, examples=["Mulberry Silk"])
    color: Optional[str] = Field(default=None, max_length=50, examples=["Crimson Red"])
    gi_tag: Optional[str] = Field(default=None, max_length=50, examples=["GI-123"])
    gi_tag_name: Optional[str] = Field(default=None, max_length=150, description="Official GI Tag Name")
    is_gi_certified: bool = Field(default=False)

    length_cm: Optional[float] = Field(default=None, gt=0, examples=[550.0])
    width_cm: Optional[float] = Field(default=None, gt=0, examples=[115.0])
    height_cm: Optional[float] = Field(default=None, gt=0, examples=[0.2])
    weight_grams: Optional[int] = Field(default=None, gt=0, examples=[600])
    weight_g: Optional[float] = Field(default=None, gt=0, description="Alias for weight in grams")

    suggested_price: float = Field(..., gt=0, description="ML-generated price suggestion in INR", examples=[4500.0])
    final_price: float = Field(..., gt=0, description="Artisan-approved listing price in INR", examples=[4200.0])
    currency: str = Field(default="INR", max_length=3)

    image_urls: list[str] = Field(default_factory=list, description="Public URLs from Supabase Storage")
    raw_image_url: Optional[str] = Field(default=None)
    enhanced_image_urls: list[str] = Field(default_factory=list)
    artisan_story: Optional[str] = Field(default=None)


class ProductCreate(ProductBase):
    artisan_id: Optional[uuid.UUID] = Field(default=None, description="Set automatically from auth token")

    @field_validator("image_urls")
    @classmethod
    def validate_image_urls(cls, urls: list[str]) -> list[str]:
        return urls


class ProductUpdate(BaseModel):
    title_en: Optional[str] = Field(default=None, min_length=3, max_length=200)
    title_hi: Optional[str] = Field(default=None, max_length=200)
    title_native: Optional[str] = None
    description_en: Optional[str] = Field(default=None, min_length=10)
    description_hi: Optional[str] = None
    description_native: Optional[str] = None
    craft_type: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    gi_tag: Optional[str] = None
    length_cm: Optional[float] = Field(default=None, gt=0)
    width_cm: Optional[float] = Field(default=None, gt=0)
    height_cm: Optional[float] = Field(default=None, gt=0)
    weight_grams: Optional[int] = Field(default=None, gt=0)
    final_price: Optional[float] = Field(default=None, gt=0)
    image_urls: Optional[list[str]] = None
    ondc_status: Optional[ONDCStatus] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: uuid.UUID
    artisan_id: uuid.UUID
    ondc_status: ONDCStatus
    ondc_item_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    limit: int