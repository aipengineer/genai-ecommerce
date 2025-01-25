# src/genai_ecommerce_web/routers/api.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from genai_ecommerce_core.models import Product
from ..dependencies import get_db

router = APIRouter()

@router.get("/products", response_model=List[Product])
async def get_products(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    try:
        products = await db.query(Product).offset(skip).limit(limit).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    try:
        product = await db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))