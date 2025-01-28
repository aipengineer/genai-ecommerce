# src/genai_ecommerce_core/raw_models.py

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Boolean,
    Column,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


# Shared Enums
class ProcessingStatus(str, Enum):
    """Status of product processing."""

    PENDING = "pending"
    NORMALIZED = "normalized"
    EMBEDDED = "embedded"
    ERROR = "error"


class IngestionStatus(str, Enum):
    """Status of ingestion process."""

    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class BatchType(str, Enum):
    """Type of batch processing."""

    NORMALIZATION = "normalization"
    EMBEDDING = "embedding"


class BatchStatus(str, Enum):
    """Status of batch processing."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


# SQLAlchemy Models
class RawProduct(Base):
    """Raw product data storage."""

    __tablename__ = "raw_products"

    id = Column(Integer, primary_key=True)
    raw_data = Column(JSON, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP"
    )
    last_seen_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP"
    )
    is_deleted = Column(Boolean, nullable=False, default=False)
    processing_status = Column(
        SQLAlchemyEnum(ProcessingStatus),
        nullable=False,
        default=ProcessingStatus.PENDING,
    )
    processing_error = Column(Text)
    processed_at = Column(TIMESTAMP(timezone=True))
    embedding_vector = Column(LargeBinary)

    # Create indexes
    __table_args__ = (
        Index("idx_updated_at", "updated_at"),
        Index("idx_processing_status", "processing_status"),
        Index("idx_last_seen", "last_seen_at"),
    )


class IngestionMetadata(Base):
    """Track ingestion progress."""

    __tablename__ = "ingestion_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP"
    )
    completed_at = Column(TIMESTAMP(timezone=True))
    total_pages = Column(Integer, nullable=False)
    current_page = Column(Integer, nullable=False)
    products_per_page = Column(Integer, nullable=False)
    total_products = Column(Integer, nullable=False)
    status = Column(
        SQLAlchemyEnum(IngestionStatus), nullable=False, default=IngestionStatus.RUNNING
    )
    error_message = Column(Text)


class ProcessingBatch(Base):
    """Track batch processing progress."""

    __tablename__ = "processing_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP"
    )
    completed_at = Column(TIMESTAMP(timezone=True))
    batch_type = Column(SQLAlchemyEnum(BatchType), nullable=False)
    status = Column(
        SQLAlchemyEnum(BatchStatus), nullable=False, default=BatchStatus.PENDING
    )
    products_processed = Column(Integer, default=0)
    total_products = Column(Integer, nullable=False)
    error_message = Column(Text)


# Pydantic Models
class RawProductCreate(BaseModel):
    """Schema for creating a raw product."""

    id: int
    raw_data: dict[str, Any]
    updated_at: datetime
    is_deleted: bool = False
    processing_status: ProcessingStatus = ProcessingStatus.PENDING


class RawProductUpdate(BaseModel):
    """Schema for updating a raw product."""

    raw_data: Optional[dict[str, Any]] = None
    updated_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None
    processing_status: Optional[ProcessingStatus] = None
    processing_error: Optional[str] = None
    processed_at: Optional[datetime] = None
    embedding_vector: Optional[bytes] = None


class RawProductResponse(BaseModel):
    """Schema for raw product responses."""

    id: int
    updated_at: datetime
    created_at: datetime
    last_seen_at: datetime
    is_deleted: bool
    processing_status: ProcessingStatus
    processing_error: Optional[str] = None
    processed_at: Optional[datetime] = None
    has_embedding: bool = Field(default=False)

    class Config:
        from_attributes = True


class IngestionMetadataCreate(BaseModel):
    """Schema for creating ingestion metadata."""

    total_pages: int
    current_page: int
    products_per_page: int
    total_products: int
    status: IngestionStatus = IngestionStatus.RUNNING


class IngestionMetadataUpdate(BaseModel):
    """Schema for updating ingestion metadata."""

    current_page: Optional[int] = None
    completed_at: Optional[datetime] = None
    status: Optional[IngestionStatus] = None
    error_message: Optional[str] = None


class ProcessingBatchCreate(BaseModel):
    """Schema for creating a processing batch."""

    batch_type: BatchType
    total_products: int
    status: BatchStatus = BatchStatus.PENDING


class ProcessingBatchUpdate(BaseModel):
    """Schema for updating a processing batch."""

    completed_at: Optional[datetime] = None
    status: Optional[BatchStatus] = None
    products_processed: Optional[int] = None
    error_message: Optional[str] = None


# Helper functions
async def upsert_raw_product(
    db_session, product_data: RawProductCreate
) -> RawProduct:
    """
    Insert or update a raw product in the database.
    
    Args:
        db_session: The database session
        product_data: The product data to upsert
        
    Returns:
        The upserted RawProduct instance
    """
    # Check if product exists
    stmt = select(RawProduct).where(RawProduct.id == product_data.id)
    result = await db_session.execute(stmt)
    existing_product = result.scalar_one_or_none()

    if existing_product:
        # Update existing product
        update_data = {
            "raw_data": product_data.raw_data,
            "updated_at": product_data.updated_at,
            "last_seen_at": datetime.utcnow(),
            "is_deleted": product_data.is_deleted,
        }
        await db_session.execute(
            update(RawProduct)
            .where(RawProduct.id == product_data.id)
            .values(**update_data)
        )
        await db_session.refresh(existing_product)
        return existing_product
    else:
        # Create new product
        new_product = RawProduct(**product_data.model_dump())
        db_session.add(new_product)
        await db_session.flush()
        return new_product