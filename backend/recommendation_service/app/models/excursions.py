from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Float, Boolean, DateTime, Text, Index, func
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Excursion(Base):
    """Excursion model for recommendation system"""

    __tablename__ = "excursions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    excursion_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100))
    location_type: Mapped[str] = mapped_column(String(20))
    price: Mapped[float] = mapped_column(Float)
    duration: Mapped[int] = mapped_column(Integer)
    average_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    popularity: Mapped[int] = mapped_column(Integer, default=0)

    text_for_embedding: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(768), nullable=True)
    ials_factors: Mapped[Optional[list[float]]] = mapped_column(Vector(128), nullable=True)

    has_embedding: Mapped[bool] = mapped_column(Boolean, default=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_excursion_id", "excursion_id"),
        Index("idx_category", "category"),
        Index("idx_location_type", "location_type"),
        Index("idx_popularity", "popularity"),
    )
