# src/genai_ecommerce_web/dependencies.py
from collections.abc import Generator

from sqlalchemy.orm import Session

from genai_ecommerce_core.database import init_db


async def get_db() -> Generator[Session, None, None]:
    db = await init_db("sqlite:///ecommerce.db")
    try:
        yield db
    finally:
        db.close()
