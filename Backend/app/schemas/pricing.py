# Kalakriti/Backend/app/schemas/pricing.py

from typing import Optional
from pydantic import BaseModel, Field, model_validator


class PricingRequest(BaseModel):
    """Input features required by the Gradient Boosting pricing model."""

    craft_type: str = Field(
        ..., min_length=2, max_length=100, examples=["Ikat Weaving"]
    )
    material: str = Field(
        ..., min_length=2, max_length=100, examples=["Mulberry Silk"]
    )
    length_cm: Optional[float] = Field(default=None, gt=0, examples=[550.0])
    width_cm: Optional[float] = Field(default=None, gt=0, examples=[115.0])
    height_cm: Optional[float] = Field(default=None, gt=0, examples=[10.0])
    weight_grams: Optional[int] = Field(default=None, gt=0, examples=[600])
    weight_g: Optional[float] = Field(default=None, gt=0, examples=[600.0])
    artisan_expected_price_inr: Optional[float] = Field(
        default=None, gt=0, examples=[4000.0]
    )

    @model_validator(mode="after")
    def populate_weights(self) -> "PricingRequest":
        if self.weight_g is None and self.weight_grams is not None:
            self.weight_g = float(self.weight_grams)
        elif self.weight_grams is None and self.weight_g is not None:
            self.weight_grams = int(self.weight_g)
        return self


class PricingResponse(BaseModel):
    """Suggested price and bounds calculated by scikit-learn regressor."""

    suggested_price: float = Field(
        ..., description="Point prediction in INR"
    )
    price_min: float = Field(
        ..., description="Recommended minimum price (-15% to -25% of suggested)"
    )
    price_max: float = Field(
        ..., description="Recommended maximum price (+20% to +35% of suggested)"
    )
    suggested_price_inr: Optional[float] = Field(
        default=None, description="Point prediction from Gradient Boosting Regressor"
    )
    price_min_inr: Optional[float] = Field(
        default=None, description="Recommended minimum price in INR"
    )
    price_max_inr: Optional[float] = Field(
        default=None, description="Recommended maximum price in INR"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Model confidence based on feature completeness"
    )
    pricing_factors: list[str] = Field(
        default_factory=list,
        description="Key factors influencing the price (e.g., 'Pure Silk Premium', 'Complex Ikat Weave')",
    )

    @model_validator(mode="after")
    def sync_inr_fields(self) -> "PricingResponse":
        if self.suggested_price_inr is None:
            self.suggested_price_inr = self.suggested_price
        if self.price_min_inr is None:
            self.price_min_inr = self.price_min
        if self.price_max_inr is None:
            self.price_max_inr = self.price_max
        return self