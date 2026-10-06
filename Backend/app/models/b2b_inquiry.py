# Kalakriti/Backend/app/models/b2b_inquiry.py

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class B2BInquiry(Base):
    __tablename__ = "b2b_inquiries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Optional linkages: inquiry can target a specific product or artisan
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    artisan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artisans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # --- Buyer details ---
    buyer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    buyer_organization: Mapped[str] = mapped_column(String(150), nullable=False)
    buyer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    buyer_phone: Mapped[str] = mapped_column(String(15), nullable=False)

    # --- Order requirements ---
    craft_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    target_budget_inr: Mapped[float | None] = mapped_column(Float, nullable=True)
    requirements_description: Mapped[str] = mapped_column(Text, nullable=False)

    # --- Inquiry lifecycle ---
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending | reviewed | matched | fulfilled | closed

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<B2BInquiry from {self.buyer_organization} for {self.craft_type} (Qty: {self.quantity})>"