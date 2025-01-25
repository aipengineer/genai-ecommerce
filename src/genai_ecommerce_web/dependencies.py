# src/genai_ecommerce_web/dependencies.py
from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from genai_ecommerce_core.database import init_db


async def get_db() -> Generator[Session, None, None]:
    db = await init_db("sqlite:///ecommerce.db")
    try:
        yield db
    finally:
        db.close()
