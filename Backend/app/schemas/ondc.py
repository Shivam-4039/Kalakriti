# Kalakriti/Backend/app/schemas/ondc.py

import uuid
from typing import Any

from pydantic import BaseModel, Field


class ONDCPrice(BaseModel):
    currency: str = "INR"
    value: str = Field(..., description="String representation of price per Beckn spec, e.g. '4200.00'")


class ONDCDescriptor(BaseModel):
    name: str
    code: str | None = None
    symbol: str | None = None
    short_desc: str
    long_desc: str
    images: list[str]


class ONDCCategory(BaseModel):
    id: str = "RET10"  # ONDC standard category code for Fashion/Handicrafts
    descriptor: dict[str, str] = {"name": "Handicrafts & Handlooms"}


class ONDCTag(BaseModel):
    code: str
    list: list[dict[str, str]]


class ONDCItemSchema(BaseModel):
    """ONDC Beckn Retail Catalog Item format for handicrafts."""

    id: str = Field(..., description="Unique product SKU identifier")
    parent_item_id: str | None = None
    descriptor: ONDCDescriptor
    price: ONDCPrice
    category_id: str = "RET10"
    fulfillment_id: str = "F1"
    matched: bool = True
    recommended: bool = False

    # Statutory mandatory fields for Indian commerce
    tags: list[ONDCTag] = Field(
        default_factory=lambda: [
            ONDCTag(
                code="origin",
                list=[{"code": "country", "value": "IND"}],
            ),
            ONDCTag(
                code="attribute",
                list=[
                    {"code": "handmade", "value": "yes"},
                    {"code": "sustainable", "value": "yes"},
                ],
            ),
        ]
    )


class ONDCPublishRequest(BaseModel):
    """Request to format and publish a product listing to ONDC network."""

    product_id: uuid.UUID


class ONDCPublishResponse(BaseModel):
    """Result of ONDC catalog publishing operation."""

    product_id: uuid.UUID
    ondc_item_id: str
    status: str = Field(..., description="published | failed | pending")
    network_transaction_id: str = Field(
        ..., description="Beckn transaction_id or mock ack ID"
    )
    raw_payload: dict[str, Any] = Field(
        ..., description="The full Beckn-compliant catalog item JSON"
    )
    message: str