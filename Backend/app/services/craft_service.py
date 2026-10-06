"""Craft & GI Service — Keyword-based craft classification and GI tag matching."""

import re
from typing import Optional
from pydantic import BaseModel, Field


class CraftGIMatch(BaseModel):
    craft_type: str = Field(..., description="Matched primary craft classification")
    gi_tag_name: Optional[str] = Field(None, description="Official GI tag name if applicable")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Match confidence score")
    state_origin: Optional[str] = Field(None, description="Origin Indian state for GI tag")


# Embedded GI & Craft Keyword Mapping for primary Indian artisanal clusters
CRAFT_GI_DATABASE = [
    {
        "keywords": ["blue pottery", "jaipur pottery", "jaipur blue"],
        "craft_type": "pottery",
        "gi_tag_name": "Blue Pottery of Jaipur",
        "state_origin": "Rajasthan",
    },
    {
        "keywords": ["khurja", "khurja pottery", "ceramic mug", "mitti bartan"],
        "craft_type": "pottery",
        "gi_tag_name": "Khurja Pottery",
        "state_origin": "Uttar Pradesh",
    },
    {
        "keywords": ["madhubani", "mithila", "madhubani painting"],
        "craft_type": "painting",
        "gi_tag_name": "Madhubani Paintings",
        "state_origin": "Bihar",
    },
    {
        "keywords": ["pashmina", "cashmere", "kashmir shawl"],
        "craft_type": "handloom",
        "gi_tag_name": "Kashmir Pashmina",
        "state_origin": "Jammu and Kashmir",
    },
    {
        "keywords": ["channapatna", "lacquer toy", "wooden toy"],
        "craft_type": "woodwork",
        "gi_tag_name": "Channapatna Toys and Dolls",
        "state_origin": "Karnataka",
    },
    {
        "keywords": ["kantha", "kantha stitch", "bengal embroidery"],
        "craft_type": "embroidery",
        "gi_tag_name": "Nakshi Kantha",
        "state_origin": "West Bengal",
    },
    {
        "keywords": ["tanjore", "thanjavur painting", "gold leaf painting"],
        "craft_type": "painting",
        "gi_tag_name": "Thanjavur Paintings",
        "state_origin": "Tamil Nadu",
    },
    {
        "keywords": ["bidri", "bidriware", "silver inlay"],
        "craft_type": "metalwork",
        "gi_tag_name": "Bidriware",
        "state_origin": "Karnataka",
    },
    {
        "keywords": ["banarasi", "banarasi saree", "varanasi silk"],
        "craft_type": "handloom",
        "gi_tag_name": "Banaras Brocades and Sarees",
        "state_origin": "Uttar Pradesh",
    },
    {
        "keywords": ["terracotta", "clay diya", "mitti diya", "terracotta craft"],
        "craft_type": "pottery",
        "gi_tag_name": "Gorakhpur Terracotta",
        "state_origin": "Uttar Pradesh",
    },
]

# General Craft Category Keywords (Fallback when no specific GI tag is detected)
GENERIC_CRAFT_KEYWORDS = {
    "pottery": ["diya", "pot", "mitti", "clay", "matka", "kullhad", "ceramic"],
    "handloom": ["saree", "shawl", "cloth", "fabric", "weaving", "khadi", "dupatta", "thread"],
    "woodwork": ["wood", "wooden", "carving", "furniture", "timber", "toy"],
    "metalwork": ["brass", "copper", "iron", "bronze", "metal", "utensil"],
    "jewelry": ["necklace", "earring", "bangle", "silver", "bead", "ornament"],
    "painting": ["painting", "picture", "art", "canvas", "color", "frame"],
    "embroidery": ["threadwork", "stitch", "embroidery", "needlework", "zari"],
    "basketry": ["bamboo", "cane", "basket", "jute", "rope"],
}


def match_craft_and_gi(
    transcript: str,
    artisan_state: Optional[str] = None,
) -> Optional[CraftGIMatch]:
    """
    Scans input transcript for craft types and GI certification tags.
    Returns CraftGIMatch object if a match is identified, otherwise None.
    """
    if not transcript or not transcript.strip():
        return None

    clean_text = transcript.lower()

    # 1. Exact or Fuzzy GI Tag Keyword Search
    for entry in CRAFT_GI_DATABASE:
        for kw in entry["keywords"]:
            if re.search(rf"\b{re.escape(kw)}\b", clean_text):
                # Extra confidence if state matches artisan location
                conf = 0.95 if (artisan_state and artisan_state.lower() in entry["state_origin"].lower()) else 0.85
                return CraftGIMatch(
                    craft_type=entry["craft_type"],
                    gi_tag_name=entry["gi_tag_name"],
                    confidence=conf,
                    state_origin=entry["state_origin"],
                )

    # 2. Generic Craft Keyword Search Fallback
    for category, keywords in GENERIC_CRAFT_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", clean_text):
                return CraftGIMatch(
                    craft_type=category,
                    gi_tag_name=None,
                    confidence=0.65,
                    state_origin=artisan_state,
                )

    return None