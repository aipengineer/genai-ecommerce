# genai-ecommerce/src/genai_ecommerce_core/models.py
"""Core data models for the GenAI E-commerce project."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Price(BaseModel):
    """Price information for a product."""

    amount: float
    currency: str
    original_amount: Optional[float] = None
    discount_percentage: Optional[float] = None


class Attribute(BaseModel):
    """Product attribute."""

    key: str
    value: str
    group: Optional[str] = None


class Category(BaseModel):
    """Product category."""

    id: int
    name: str
    parent_id: Optional[int] = None
    level: int = Field(default=0)
    path: str


class Image(BaseModel):
    """Product image."""

    url: str
    type: str = Field(default="standard")
    local_path: Optional[str] = None


class Product(BaseModel):
    """Main product model."""

    id: int
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    price: Price
    images: List[Image] = Field(default_factory=list)
    categories: List[Category] = Field(default_factory=list)
    attributes: List[Attribute] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class ProductResponse(BaseModel):
    """API response for product listing."""

    entities: List[Product]
    pagination: Dict[str, Any]
