# src/genai_ecommerce_web/routers/api.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from genai_ecommerce_core.database import DBProduct  # Use the SQLAlchemy model
from genai_ecommerce_core.models import Product  # Use Pydantic model for validation

from ..dependencies import get_db

router = APIRouter()

# Dependency for the database session
get_db_dependency = Depends(get_db)


@router.get("/products", response_model=list[Product])
async def get_products(
    skip: int = 0, limit: int = 20, db: AsyncSession = get_db_dependency
) -> list[Product]:
    """
    Fetch a list of products with pagination.

    Args:
        skip: Number of products to skip.
        limit: Number of products to return.
        db: Database session.

    Returns:
        A list of products.
    """
    try:
        result = await db.execute(select(DBProduct).offset(skip).limit(limit))
        db_products = result.scalars().all()

        # Convert database models to Pydantic models
        products = [
            Product(
                id=prod.id,
                name=prod.name,
                description=prod.description,
                brand=prod.brand,
                created_at=prod.created_at,
                updated_at=prod.updated_at,
                raw_data=prod.raw_data,
                price=None,  # Add price conversion logic if needed
                images=[],  # Add images conversion logic if needed
                categories=[],  # Add categories conversion logic if needed
                attributes=[],  # Add attributes conversion logic if needed
            )
            for prod in db_products
        ]
        print(f"Fetched {len(products)} products from the database.")

        return products
    except Exception as e:
        print(f"Error in get_products: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int, db: AsyncSession = get_db_dependency) -> Product:
    """
    Fetch a single product by its ID.

    Args:
        product_id: The ID of the product to fetch.
        db: Database session.

    Returns:
        The product object.

    Raises:
        HTTPException: If the product is not found or an error occurs.
    """
    try:
        result = await db.execute(select(DBProduct).where(DBProduct.id == product_id))
        db_product = result.scalars().first()

        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Convert database model to Pydantic model
        product = Product(
            id=db_product.id,
            name=db_product.name,
            description=db_product.description,
            brand=db_product.brand,
            created_at=db_product.created_at,
            updated_at=db_product.updated_at,
            raw_data=db_product.raw_data,
            price=None,  # Add price conversion logic if needed
            images=[],  # Add images conversion logic if needed
            categories=[],  # Add categories conversion logic if needed
            attributes=[],  # Add attributes conversion logic if needed
        )

        return product
    except Exception as e:
        print(f"Error in get_product: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
