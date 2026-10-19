"""Product catalog schemas — Pydantic models for artisan products and ONDC listings."""

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


ONDCStatus = Literal["draft", "pending", "published", "unlisted", "failed"]


class ProductBase(BaseModel):
    title_en: str = Field(..., min_length=1, max_length=200)
    title_hi: Optional[str] = Field(default=None, max_length=200)
    title_native: Optional[str] = Field(default=None, max_length=200)
    
    description_en: str = Field(..., min_length=1)
    description_hi: Optional[str] = Field(default=None)
    description_native: Optional[str] = Field(default=None)

    craft_type: str = Field(default="handmade", max_length=100)
    material: str = Field(default="other", max_length=100)
    color: Optional[str] = Field(default=None, max_length=50)
    gi_tag: Optional[str] = Field(default=None, max_length=50)
    gi_tag_name: Optional[str] = Field(default=None, max_length=150)
    is_gi_certified: bool = Field(default=False)

    length_cm: Optional[float] = Field(default=15.0, gt=0)
    width_cm: Optional[float] = Field(default=15.0, gt=0)
    height_cm: Optional[float] = Field(default=15.0, gt=0)
    weight_grams: Optional[int] = Field(default=500, gt=0)
    weight_g: Optional[float] = Field(default=500.0, gt=0)

    suggested_price: float = Field(default=500.0, ge=0)
    final_price: float = Field(default=500.0, ge=0)
    currency: str = Field(default="INR", max_length=3)

    image_urls: list[str] = Field(default_factory=list)
    raw_image_url: Optional[str] = Field(default=None)
    enhanced_image_urls: list[str] = Field(default_factory=list)
    artisan_story: Optional[str] = Field(default=None)


class ProductCreate(ProductBase):
    artisan_id: Optional[uuid.UUID] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def normalize_frontend_payload(cls, data: Any) -> Any:
        """Map frontend shorthand keys (title, description, price, image_url) to backend fields."""
        if not isinstance(data, dict):
            return data

        # Map title
        if "title" in data and not data.get("title_en"):
            data["title_en"] = data.get("title") or "Handcrafted Item"
        if not data.get("title_en"):
            data["title_en"] = "Handcrafted Item"

        # Map description
        if "description" in data and not data.get("description_en"):
            data["description_en"] = data.get("description") or "Handcrafted artisan product."
        if not data.get("description_en"):
            data["description_en"] = "Handcrafted artisan product."

        # Map material
        if not data.get("material") or len(str(data.get("material")).strip()) < 2:
            data["material"] = "clay"

        # Map prices
        price_val = data.get("price") or data.get("final_price") or data.get("suggested_price") or 500.0
        try:
            p_float = float(price_val)
        except (ValueError, TypeError):
            p_float = 500.0

        data["suggested_price"] = data.get("suggested_price") or p_float
        data["final_price"] = data.get("final_price") or p_float

        # Map image URLs
        urls = data.get("image_urls") or []
        if isinstance(urls, str):
            urls = [urls]
        if "image_url" in data and data["image_url"]:
            if data["image_url"] not in urls:
                urls.append(data["image_url"])
        if not urls:
            urls = ["https://placeholder.supabase.co/storage/v1/object/public/products/default.jpg"]
        
        data["image_urls"] = urls
        data["raw_image_url"] = data.get("raw_image_url") or urls[0]
        data["enhanced_image_urls"] = data.get("enhanced_image_urls") or urls

        return data


class ProductUpdate(BaseModel):
    title_en: Optional[str] = None
    title_hi: Optional[str] = None
    title_native: Optional[str] = None
    description_en: Optional[str] = None
    description_hi: Optional[str] = None
    description_native: Optional[str] = None
    craft_type: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    gi_tag: Optional[str] = None
    length_cm: Optional[float] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    weight_grams: Optional[int] = None
    final_price: Optional[float] = None
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