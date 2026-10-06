# Kalakriti/Backend/app/models/product.py

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    artisan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artisans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # --- Listing content ---
    title_en: Mapped[str] = mapped_column(String(200), nullable=False)
    title_hi: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description_en: Mapped[str] = mapped_column(Text, nullable=False)
    description_hi: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Classification ---
    craft_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    material: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gi_tag: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    # --- Dimensions (cm) ---
    length_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    width_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_grams: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # --- Pricing ---
    suggested_price: Mapped[float] = mapped_column(Float, nullable=False)
    final_price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")

    # --- Media ---
    image_urls: Mapped[list[str]] = mapped_column(
        ARRAY(Text), default=list, nullable=False
    )

    # --- ONDC integration ---
    ondc_status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False
    )  # draft | pending | published | unlisted | failed
    ondc_item_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    artisan: Mapped["Artisan"] = relationship(back_populates="products")  # noqa: F821

    # Compatibility properties
    @property
    def is_active(self) -> bool:
        return self.ondc_status != "unlisted"

    @is_active.setter
    def is_active(self, value: bool) -> None:
        if not value:
            self.ondc_status = "unlisted"
        elif self.ondc_status == "unlisted":
            self.ondc_status = "draft"

    @property
    def gi_tag_name(self) -> str | None:
        return self.gi_tag

    @property
    def is_gi_certified(self) -> bool:
        return bool(self.gi_tag)

    @property
    def gi_proof_url(self) -> str | None:
        return None

    @property
    def weight_g(self) -> float | None:
        return float(self.weight_grams) if self.weight_grams is not None else None

    @property
    def title_native(self) -> str | None:
        return self.title_hi

    @property
    def description_native(self) -> str | None:
        return self.description_hi

    @property
    def raw_image_url(self) -> str | None:
        return self.image_urls[0] if self.image_urls else None

    @property
    def enhanced_image_urls(self) -> list[str]:
        return self.image_urls

    @property
    def artisan_story(self) -> str | None:
        return None

    @property
    def dimensions(self) -> dict[str, Any] | None:
        if self.length_cm or self.width_cm or self.height_cm:
            return {
                "length_cm": self.length_cm,
                "width_cm": self.width_cm,
                "height_cm": self.height_cm,
            }
        return None

    def __repr__(self) -> str:
        return f"<Product {self.title_en} (INR {self.final_price})>"