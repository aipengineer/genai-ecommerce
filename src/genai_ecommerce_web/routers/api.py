# src/genai_ecommerce_web/routers/api.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from genai_ecommerce_core.models import Product

from ..dependencies import get_db

router = APIRouter()

# Define the dependency at the module level
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
        result = await db.execute(select(Product).offset(skip).limit(limit))
        products = result.scalars().all()
        return products
    except Exception as e:
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
        result = await db.execute(select(Product).filter(Product.id == product_id))
        product = result.scalars().first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
