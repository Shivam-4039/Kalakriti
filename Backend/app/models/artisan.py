# Kalakriti/Backend/app/models/artisan.py

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Artisan(Base):
    __tablename__ = "artisans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    phone: Mapped[str] = mapped_column(
        String(15), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    village: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    craft_lineage: Mapped[str | None] = mapped_column(Text, nullable=True)
    languages: Mapped[list[str]] = mapped_column(
        ARRAY(String(10)), default=list, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships defined here, back_populates in product.py
    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        back_populates="artisan", cascade="all, delete-orphan"
    )

    @property
    def phone_number(self) -> str:
        return self.phone

    @property
    def profile_photo_url(self) -> str | None:
        return None

    def __repr__(self) -> str:
        return f"<Artisan {self.name} ({self.phone})>"