# genai-ecommerce/src/genai_ecommerce_core/database.py
"""Database models and utilities for the GenAI E-commerce project."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DBProduct(Base):
    """Product table."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    raw_data = Column(JSON)

    # Relationships
    prices = relationship("DBPrice", back_populates="product")
    images = relationship("DBImage", back_populates="product")
    attributes = relationship("DBAttribute", back_populates="product")
    categories = relationship("DBProductCategory", back_populates="product")


class DBPrice(Base):
    """Price history table."""

    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    original_amount = Column(Float, nullable=True)
    discount_percentage = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("DBProduct", back_populates="prices")


class DBCategory(Base):
    """Category hierarchy table."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    level = Column(Integer, default=0)
    path = Column(String, nullable=False)

    # Self-referential relationship
    children = relationship("DBCategory")


class DBProductCategory(Base):
    """Product-Category association table."""

    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    # Relationships
    product = relationship("DBProduct", back_populates="categories")
    category = relationship("DBCategory")


class DBAttribute(Base):
    """Product attributes table."""

    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    group = Column(String, nullable=True)

    # Relationships
    product = relationship("DBProduct", back_populates="attributes")


class DBImage(Base):
    """Product images table."""

    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    url = Column(String, nullable=False)
    type = Column(String, default="standard")
    local_path = Column(String, nullable=True)

    # Relationships
    product = relationship("DBProduct", back_populates="images")


async def init_db(database_url: str) -> None:
    """Initialize database schema."""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
