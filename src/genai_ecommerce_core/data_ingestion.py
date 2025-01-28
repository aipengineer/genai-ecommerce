# src/genai_ecommerce_core/data_ingestion.py
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from genai_ecommerce_core.client import AboutYouClient
from genai_ecommerce_core.database import init_db
from genai_ecommerce_core.models import PaginationResponse
from genai_ecommerce_core.raw_models import (
    IngestionMetadata,
    IngestionStatus,
    ProcessingStatus,
    RawProduct,
    RawProductCreate,
)


@asynccontextmanager
async def get_db() -> AsyncSession:
    """Async context manager to initialize and close the database session."""
    db_url = "sqlite+aiosqlite:///ecommerce.db"
    session_maker = await init_db(db_url)
    async with session_maker() as db:
        try:
            yield db
        finally:
            await db.close()


async def create_ingestion_session(
    db: AsyncSession, pagination_data: PaginationResponse
) -> IngestionMetadata:
    """Create a new ingestion session to track progress."""
    metadata_dict = {
        "total_pages": pagination_data.total // pagination_data.per_page + 1,
        "current_page": pagination_data.page,
        "products_per_page": pagination_data.per_page,
        "total_products": pagination_data.total,
        "status": IngestionStatus.RUNNING,
        "started_at": datetime.now(timezone.utc),  # Fix the deprecation warning too
    }

    # Create SQLAlchemy model instance directly
    ingestion_session = IngestionMetadata(**metadata_dict)
    db.add(ingestion_session)
    await db.commit()  # Commit the session first

    # Get a new session for further operations
    await db.refresh(ingestion_session)
    return ingestion_session


# src/genai_ecommerce_core/data_ingestion.py


async def store_raw_product(
    db: AsyncSession, product: dict[str, Any], ingestion_id: int
) -> RawProduct | None:
    """Store a raw product in the database."""
    try:
        now = datetime.now(timezone.utc)
        product_data = RawProductCreate(
            id=product["id"],
            raw_data=product,
            updated_at=datetime.fromisoformat(product["updatedAt"]),
            is_deleted=not product.get("isActive", True),
        )

        stmt = select(RawProduct).where(RawProduct.id == product_data.id)
        result = await db.execute(stmt)
        existing_product = result.scalar_one_or_none()

        if existing_product:
            # Update existing product
            stmt = (
                update(RawProduct)
                .where(RawProduct.id == product_data.id)
                .values(
                    raw_data=product_data.raw_data,
                    updated_at=product_data.updated_at,
                    last_seen_at=now,
                    is_deleted=product_data.is_deleted,
                )
            )
            await db.execute(stmt)
            return existing_product

        # Create new product
        new_product = RawProduct(
            **product_data.model_dump(),
            created_at=now,
            last_seen_at=now,
        )
        db.add(new_product)
        return new_product

    except Exception as e:
        print(f"Error storing raw product {product.get('id', 'unknown')}: {e}")
        return None


