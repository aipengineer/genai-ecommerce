# genai-ecommerce/src/genai_ecommerce_core/models.py
"""Core data models for the GenAI E-commerce project."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Price(BaseModel):
    """Price information for a product."""

    amount: float
    currency: str
    original_amount: float | None = None
    discount_percentage: float | None = None


class Attribute(BaseModel):
    """Product attribute."""

    key: str
    value: str
    group: str | None = None


class Category(BaseModel):
    """Product category."""

    id: int
    name: str
    parent_id: int | None = None
    level: int = Field(default=0)
    path: str


class Image(BaseModel):
    """Product image."""

    url: str
    type: str = Field(default="standard")
    local_path: str | None = None


class Product(BaseModel):
    """Main product model."""

    id: int
    name: str
    description: str | None = None
    brand: str | None = None
    price: Price
    images: list[Image] = Field(default_factory=list)
    categories: list[Category] = Field(default_factory=list)
    attributes: list[Attribute] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    raw_data: dict[str, Any] = Field(default_factory=dict)


class ProductResponse(BaseModel):
    """API response for product listing."""

    entities: list[Product]
    pagination: dict[str, Any]
