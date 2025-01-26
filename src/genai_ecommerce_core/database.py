# genai-ecommerce/src/genai_ecommerce_core/database.py
"""Database models and utilities for the GenAI E-commerce project."""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

engine = create_async_engine("sqlite+aiosqlite:///ecommerce.db", echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def bulk_insert_products(db: AsyncSession, products: list[dict]) -> None:
    """
    Bulk insert products into the database with data preprocessing.

    Args:
        db: The database session.
        products: A list of dictionaries containing product data.
    """
    from .database import (
        DBAttribute,
        DBCategory,
        DBImage,
        DBPrice,
        DBProduct,
        DBProductCategory,
    )

    def preprocess_product_data(product: dict) -> dict:
        """Preprocess a single product dictionary."""
        product.setdefault("name", "Unknown")
        product.setdefault("price", {"amount": 0.0, "currency": "USD"})
        product.setdefault("images", [])
        product.setdefault("categories", [])
        product.setdefault("attributes", [])
        product.setdefault("created_at", datetime.utcnow())
        product.setdefault("updated_at", datetime.utcnow())

        # Normalize images
        product["images"] = [
            {"url": img.get("url", ""), "type": img.get("type", "standard")}
            for img in product["images"]
            if "url" in img
        ]

        # Normalize categories
        product["categories"] = [
            {
                "id": cat.get("categoryId", 0),
                "name": cat.get("name", "Unknown"),
                "parent_id": cat.get("parentId"),
                "level": cat.get("level", 0),
                "path": cat.get("path", ""),
            }
            for cat in product["categories"]
        ]

        # Normalize attributes
        product["attributes"] = [
            {
                "key": attr.get("key", ""),
                "value": attr.get("value", ""),
                "group": attr.get("group"),
            }
            for attr in product["attributes"]
        ]

        return product

    try:
        for raw_product in products:
            product = preprocess_product_data(raw_product)

            # Create a new product record
            db_product = DBProduct(
                id=product["id"],
                name=product["name"],
                description=product.get("description"),
                brand=product.get("brand"),
                raw_data=product,  # Store the raw product data for reference
            )

            # Add related price records
            db_price = DBPrice(
                product_id=product["id"],
                amount=product["price"]["amount"],
                currency=product["price"]["currency"],
                original_amount=product["price"].get("original_amount"),
                discount_percentage=product["price"].get("discount_percentage"),
            )
            db_product.prices.append(db_price)

            # Add related category records
            for category in product["categories"]:
                db_category = DBCategory(
                    id=category["id"],
                    name=category["name"],
                    parent_id=category.get("parent_id"),
                    level=category["level"],
                    path=category["path"],
                )
                db_product.categories.append(DBProductCategory(category=db_category))

            # Add related image records
            for image in product["images"]:
                db_image = DBImage(
                    product_id=product["id"],
                    url=image["url"],
                    type=image["type"],
                    local_path=image.get("local_path"),
                )
                db_product.images.append(db_image)

            # Add related attribute records
            for attr in product["attributes"]:
                db_attribute = DBAttribute(
                    product_id=product["id"],
                    key=attr["key"],
                    value=attr["value"],
                    group=attr.get("group"),
                )
                db_product.attributes.append(db_attribute)

            # Add the product to the session
            db.add(db_product)

        # Commit the session to save all changes
        await db.commit()
        print(f"Inserted {len(products)} products into the database.")
    except Exception as e:
        await db.rollback()  # Rollback in case of error
        print(f"Error during bulk insert: {e}")
        raise


async def init_db(db_url: str = "sqlite+aiosqlite:///ecommerce.db") -> sessionmaker:
    """
    Create all tables and return the session maker.

    Args:
        db_url: The database connection URL.

    Returns:
        A sessionmaker bound to the database engine.
    """
    engine = create_async_engine(db_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
    )


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
