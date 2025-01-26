# src/genai_ecommerce_web/dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession

from genai_ecommerce_core.database import init_db


async def get_db() -> AsyncSession:
    """Yield an asynchronous database session."""
    session_maker = await init_db()
    async with session_maker() as session:
        yield session
