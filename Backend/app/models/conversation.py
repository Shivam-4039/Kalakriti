# Kalakriti/Backend/app/models/conversation.py

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    artisan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artisans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # --- Voice session data ---
    language: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # BCP-47 code: "hi", "te", "ta"
    raw_transcript: Mapped[str] = mapped_column(Text, nullable=False)
    translated_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Structured fields extracted by LLM from the transcript.
    # Example: {"product_type": "saree", "material": "silk", "color": "red"}
    extracted_fields: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # --- Session state ---
    status: Mapped[str] = mapped_column(
        String(20), default="in_progress", nullable=False
    )  # in_progress | pending_approval | approved | rejected

    # Links to the product created after approval (null until approved)
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Conversation {self.id} [{self.status}]>"