async def ingest_data() -> None:
    """Fetch data from AboutYou API and store raw data in the database."""
    async with get_db() as db:
        client = AboutYouClient()
        ingestion_id = None

        try:
            # Start ingestion
            initial_response = await client.get_products(page=1)

            # Create metadata without session
            metadata_dict = {
                "total_pages": initial_response.pagination.total
                // initial_response.pagination.per_page
                + 1,
                "current_page": initial_response.pagination.page,
                "products_per_page": initial_response.pagination.per_page,
                "total_products": initial_response.pagination.total,
                "status": IngestionStatus.RUNNING,
                "started_at": datetime.now(timezone.utc),
            }

            # Insert ingestion metadata
            stmt = (
                insert(IngestionMetadata)
                .values(**metadata_dict)
                .returning(IngestionMetadata.id)
            )
            result = await db.execute(stmt)
            ingestion_id = result.scalar_one()
            await db.commit()

            current_page = 1
            total_pages = metadata_dict["total_pages"]

            while current_page <= total_pages:
                print(f"Fetching page {current_page}/{total_pages}...")

                if current_page > 1:
                    response = await client.get_products(page=current_page)
                else:
                    response = initial_response

                # Exit if no more products
                if not response.entities:
                    print("No more products to process. Exiting.")
                    break

                # Process each product in the batch
                for raw_product in response.entities:
                    now = datetime.now(timezone.utc)

                    try:
                        stmt = select(RawProduct.id).where(
                            RawProduct.id == raw_product["id"]
                        )
                        result = await db.execute(stmt)
                        existing_id = result.scalar_one_or_none()

                        if existing_id:
                            # Update
                            stmt = (
                                update(RawProduct)
                                .where(RawProduct.id == raw_product["id"])
                                .values(
                                    raw_data=raw_product,
                                    updated_at=datetime.fromisoformat(
                                        raw_product["updatedAt"]
                                    ),
                                    last_seen_at=now,
                                    is_deleted=not raw_product.get("isActive", True),
                                )
                            )
                            await db.execute(stmt)
                        else:
                            # Insert
                            stmt = insert(RawProduct).values(
                                id=raw_product["id"],
                                raw_data=raw_product,
                                updated_at=datetime.fromisoformat(
                                    raw_product["updatedAt"]
                                ),
                                created_at=now,
                                last_seen_at=now,
                                is_deleted=not raw_product.get("isActive", True),
                                processing_status=ProcessingStatus.PENDING,
                            )
                            await db.execute(stmt)

                        print(f"Stored/updated raw product {raw_product['id']}")

                    except Exception as e:
                        print(
                            f"Error processing product {raw_product.get('id', 'unknown')}: {e}"
                        )
                        continue

                # Update progress
                stmt = (
                    update(IngestionMetadata)
                    .where(IngestionMetadata.id == ingestion_id)
                    .values(
                        current_page=current_page,
                        completed_at=datetime.now(timezone.utc)
                        if current_page == total_pages
                        else None,
                        status=IngestionStatus.COMPLETED
                        if current_page == total_pages
                        else IngestionStatus.RUNNING,
                    )
                )
                await db.execute(stmt)
                await db.commit()

                current_page += 1

        except Exception as e:
            print(f"Error during ingestion: {e}")
            if ingestion_id:
                stmt = (
                    update(IngestionMetadata)
                    .where(IngestionMetadata.id == ingestion_id)
                    .values(
                        status=IngestionStatus.ERROR,
                        error_message=str(e),
                    )
                )
                await db.execute(stmt)
                await db.commit()
        finally:
            await client.close()


async def update_ingestion_progress(
    db: AsyncSession,
    session: IngestionMetadata,
    current_page: int,
    is_complete: bool,
) -> None:
    """Update ingestion session progress."""
    async with db.begin():
        stmt = (
            update(IngestionMetadata)
            .where(IngestionMetadata.id == session.id)
            .values(
                current_page=current_page,
                completed_at=datetime.now(timezone.utc) if is_complete else None,
                status=IngestionStatus.COMPLETED
                if is_complete
                else IngestionStatus.RUNNING,
            )
        )
        await db.execute(stmt)


async def update_ingestion_error(
    db: AsyncSession,
    session: IngestionMetadata,
    error: str,
) -> None:
    """Update ingestion session with error status."""
    async with db.begin():
        stmt = (
            update(IngestionMetadata)
            .where(IngestionMetadata.id == session.id)
            .values(
                status=IngestionStatus.ERROR,
                error_message=error,
            )
        )
        await db.execute(stmt)


async def normalize_raw_data(batch_size: int = 100) -> None:
    """
    Process raw data and populate normalized schema.
    This would be run as a separate process after ingestion.
    """
    async with get_db() as db:
        while True:
            # Get batch of unprocessed raw products
            stmt = (
                select(RawProduct)
                .where(RawProduct.processing_status == ProcessingStatus.PENDING)
                .limit(batch_size)
            )
            result = await db.execute(stmt)
            raw_products = result.scalars().all()

            if not raw_products:
                print("No more products to normalize")
                break

            for raw_product in raw_products:
                try:
                    # Here we'll call the original normalization logic
                    # but using raw_product.raw_data as source
                    await normalize_product(db, raw_product)

                    # Update processing status
                    raw_product.processing_status = ProcessingStatus.NORMALIZED
                    raw_product.processed_at = datetime.utcnow()

                except Exception as e:
                    raw_product.processing_status = ProcessingStatus.ERROR
                    raw_product.processing_error = str(e)
                    print(f"Error normalizing product {raw_product.id}: {e}")

            await db.commit()


async def normalize_product(db: AsyncSession, raw_product: RawProduct) -> None:
    """
    Normalize a single product into the existing schema.
    This would use the existing normalization logic but source from raw_data.
    """
    # Here we'll implement the normalization logic
    # This would use the existing models.py structures
    # but source from raw_product.raw_data instead of API response
    pass


if __name__ == "__main__":
    # Run raw ingestion
    asyncio.run(ingest_data())

    # Optionally, run normalization as a separate step
    # asyncio.run(normalize_raw_data())
