"""ONDC Service — Formats catalog payloads into Beckn RET10 handicraft specifications."""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.artisan import Artisan
from app.models.product import Product
from app.utils.logger import logger


def build_statutory_tags(product: Product, artisan: Artisan) -> list[dict[str, Any]]:
    """Build mandatory Beckn statutory and origin tags for handicraft listings."""
    tags = [
        {
            "code": "origin",
            "list": [
                {"code": "country", "value": "IND"}
            ]
        },
        {
            "code": "artisan_details",
            "list": [
                {"code": "name", "value": artisan.name or "Verified Artisan"},
                {"code": "lineage", "value": artisan.craft_lineage or "Traditional Artisan"},
                {"code": "craft_type", "value": product.craft_type}
            ]
        }
    ]

    gi_name = getattr(product, "gi_tag_name", None) or getattr(product, "gi_tag", None)
    if gi_name:
        is_cert = getattr(product, "is_gi_certified", True)
        tags.append({
            "code": "gi_certification",
            "list": [
                {"code": "tag_name", "value": gi_name},
                {"code": "certified", "value": "true" if is_cert else "false"}
            ]
        })

    if product.material:
        tags.append({
            "code": "attribute",
            "list": [
                {"code": "material", "value": product.material}
            ]
        })

    return tags


def build_ondc_item(product: Product, artisan: Artisan) -> dict[str, Any]:
    """Convert a product entity into a Beckn RET10 item object."""
    price_val = float(product.final_price or product.suggested_price or 0.0)
    price_str = f"{price_val:.2f}"
    images = list(product.image_urls or [])

    return {
        "id": str(product.id),
        "descriptor": {
            "name": product.title_en or getattr(product, "title_native", None) or "Handicraft Product",
            "code": f"KALA-{str(product.id)[:8].upper()}",
            "symbol": images[0] if images else "",
            "short_desc": product.description_en or getattr(product, "description_native", "") or "",
            "long_desc": getattr(product, "artisan_story", None) or product.description_en or "",
            "images": images
        },
        "price": {
            "currency": getattr(product, "currency", "INR") or "INR",
            "value": price_str,
            "maximum_value": price_str
        },
        "category_id": (product.craft_type or "handicraft").lower().replace(" ", "_"),
        "fulfillment_id": "F1",
        "location_id": "L1",
        "@ondc/org/returnable": False,
        "@ondc/org/cancellable": True,
        "@ondc/org/available_on_cod": True,
        "@ondc/org/time_to_ship": "P3D",
        "tags": build_statutory_tags(product, artisan)
    }


def build_ondc_catalog(artisan: Artisan, products: list[Product]) -> dict[str, Any]:
    """Construct full Beckn Provider Catalog payload for an artisan."""
    items = [build_ondc_item(p, artisan) for p in products if p.is_active]
    phone_digits = artisan.phone[-4:] if artisan.phone else "0000"

    return {
        "bpp/descriptor": {
            "name": "Kalakriti Artisan Network",
            "symbol": "https://kalakriti.app/logo.png",
            "short_desc": "DPI Gateway for Indian Artisans"
        },
        "bpp/providers": [
            {
                "id": str(artisan.id),
                "descriptor": {
                    "name": artisan.name or f"Artisan {phone_digits}",
                    "short_desc": artisan.craft_lineage or "Traditional Handicraft Artisan",
                    "images": []
                },
                "locations": [
                    {
                        "id": "L1",
                        "gps": "28.6139,77.2090",
                        "address": {
                            "locality": artisan.state or "India",
                            "country": "IND"
                        }
                    }
                ],
                "items": items
            }
        ]
    }


async def publish_item_to_ondc(product: Product, artisan: Artisan) -> dict[str, Any]:
    """
    Publish/sync a product item to ONDC seller network.
    Mocks Beckn Gateway on_search / catalog sync transaction.
    """
    item_payload = build_ondc_item(product, artisan)
    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Published product {} to ONDC (TxID: {}, Price: INR {})",
        product.id,
        transaction_id,
        item_payload["price"]["value"]
    )

    return {
        "context": {
            "domain": "nic2004:52110",
            "country": "IND",
            "city": "std:080",
            "action": "on_search",
            "core_version": "1.2.0",
            "bap_id": "mock.bap.ondc.org",
            "bpp_id": "api.kalakriti.app",
            "transaction_id": transaction_id,
            "message_id": message_id,
            "timestamp": timestamp
        },
        "message": {
            "ack": {
                "status": "ACK"
            }
        },
        "published_item": item_payload
    }